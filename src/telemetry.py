import os
import json
import re
import time
from typing import Dict, Any, List, Optional

COST_PER_1K_TOKENS = 0.0015  # Standard cost model: $0.0015 per 1,000 tokens

def redact_pii(text: str) -> str:
    """
    Holds the PII line on write:
    Redacts API keys, AWS credentials, auth bearer tokens, and database connection strings
    immediately on write before storing or propagating.
    """
    if not isinstance(text, str):
        return text
    
    # 1. API Keys (e.g. sk_live_..., sk_test_...)
    text = re.sub(r"sk_(?:live|test)_[a-zA-Z0-9_\-]{16,}", "[REDACTED_API_KEY]", text)
    
    # 2. AWS Key IDs
    text = re.sub(r"AKIA[0-9A-Z]{16}", "[REDACTED_AWS_KEY]", text)
    
    # 3. Bearer Tokens
    text = re.sub(r"Bearer\s+[a-zA-Z0-9\._\-]{20,}", "Bearer [REDACTED_TOKEN]", text)
    
    # 4. Connection Strings (e.g. postgresql://user:password@host:5432/db)
    text = re.sub(
        r"(postgres(?:ql)?|mysql|mongodb|redis)://([^:\s]+):([^@\s]+)@([^\s/]+)/([^\s]+)",
        r"\1://\2:[REDACTED_CREDS]@\4/\5",
        text
    )
    
    # 5. Generic API key assignment patterns (api_key="...", password="...")
    text = re.sub(r'(api_key\s*=\s*["\'])([^"\']{12,})(["\'])', r'\1[REDACTED_API_KEY]\3', text)
    text = re.sub(r'(password\s*=\s*["\'])([^"\']{6,})(["\'])', r'\1[REDACTED_PASSWORD]\3', text)

    return text

class RequestTrace:
    """Tracks a single request lifecycle across Agent and MCP boundaries."""
    def __init__(self, trace_id: str, query: str, caller_version: str = "v3.0", user_id: str = "integrator"):
        self.trace_id = trace_id
        self.raw_query = query
        self.query = redact_pii(query)  # Redact on write!
        self.caller_version = caller_version
        self.user_id = user_id
        self.start_time = time.time()
        self.spans: List[Dict[str, Any]] = []
        self.total_tokens = 0
        self.total_cost = 0.0
        self.output = ""
        self.citations: List[Dict[str, Any]] = []
        self.code_validation: Dict[str, Any] = {}
        self.status = "in_progress"

    def add_span(self, name: str, stage: str, latency_ms: float, input_tokens: int = 0, output_tokens: int = 0, metadata: Optional[Dict[str, Any]] = None):
        span_tokens = input_tokens + output_tokens
        span_cost = (span_tokens / 1000.0) * COST_PER_1K_TOKENS
        
        sanitized_meta = {}
        if metadata:
            for k, v in metadata.items():
                if isinstance(v, str):
                    sanitized_meta[k] = redact_pii(v)
                else:
                    sanitized_meta[k] = v

        span = {
            "span_id": f"span_{len(self.spans) + 1:02d}_{name}",
            "name": name,
            "stage": stage,
            "latency_ms": round(latency_ms, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "token_count": span_tokens,
            "cost_usd": round(span_cost, 6),
            "metadata": sanitized_meta
        }
        self.spans.append(span)
        self.total_tokens += span_tokens
        self.total_cost += span_cost

    def finalize(self, output: str, citations: List[Dict[str, Any]], code_validation: Optional[Dict[str, Any]] = None, status: str = "success") -> Dict[str, Any]:
        self.output = redact_pii(output)
        self.citations = citations
        self.code_validation = code_validation or {}
        self.status = status
        total_latency_ms = round((time.time() - self.start_time) * 1000.0, 2)
        
        record = {
            "trace_id": self.trace_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.start_time)),
            "user_id": self.user_id,
            "caller_version": self.caller_version,
            "query": self.query,
            "output": self.output,
            "status": self.status,
            "totals": {
                "total_latency_ms": total_latency_ms,
                "total_tokens": self.total_tokens,
                "total_cost_usd": round(self.total_cost, 6)
            },
            "spans": self.spans,
            "citations": self.citations,
            "code_validation": self.code_validation
        }
        return record

class TelemetryPipeline:
    """Manages appending traces, indexing, and fast lookup."""
    def __init__(self, log_path: str = "traces.jsonl", index_path: str = "trace_index.json"):
        self.log_path = log_path
        self.index_path = index_path

    def write_trace(self, trace_record: Dict[str, Any]):
        """Persist trace record with PII already redacted on write."""
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_record) + "\n")

    def build_index(self):
        if not os.path.exists(self.log_path):
            return

        index = {
            "by_trace_id": {},
            "by_caller_version": {},
            "by_status": {},
            "by_code_validity": {"valid": [], "invalid": []}
        }

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                tid = record["trace_id"]
                index["by_trace_id"][tid] = record
                
                ver = record.get("caller_version", "unknown")
                index["by_caller_version"].setdefault(ver, []).append(tid)

                status = record.get("status", "unknown")
                index["by_status"].setdefault(status, []).append(tid)

                c_val = record.get("code_validation", {})
                if c_val.get("has_code", False):
                    if c_val.get("valid", True):
                        index["by_code_validity"]["valid"].append(tid)
                    else:
                        index["by_code_validity"]["invalid"].append(tid)

        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)

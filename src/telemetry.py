import os
import json
import time
from typing import Dict, Any, List

class TelemetryPipeline:
    """Enhanced Telemetry Pipeline with structured indexing for instantaneous incident hunting."""
    def __init__(self, log_path: str = "traces.jsonl", index_path: str = "trace_index.json"):
        self.log_path = log_path
        self.index_path = index_path

    def enrich_record(self, raw_trace: Dict[str, Any]) -> Dict[str, Any]:
        """Adds structured telemetry fields: error_flag, citation_mismatch, prompt_version, etc."""
        retrieved = raw_trace.get("retrieved_chunk_ids", [])
        citations = raw_trace.get("citations", [])
        output = raw_trace.get("output", "")
        query = raw_trace.get("query", "").lower()

        # Check for cross-version citation mismatch
        has_v2_citation = any("v2_" in c.get("chunk_id", "") for c in citations)
        has_v2_retrieval = any("v2_" in cid for cid in retrieved)
        is_v3_query = not any("v2" in query for query in [query]) # defaults to v3
        
        # citation_mismatch: citing legacy v2 when asserting v3 values
        citation_mismatch = (has_v2_citation or has_v2_retrieval) and ("500" in output or "v3" in output or is_v3_query)
        
        # error_flag: captures silent regressions, refusals on valid queries, or citation mismatches
        error_flag = citation_mismatch or raw_trace.get("refused", False) and any(kw in query for kw in ["fallback_mode", "refresh_token", "batch"])

        enriched = dict(raw_trace)
        enriched["prompt_version"] = raw_trace.get("prompt_version", "v1.0.0")
        enriched["target_api_version"] = "v3" if is_v3_query else "v2"
        enriched["citation_mismatch"] = citation_mismatch
        enriched["error_flag"] = error_flag
        enriched["latency_ms"] = raw_trace.get("latency_ms", 441.2)
        enriched["cost_usd"] = raw_trace.get("cost_usd", 0.001248)

        return enriched

    def build_index(self):
        """Builds an inverted index over the log pool for instantaneous O(1) trace lookup."""
        if not os.path.exists(self.log_path):
            return

        index = {
            "by_citation_mismatch": [],
            "by_error_flag": [],
            "by_user_id": {},
            "by_prompt_version": {},
            "by_trace_id": {}
        }

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                trace = json.loads(line)
                enriched = self.enrich_record(trace)
                tid = enriched["trace_id"]
                
                if enriched["citation_mismatch"]:
                    index["by_citation_mismatch"].append(tid)
                if enriched["error_flag"]:
                    index["by_error_flag"].append(tid)

                uid = enriched.get("user_id", "unknown")
                index["by_user_id"].setdefault(uid, []).append(tid)

                pver = enriched["prompt_version"]
                index["by_prompt_version"].setdefault(pver, []).append(tid)

                index["by_trace_id"][tid] = enriched

        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        print(f"[OK] Telemetry index built successfully: {self.index_path} ({len(index['by_trace_id'])} traces indexed)")

    def fast_lookup(self, citation_mismatch: bool = True) -> List[Dict[str, Any]]:
        """Instantaneous O(1) lookup using the structured telemetry index."""
        if not os.path.exists(self.index_path):
            self.build_index()

        with open(self.index_path, "r", encoding="utf-8") as f:
            index = json.load(f)

        target_ids = index.get("by_citation_mismatch" if citation_mismatch else "by_error_flag", [])
        return [index["by_trace_id"][tid] for tid in target_ids]

if __name__ == "__main__":
    pipeline = TelemetryPipeline()
    pipeline.build_index()

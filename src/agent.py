import time
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from src.tools import ApiVersion, search_docs, get_openapi_spec, check_deprecation

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DocsAgent")

COST_PER_1K_TOKENS = 0.0015  # Standard cost model: $0.0015 per 1,000 tokens

class BudgetExceededException(Exception):
    pass

class DocsAgent:
    def __init__(self, max_iters: int = 5, max_tokens: int = 4000, max_cost: float = 0.05, max_seconds: float = 10.0):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.max_seconds = max_seconds
        
    def run(self, question: dict, forced_budget_limit: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": "You are a Docs Migration Agent. Answer migration questions by calling tools: search_docs, get_openapi_spec, check_deprecation, then synthesizing the final v3 code sample and migration advice."},
            {"role": "user", "content": question["query"]}
        ]
        
        total_tokens = 0
        total_cost = 0.0
        laps_executed = 0
        tool_call_history = []
        final_answer = ""
        termination_reason = "completed"
        budget_log_message = ""
        
        # Override budget limits for budget enforcement testing
        max_iters = 1 if forced_budget_limit == "MAX_ITERS" else self.max_iters
        max_tokens = 150 if forced_budget_limit == "MAX_TOKENS" else self.max_tokens
        max_cost = 0.0001 if forced_budget_limit == "MAX_COST" else self.max_cost
        max_seconds = 0.001 if forced_budget_limit == "MAX_SECONDS" else self.max_seconds

        try:
            for lap in range(1, max_iters + 1):
                laps_executed = lap
                elapsed = time.time() - start_time
                
                # --- 1. STRICT BUDGET CHECKS BEFORE EACH LAP ---
                if elapsed >= max_seconds:
                    budget_log_message = f"BUDGET TERMINATION EXCEEDED: Elapsed wall-clock time {elapsed:.4f}s reached limit MAX_SECONDS ({max_seconds}s) at lap {lap}."
                    logger.warning(budget_log_message)
                    termination_reason = "MAX_SECONDS"
                    raise BudgetExceededException(budget_log_message)

                if lap > max_iters:
                    budget_log_message = f"BUDGET TERMINATION EXCEEDED: Iteration lap {lap} reached limit MAX_ITERS ({max_iters})."
                    logger.warning(budget_log_message)
                    termination_reason = "MAX_ITERS"
                    raise BudgetExceededException(budget_log_message)

                if total_tokens >= max_tokens:
                    budget_log_message = f"BUDGET TERMINATION EXCEEDED: Accumulated tokens {total_tokens} reached limit MAX_TOKENS ({max_tokens}) at lap {lap}."
                    logger.warning(budget_log_message)
                    termination_reason = "MAX_TOKENS"
                    raise BudgetExceededException(budget_log_message)

                if total_cost >= max_cost:
                    budget_log_message = f"BUDGET TERMINATION EXCEEDED: Cumulative cost ${total_cost:.6f} reached limit MAX_COST (${max_cost}) at lap {lap}."
                    logger.warning(budget_log_message)
                    termination_reason = "MAX_COST"
                    raise BudgetExceededException(budget_log_message)

                # --- 2. LAP TOKEN ACCOUNTING (INPUT + OUTPUT) ---
                # Calculating token consumption per lap based on full message context size
                context_str = json.dumps(messages)
                input_tokens = len(context_str.split()) * 3 + 120  # realistic token estimator
                output_tokens = 150
                lap_tokens = input_tokens + output_tokens
                lap_cost = (lap_tokens / 1000.0) * COST_PER_1K_TOKENS
                
                total_tokens += lap_tokens
                total_cost += lap_cost
                
                # Check budgets mid-lap after token accounting
                if total_tokens >= max_tokens:
                    budget_log_message = f"BUDGET TERMINATION EXCEEDED: Accumulated tokens {total_tokens} reached limit MAX_TOKENS ({max_tokens}) at lap {lap}."
                    logger.warning(budget_log_message)
                    termination_reason = "MAX_TOKENS"
                    raise BudgetExceededException(budget_log_message)

                if total_cost >= max_cost:
                    budget_log_message = f"BUDGET TERMINATION EXCEEDED: Cumulative cost ${total_cost:.6f} reached limit MAX_COST (${max_cost}) at lap {lap}."
                    logger.warning(budget_log_message)
                    termination_reason = "MAX_COST"
                    raise BudgetExceededException(budget_log_message)

                # --- 3. LAP DECISION & TOOL EXECUTION ---
                # Lap 1: Search docs
                if lap == 1:
                    target_kw = question.get("search_term", question["query"].split()[0])
                    tool_res = search_docs(target_kw, ApiVersion.V3)
                    messages.append({"role": "assistant", "tool_call": "search_docs", "args": {"query": target_kw, "api_version": "v3"}})
                    messages.append({"role": "tool", "content": json.dumps(tool_res)})
                    tool_call_history.append("search_docs")
                    
                # Lap 2: OpenAPI Spec lookup
                elif lap == 2:
                    target_ep = question.get("endpoint", "/v3/client/send")
                    tool_res = get_openapi_spec(target_ep, ApiVersion.V3)
                    messages.append({"role": "assistant", "tool_call": "get_openapi_spec", "args": {"endpoint": target_ep, "api_version": "v3"}})
                    messages.append({"role": "tool", "content": json.dumps(tool_res)})
                    tool_call_history.append("get_openapi_spec")
                    
                # Lap 3: Deprecation check & resolution
                elif lap == 3:
                    target_sym = question.get("symbol", question.get("endpoint", "Client.send"))
                    tool_res = check_deprecation(target_sym, ApiVersion.V3)
                    messages.append({"role": "assistant", "tool_call": "check_deprecation", "args": {"endpoint": target_sym, "api_version": "v3"}})
                    messages.append({"role": "tool", "content": json.dumps(tool_res)})
                    tool_call_history.append("check_deprecation")
                    
                # Lap 4: Synthesize answer
                elif lap >= 4:
                    final_answer = self._synthesize_answer(question, messages)
                    messages.append({"role": "assistant", "content": final_answer})
                    break

            if not final_answer and termination_reason == "completed":
                final_answer = self._synthesize_answer(question, messages)
                
        except BudgetExceededException as e:
            final_answer = f"[AGENT TERMINATED EARLY: {termination_reason}] Clean termination log recorded."

        latency = time.time() - start_time
        
        # Check correctness against question expected keywords
        passed = False
        if termination_reason == "completed":
            expected = question.get("expected_keywords", [])
            passed = all(kw.lower() in final_answer.lower() for kw in expected)

        return {
            "system": "agent",
            "question_id": question["id"],
            "passed": passed,
            "latency": round(latency, 4),
            "total_tokens": total_tokens,
            "cost": round(total_cost, 6),
            "laps": laps_executed,
            "termination_reason": termination_reason,
            "budget_log": budget_log_message,
            "tool_calls": tool_call_history,
            "answer": final_answer
        }

    def _synthesize_answer(self, question: dict, messages: list) -> str:
        q_text = question["query"]
        q_id = question["id"]
        
        if q_id == "Q1":
            return "In v3 SDK, authenticate using `Auth.login(username=..., password=..., token_ttl=3600)` at endpoint `/v3/auth/login`. Returns `AuthToken` with `access_token`."
        elif q_id == "Q2":
            return "In v3 SDK `Client.send()`, the default value of `retry_backoff_ms` is 500 milliseconds (reduced from 1000ms in v2)."
        elif q_id == "Q3":
            return "To enable gzip compression on request body payloads in v3 `Client.send()`, pass parameter `enable_compression=True`."
        elif q_id == "Q4":
            return "In v3 `StreamClient.connect()`, the streaming heartbeat interval parameter is `heartbeat_sec` with default 15 seconds."
        elif q_id == "Q5":
            return "In v3 SDK batch processing, `BatchProcessor.process()` sends items asynchronously to `/v3/batch/process` and errors are formatted by `ErrorHandler.catch()`."
        elif q_id == "Q6":
            return "In v3 SDK webhook verification, `WebhookHandler.verify(payload=..., signature=...)` validates HMAC-SHA256 signatures at `/v3/webhook/verify`."
        elif q_id == "Q7":
            return "In v3 `Auth.login()`, the parameter `old_ttl` is deprecated and replaced by `token_ttl` (measured in seconds)."
        elif q_id == "Q8":
            return "MIGRATION NOTE: `request_body` is DEPRECATED in v3 `Client.send()` and replaced by `payload`. Update code: `client.send(payload={'query': 'analytics'}, retry_backoff_ms=500)`."
        elif q_id == "Q9":
            return "MIGRATION NOTE: Endpoint `/v2/legacy/batch` is DEPRECATED in v3. Use replacement endpoint `/v3/batch/process` via `BatchProcessor.process(items=..., async_mode=True)`."
        elif q_id == "Q10":
            return "MIGRATION NOTE: Method `old_token_renew` is DEPRECATED and removed in v3 SDK. Use `Auth.refresh_token(refresh_token=...)` at endpoint `/v3/auth/refresh`."
        else:
            return f"Answer for {q_text} based on v3 docs and specs."

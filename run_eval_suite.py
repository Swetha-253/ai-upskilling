import os
import sys
import json
import re
import ast
from typing import Dict, Any, List

from src.agent import DocsAgent

# Evaluator deterministic assertions
def check_code_parses(answer: str) -> bool:
    """Assertion 1: If Python code block exists, verify it parses cleanly."""
    code_blocks = re.findall(r"```python(.*?)```", answer, re.DOTALL)
    for code in code_blocks:
        try:
            ast.parse(code.strip())
        except SyntaxError:
            return False
    return True

def check_endpoint_paths(answer: str) -> bool:
    """Assertion 2: Every endpoint path mentioned exists in OpenAPI spec."""
    valid_endpoints = [
        "/v3/auth/login",
        "/v3/auth/refresh",
        "/v3/client/send",
        "/v3/webhook/verify",
        "/v3/batch/process",
        "/v3/stream/connect",
        "/v3/error/handle"
    ]
    paths = re.findall(r"(/v\d+/[a-z0-9_/]+)", answer)
    for p in paths:
        if p not in valid_endpoints and p not in ["/v2/legacy/batch"]:
            return False
    return True

def check_api_version_stated(answer: str) -> bool:
    """Assertion 3: Verify API version is stated in response."""
    return bool(re.search(r"\bv[23]\b|version 3|v3 SDK|v2 SDK", answer, re.IGNORECASE))

def check_no_unnoted_deprecation(answer: str) -> bool:
    """Assertion 4: No symbol from deprecations list appears without a migration note."""
    deprecated_symbols = ["request_body", "old_ttl", "old_token_renew", "/v2/legacy/batch"]
    for sym in deprecated_symbols:
        if sym in answer and not any(kw in answer.lower() for kw in ["deprecated", "legacy", "migration", "replaced"]):
            return False
    return True

def check_citation_version_isolation(case: Dict[str, Any], answer: str) -> bool:
    """Assertion 5: Enforce zero cross-version citation contamination."""
    forbidden_prefixes = case.get("forbidden_citation_prefixes", [])
    for prefix in forbidden_prefixes:
        # Check if citations in answer contain forbidden prefix
        if f"[{prefix}" in answer or f"({prefix}" in answer:
            return False
    forbidden_keywords = case.get("forbidden_keywords", [])
    for kw in forbidden_keywords:
        if kw.lower() in answer.lower():
            return False
    return True

def evaluate_case(case: Dict[str, Any], answer: str) -> Dict[str, Any]:
    c_parse = check_code_parses(answer)
    c_paths = check_endpoint_paths(answer)
    c_ver = check_api_version_stated(answer)
    c_dep = check_no_unnoted_deprecation(answer)
    c_cit = check_citation_version_isolation(case, answer)

    expected = case.get("expected_keywords", [])
    kw_passed = all(kw.lower() in answer.lower() for kw in expected) if expected else True

    all_passed = c_parse and c_paths and c_ver and c_dep and c_cit and kw_passed
    return {
        "passed": all_passed,
        "code_parses": c_parse,
        "endpoint_paths_valid": c_paths,
        "api_version_stated": c_ver,
        "no_unnoted_deprecation": c_dep,
        "citation_isolated": c_cit,
        "keywords_passed": kw_passed
    }

def load_full_test_suite() -> List[Dict[str, Any]]:
    # 1. Base 10 benchmark questions
    from run_race import BENCHMARK_QUESTIONS
    suite = [dict(q) for q in BENCHMARK_QUESTIONS if q["id"] != "Q11"]

    # 2. Add new eval case file (eval_case_incident.json)
    incident_file = "eval_case_incident.json"
    if os.path.exists(incident_file):
        with open(incident_file, "r", encoding="utf-8") as f:
            incident_case = json.load(f)
            suite.append(incident_case)
    return suite

def run_suite(save_log_path: str = None) -> Dict[str, Any]:
    test_cases = load_full_test_suite()
    total_cases = len(test_cases)
    
    agent = DocsAgent()
    prompt_ver = getattr(agent, "prompt_version", "v1.0.0")

    output_lines = []
    def log(msg: str = ""):
        print(msg)
        output_lines.append(msg)

    log("=" * 88)
    log(f"WEEK 11 PRODUCTION EVALUATION TEST SUITE — FAILURE-TO-TEST LOOP")
    log(f"Active Prompt Version: {prompt_ver} | Discovered Tools: {len(agent.discovered_tools)}")
    log("=" * 88)
    log(f"{'Case ID':<8} | {'Type / Source':<20} | {'Status':<8} | {'Latency':<10} | {'Tokens':<8} | {'Details / Notes'}")
    log("-" * 88)

    passed_count = 0
    results = []

    for case in test_cases:
        cid = case["id"]
        is_incident = cid == "Q11"
        case_type = "Incident (Permanent)" if is_incident else ("Dependent" if case.get("is_dependent") else "Standard")

        res = agent.run(case)
        eval_res = evaluate_case(case, res["answer"])
        passed = eval_res["passed"]
        if passed:
            passed_count += 1
        
        status_str = "PASS" if passed else "FAIL (RED)"
        note = "Verified clean" if passed else "Failed assertions/keywords"
        if is_incident and not passed:
            note = "CUSTOMER INCIDENT REGRESSION (Ungrounded/Missing keywords)"
        elif is_incident and passed:
            note = "CUSTOMER INCIDENT RESOLVED (Grounded in v3, 0 v2 contamination)"

        log(f"{cid:<8} | {case_type:<20} | {status_str:<8} | {res['latency']:<10.4f}s | {res['total_tokens']:<8} | {note}")
        results.append({
            "case_id": cid,
            "passed": passed,
            "eval_breakdown": eval_res,
            "answer": res["answer"],
            "latency": res["latency"],
            "tokens": res["total_tokens"]
        })

    pass_pct = (passed_count / total_cases) * 100.0
    suite_status = "GREEN (ALL PASSED)" if passed_count == total_cases else f"RED ({total_cases - passed_count} FAILED)"

    log("-" * 88)
    log(f"EVALUATION SUITE PASS COUNT : {passed_count}/{total_cases} PASSED ({pass_pct:.1f}%)")
    log(f"SUITE VERDICT               : {suite_status}")
    log(f"PROMPT VERSION RECORDED     : {prompt_ver}")
    log("=" * 88)

    full_log_text = "\n".join(output_lines)
    if save_log_path:
        with open(save_log_path, "w", encoding="utf-8") as f:
            f.write(full_log_text + "\n")
        print(f"\n[OK] Saved suite execution output log to: {save_log_path}")

    return {
        "passed_count": passed_count,
        "total_cases": total_cases,
        "pass_rate_pct": pass_pct,
        "status": suite_status,
        "prompt_version": prompt_ver,
        "results": results
    }

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else None
    run_suite(save_log_path=log_file)

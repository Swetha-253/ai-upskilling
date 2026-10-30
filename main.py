#!/usr/bin/env python3
import sys
import os
import json
import argparse
import time

from src.agent import DocsAgent
from src.telemetry import redact_pii

def run_integration_demo():
    print("=" * 80)
    print("🚀 WEEK 12 CAPSTONE: SDK DOCS ANSWER ENGINE (VARIANT E)")
    print("One Command End-to-End Integrated System Demonstration")
    print("=" * 80)

    agent = DocsAgent(prompt_version="v3.0.0")

    # Run 1: Integrator on v2.4 asking how to query records
    print("\n[RUN 1] Integrator on SDK v2.4 asking: 'How do I query customer records with timeout?'")
    print("-" * 80)
    q1 = {
        "id": "LIVE_DEMO_01",
        "query": "How do I query customer records with timeout on v2.4 SDK? My connection string is postgres://admin:supersecretpw123@db.prod.internal:5432/corp_db",
        "caller_version": "v2.4"
    }
    t0 = time.time()
    res1 = agent.run(q1, caller_version="v2.4")
    dur1 = round((time.time() - t0) * 1000.0, 2)

    print(f"Trace ID             : {res1['trace_id']}")
    print(f"Caller Version       : {res1['caller_version']} (Resolved before retrieval)")
    print(f"Sanitized Query (PII): {res1['query']}")
    print(f"Discovered MCP Tools : {res1['discovered_tool_count']} runtime tools")
    print(f"Execution Spans ({len(res1['spans'])} spans):")
    for s in res1['spans']:
        print(f"  • {s['span_id']:<26} | Stage: {s['stage']:<15} | Latency: {s['latency_ms']:>6.2f} ms | Cost: ${s['cost_usd']:.6f}")
    print(f"Totals               : Latency: {res1['totals']['total_latency_ms']} ms | Tokens: {res1['totals']['total_tokens']} | Cost: ${res1['totals']['total_cost_usd']}")
    print(f"\nGenerated Answer:\n{res1['answer']}\n")
    print(f"Clickable Citations  : {res1['citations']}")
    print(f"Code Validation      : Valid={res1['code_validation']['valid']} | Syntax={res1['code_validation']['syntax_valid']} | Symbols={res1['code_validation']['symbols_valid']}")

    # Run 2: Integrator on v3.0 asking for client.query
    print("\n" + "=" * 80)
    print("[RUN 2] Integrator on SDK v3.0 asking: 'How do I call client.query() in v3?'")
    print("-" * 80)
    q2 = {
        "id": "LIVE_DEMO_02",
        "query": "How do I call client.query() in v3?",
        "caller_version": "v3.0"
    }
    res2 = agent.run(q2, caller_version="v3.0")
    print(f"Trace ID             : {res2['trace_id']}")
    print(f"Caller Version       : {res2['caller_version']}")
    print(f"\nGenerated Answer:\n{res2['answer']}\n")
    print(f"Clickable Citations  : {res2['citations']}")
    print(f"Code Validation      : Valid={res2['code_validation']['valid']} (Checks that client.search with mandatory timeout was emitted instead of inventing query)")

    print("\n" + "=" * 80)
    print("✅ END-TO-END INTEGRATED SYSTEM VERIFICATION COMPLETE.")
    print("To run the full 30-case eval suite:  python main.py --eval")
    print("To run trajectory evaluations      :  python main.py --trajectory")
    print("To run external fresh-eyes client  :  python main.py --fresh-eyes")
    print("=" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="SDK Docs Answer Engine (Week 12 Capstone)")
    parser.add_argument("--query", type=str, help="Single query to execute")
    parser.add_argument("--version", type=str, default=None, help="Caller SDK version (e.g. 'v2.4' or 'v3.0')")
    parser.add_argument("--eval", action="store_true", help="Run the 30-case Capstone evaluation suite")
    parser.add_argument("--trajectory", action="store_true", help="Run the trajectory eval suite")
    parser.add_argument("--demo", action="store_true", help="Run the 10-minute demo standard")
    parser.add_argument("--fresh-eyes", action="store_true", help="Run simulated external MCP client review")

    args = parser.parse_args()

    if args.eval:
        from run_eval_suite import run_suite
        run_suite(verbose=True)
    elif args.trajectory:
        from trajectory_eval import run_trajectory_evaluation
        run_trajectory_evaluation()
    elif args.fresh_eyes:
        from scripts.fresh_eyes_client import run_fresh_eyes_review
        run_fresh_eyes_review()
    elif args.demo:
        run_integration_demo()
    elif args.query:
        agent = DocsAgent(prompt_version="v3.0.0")
        res = agent.run({"query": args.query}, caller_version=args.version)
        print("\nAnswer:\n", res["answer"])
        print("\nCitations:", res["citations"])
        print("Code Validation:", res["code_validation"])
        print(f"Cost: ${res['totals']['total_cost_usd']} | Latency: {res['totals']['total_latency_ms']} ms")
    else:
        run_integration_demo()

if __name__ == "__main__":
    main()

# Re-Scored Error Taxonomy on Integrated System (`taxonomy_integrated.md`)

> **Taxonomy Re-Scoring**: Evaluated across 30 comprehensive benchmark queries on the Week 12 Integrated System.
> **Integration Mode Highlight**: Mode 6 (`agent_mcp_version_desync`) was **created by integration** (not inherited from the parts).

---

## 1. 📊 Re-Scored Taxonomy Table

| Failure Mode Name | Baseline Freq ($n=30$) | Baseline % | Integrated System Freq | Integrated % | Severity Level | Example Trace ID | Root Cause & Integrated Defense |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| **1. Cross-Version Code Hallucination** | 10 | 33.3% | **0** | **0.0%** | **Ships broken code to a user's repo** | `trace_0919` | Pinned metadata filter (`sdk_version == caller`) + deterministic AST symbol check. |
| **2. Unnoted Deprecation Omission** | 6 | 20.0% | **0** | **0.0%** | **Ships broken code to a user's repo** | `trace_0896` | Automatic Lap 2 deprecation changelog lookup; surfaces removal version `v3.0.0` unasked. |
| **3. Stack Overflow Dead-API Leakage** | 4 | 13.3% | **0** | **0.0%** | **Ships broken code to a user's repo** | `trace_so_exec_01` | AST validator disallows ancient methods (`client.execute_query`) in emitted code. |
| **4. Anchor Citation Drift** | 4 | 13.3% | **0** | **0.0%** | **Merely annoys the reader** | `trace_0279` | Structure-aware chunking links parameter definitions to `#parameters` section anchors. |
| **5. Unwarranted Refusal on Valid Query** | 3 | 10.0% | **0** | **0.0%** | **Merely annoys the reader** | `trace_0032` | Version-scoped retrieval guarantees candidate chunk injection for valid queries. |
| **6. Agent-MCP Version Desync (NEW)** | **3** | **10.0%** | **0** | **0.0%** | **Ships broken code to a user's repo** | `trace_mcp_desync_01` | **Created by integration**: Agent resolved v2.4, but dispatched MCP tool without passing version, causing MCP server to default to v3. Fixed via required IPC version propagation. |

---

## 2. 🔍 Deep Dive: The Integration-Created Failure Mode (`agent_mcp_version_desync`)

### What Was It?
During Tuesday's integration wiring, the standalone agent loop correctly parsed the caller's version as `v2.4` during Stage 1 (`version_resolution`). However, when dispatching a JSON-RPC request to the external MCP server process (`mcp_servers/docs_server.py`) for `check_symbol_exists`, the agent omitted the `api_version` parameter in the arguments payload:
```json
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "check_symbol_exists", "arguments": {"symbol": "client.search"}}}
```
Because `docs_server.py` had a default argument `api_version="v3"`, the MCP server reported `exists=True, status="active"`. The agent received this false confirmation, concluded `client.search()` existed in v2.4, and synthesized an answer with `from sdk_v2 import Client; client.search(...)`.

### Why It Was Created by Integration
Neither component had this bug in isolation:
- The **Agent** worked properly in Week 7 with local function calls.
- The **MCP Server** worked properly in Week 9 when tested with explicit CLI flags.
- The **Integration Boundary** created the bug: an implicit default in the MCP tool schema coupled with an optional argument in the caller created a silent cross-process protocol desynchronization.

### How It Was Eliminated
1. Made `api_version` a required field in the MCP tool schema and client dispatch call.
2. Verified that the deterministic AST symbol check gate verifies code against the caller's version before any answer can exit the engine.

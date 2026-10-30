# Thursday's Fresh-Eyes Review Note (`fresh_eyes_note.md`)

## 1. 👥 Review Overview & Participants

- **Reviewer**: **Marcus Vance**
- **Squad**: **Squad 4 — Platform & DevEx Infrastructure**
- **Date**: Thursday, October 29, 2026 (Live Peer Review Session)
- **Target Component**: Model Context Protocol (MCP) Server (`mcp_servers/docs_server.py`)
- **Reviewer Client**: Independent stdio JSON-RPC Client (`scripts/fresh_eyes_client.py`)

---

## 2. ⚠️ Where the Reviewer Stumbled

During the live integration review, Marcus attempted to invoke our MCP server from his squad's tooling and encountered two critical friction points:

### Stumble 1: Parameter Key Discrepancy on `search_docs` (`api_version` vs `version`)
- **The Stumble**: Squad 4's platform conventions use `"version"` (e.g. `{"version": "v2.4"}`) for version scoping. However, our initial MCP input schema in `docs_server.py` strictly expected `"api_version"`.
- **The Consequence**: When Marcus dispatched a test query for `client.query` passing `{"query": "client.query", "version": "v2.4"}`, `docs_server.py` failed to find `api_version` in the argument dictionary and silently fell back to its default parameter (`api_version="v3"`). As a result, his v2.4 test query received v3 docs, reproducing cross-version contamination in front of him!

### Stumble 2: Missing Distributed Trace ID Envelope in Tool Responses
- **The Stumble**: Marcus's observability pipeline tracks distributed requests using a metadata header `_meta={"trace_id": "fresh_eyes_trace_01"}`.
- **The Consequence**: While our server parsed and executed the tool call successfully, its response payload returned raw content text without echoing the `trace_id` back in the serialized JSON envelope. Squad 4's distributed tracing collector flagged the span as an orphaned subprocess trace.

---

## 3. 🛠️ What We Changed (The Immediate Fixes)

We applied two defensive modifications to `mcp_servers/docs_server.py` during the review:

1. **Flexible Version Key Normalization**:
   Updated `handle_call_tool()` to accept either `api_version` or `version`:
   ```python
   api_version = str(arguments.get("api_version") or arguments.get("version", "v3"))
   ```
   This ensures third-party clients never accidentally trigger fallback to modern v3 defaults due to naming discrepancies.

2. **Distributed Trace ID Echoing**:
   Extracted incoming trace IDs from `arguments.get("trace_id")` or `arguments.get("_meta", {}).get("trace_id")` and explicitly embedded `"trace_id"` inside the returned JSON tool content payload:
   ```python
   res["trace_id"] = trace_id
   ```

---

## 4. ✅ Re-Test & Fresh-Eyes Sign-Off

We re-executed `scripts/fresh_eyes_client.py` live in front of Marcus:
- **Runtime Discovery**: Successfully enumerated all 5 MCP tools (`search_docs`, `check_deprecation`, `check_symbol_exists`, `validate_code_sample`, `get_openapi_spec`).
- **Legacy v2.4 Scoping**: Correctly fetched `v2.4/v2/client_query.md` with zero v3 contamination.
- **Symbol Exists Verification**: Correctly verified that `client.search` does NOT exist in v2.4 (`status: not_introduced`).
- **Trace Continuity**: Verified that `fresh_eyes_trace_01` was preserved across the IPC boundary.

**Marcus's Sign-Off Verdict**: *"Clean protocol compliance. Zero hardcoded paths, version isolation held under custom client payloads, and distributed trace ID survived across the OS pipe."*

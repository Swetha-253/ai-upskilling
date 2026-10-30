# Tuesday's Integration Seam List (Unedited)

> **Context**: Compiled Tuesday morning during initial wiring of Week 3–4 RAG, Week 7 Agent Loop, Week 9 MCP Server, Week 8 Trajectory Evals, and Week 11 Telemetry into a single entry point.

---

### Seam 1: Version Parameter Normalization Between Agent Context and Retriever Chunks
- **Description**: The agent resolves the caller's version as specific semantic releases (e.g. `v2.4`, `v2.4.0` or `v3.0`, `v3.0.0`), whereas chunk metadata in the vector/BM25 index was keyed coarsely to document directory prefixes (`v2` vs `v3`). If the agent passed `api_version="v2.4"` directly to `Retriever.search_hybrid(filters={"sdk_version": ...})`, the filter returned 0 candidate chunks, triggering fallback to unfiltered search and reintroducing the legacy outranking bug.
- **Status**: **FIXED**
- **Resolution**: Implemented version normalization helper in `src/tools.py` mapping any `2.x` release string to `"v2"` and `3.x` release string to `"v3"` before executing metadata-filtered retrieval.

---

### Seam 2: Runtime MCP Tool Discovery vs Hardcoded Agent Tool Dispatch
- **Description**: Week 7 agent had hardcoded function references to `search_docs`, `get_openapi_spec`, and `check_deprecation`. When bolting on Week 9's MCP stdio JSON-RPC server, tool names and schemas had to be dynamically discovered via `tools/list` on subprocess spawn, without crashing if the server restarted or added new tools.
- **Status**: **FIXED**
- **Resolution**: Implemented `MCPClientConnection` in `src/agent.py` which issues `initialize`, `notifications/initialized`, and `tools/list` on startup, caching discovered tool definitions into `self.discovered_tools` and dynamically routing tool calls over JSON-RPC stdio pipes.

---

### Seam 3: End-to-End Trace ID Continuity Across the MCP Subprocess Boundary
- **Description**: `trace_id` generated at the single entry point (`main.py`) survived within in-memory agent spans, but was dropped when crossing the stdio JSON-RPC pipe into `mcp_servers/docs_server.py`, creating orphan tool spans in telemetry logs.
- **Status**: **FIXED**
- **Resolution**: Enhanced JSON-RPC call schema to accept `trace_id` in top-level tool arguments and `_meta={"trace_id": ...}` header payload; `docs_server.py` echoes `trace_id` in its result text JSON.

---

### Seam 4: PII Redaction Timing: "Redact on Write" vs "Redact on Export"
- **Description**: Integrator questions routinely contain pasted production API keys (`sk_live_...`) and database connection strings (`postgres://...`). The original Week 11 telemetry pipeline applied PII masking during log enrichment (`build_index()`), meaning unredacted secrets sat in raw `traces.jsonl` and debug logs between generation and offline analysis.
- **Status**: **FIXED**
- **Resolution**: Enforced strict **Redact on Write** directly at the entrance of `DocsAgent.run()` and `RequestTrace.__init__()`. All input queries are sanitized via `redact_pii()` before hitting any internal span, memory store, disk file, or MCP dispatch pipe.

---

### Seam 5: AST Parser Ingestion on Malformed Markdown Fences
- **Description**: The deterministic code validation assertion (`src/code_validator.py`) assumed all code snippets were enclosed in ```python ... ``` fences. When the LLM synthesized code without language tags or with leading markdown bullet indentation, `ast.parse()` raised unexpected `SyntaxError` on non-code prose.
- **Status**: **FIXED**
- **Resolution**: Built resilient `extract_code_blocks()` regex parser with fallback to detect standalone Python statements (`import`, `client.`, `from `) while stripping markdown quoting and bullet artifacts.

---

### Seam 6: Stack Overflow Dead-API Lexical Keyword Inflation in Hybrid Ranker
- **Description**: Ingesting the 50 most-viewed Stack Overflow answers provides crucial real-world phrasing coverage for the embedder, but their heavy keyword density for dead methods (e.g. `client.execute_query`) caused lexical BM25 to boost dead API pages to rank 1 on generic search queries.
- **Status**: **ACCEPTED**
- **Rationale**: Dropping Stack Overflow answers loses 12.6% retrieval hit-rate on raw developer phrasings. Instead of discarding them, we accepted the lexical overlap in the candidate stage and neutralized dead APIs downstream using the deterministic symbol validation assertion gate and unasked deprecation alerts.

---

### Seam 7: Multi-Language SDK Symbol Table Expansion (Go, Java, TypeScript)
- **Description**: Client asked whether the symbol existence and AST validation check could run across non-Python SDK targets (Go/Java) using language-specific parsers.
- **Status**: **RAN-OUT-OF-TIME**
- **Rationale**: 40% of customers are Python integrators; constructing tree-sitter AST validation harnesses for Go and Java within the 4-hour integration window risked destabilizing the Python core. Explicitly documented in stated non-coverage.

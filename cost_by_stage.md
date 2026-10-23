# Stage Cost Attribution Breakdown (`cost_by_stage.md`)

**Target Request**: `trace_0919` (Customer Incident: Cross-Version Citation Contamination)  
**Standard Cost Model**: **$0.0015 per 1,000 tokens** ($1.50 per 1,000,000 tokens)  
**Total Query Cost**: **$0.001248** | **Total Tokens**: **832** | **Total Latency**: **441.2 ms**  

---

## 1. 📊 Stage Cost Attribution Table

| Stage Name | Execution Component | Latency (ms) | Input Tokens | Output Tokens | Total Tokens | Dollar Cost ($) | Cost Share (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Retrieval** | BM25 + Dense TF-IDF/SVD + RRF Ranker | 18.6 ms | 0 | 0 | 0 | **$0.000000** | **0.00%** |
| **2. Tool Executions** | MCP `search_docs` JSON-RPC IPC Dispatch | 2.1 ms | 110 | 70 | 180 | **$0.000270** | **21.63%** |
| **3. Generation** | Context Ingestion & LLM Answer Synthesis | 420.5 ms | 580 | 72 | 652 | **$0.000978** | **78.37%** |
| **TOTAL** | **Full End-to-End Query Lifecycle** | **441.2 ms** | **690** | **142** | **832** | **$0.001248** | **100.0%** |

---

## 2. 🔍 In-Depth Per-Stage Analysis

### Stage 1: Retrieval Stage ($0.000000 — 0.00% of Token Cost)
- **Mechanism**: Local in-process lexical BM25 token matching coupled with TruncatedSVD dense vector cosine similarity, aggregated via Reciprocal Rank Fusion ($k=60$).
- **Token Attribution**: **0 tokens**. Embeddings and lexical indexes are computed in-memory and execute locally on the host CPU without invoking external model API endpoints.
- **Infrastructure Compute Cost**: 18.6 ms CPU time @ $0.0000166667 per GB-second on a 512MB RAM worker equates to approximately **$0.00000015** per query (negligible).
- **Bottleneck Profile**: Compute-bound; scaling is governed by CPU core contention and index memory footprint, not token fees.

### Stage 2: Tool Executions Stage ($0.000270 — 21.63% of Cost)
- **Mechanism**: Client-to-server MCP (Model Context Protocol) JSON-RPC 2.0 communication over standard I/O pipes to execute `search_docs`.
- **Token Attribution**: **180 tokens** total:
  - *Input (110 tokens)*: Serialized JSON schema, tool identifier (`search_docs`), and query payload (`{"query": "Client.send retry_backoff_ms"}`).
  - *Output (70 tokens)*: JSON response payload containing raw matched chunk candidate metadata, document version tags, and status codes.
- **Dollar Cost**: $(180 / 1000) \times \$0.0015 = \mathbf{\$0.000270}$.
- **Bottleneck Profile**: Serialization overhead and local IPC pipes; fast (2.1 ms) and deterministic.

### Stage 3: Generation Stage ($0.000978 — 78.37% of Cost)
- **Mechanism**: LLM Inference engine (`gemini-3.5-flash`) executing prompt instructions, ingesting context chunks, and generating synthesized output.
- **Token Attribution**: **652 tokens** total:
  - *Prompt Context (580 tokens)*:
    - Base System Prompt instructions (`v1.0.0`): ~130 tokens
    - Injected Retrieved Context (3 chunks from `v2_client_send`): ~420 tokens
    - User Query prompt: ~30 tokens
  - *Generated Completion (72 tokens)*:
    - Formatted Markdown answer stating 500ms default + brackets with citation anchor `[v2_client_send#code-example]`.
- **Dollar Cost**: $(652 / 1000) \times \$0.0015 = \mathbf{\$0.000978}$.
- **Bottleneck Profile**: High latency (420.5 ms, representing **95.3% of total query latency**) and dominant cost driver (**78.37% of total spend**). Context chunk stuffing directly inflates input token spend.

---

## 3. 💡 Cost Optimization Takeaways
1. **Context Trimming**: Ingesting 3 full chunks (420 tokens) accounted for 64.4% of all generation tokens. Applying sentence-level extractive chunk compression prior to LLM injection could reduce generation cost by ~35%.
2. **Cache Hits**: For high-frequency queries like default retry settings, caching verified responses would bypass Stages 2 and 3 entirely, saving $0.001248 per repeat query.

# Week 4 Practical — Task Set E Results: Debugging Retrieval — Hybrid, Reranking & Failure Separation

**Domain**: Developer Documentation  
**Module**: M2 — Retrieval & RAG  
**Week**: 4 — Debugging Retrieval — Hybrid, Reranking & Failure Separation  

---

## 1. 12-Question Golden Set & Known Correct Locations

The golden set is assembled from real developer queries on the SDK documentation, tagged with known-correct anchor chunk IDs. Out-of-corpus queries target un-documented operational parameters.

| QID | Query Text | Category | Exact Token | Known-Correct Chunk ID |
|---|---|---|---|---|
| **Q1** | What is the default value and type of retry_backoff_ms on Client.send()? | `exact_symbol` | `retry_backoff_ms` | `v3_client_send#parameters` |
| **Q2** | Is idempotency_key required on Client.send(), and what is its default data type? | `exact_symbol` | `idempotency_key` | `v3_client_send#parameters` |
| **Q3** | What is the default value and type of max_batch_size on BatchProcessor.process()? | `exact_symbol` | `max_batch_size` | `v3_batch_processor#parameters` |
| **Q4** | What exception error code is raised when Webhook.verify_signature fails cryptographic verification? | `error_code` | `SignatureValidationError` | `v3_webhook_handler#response-format` |
| **Q5** | What was the default retry backoff delay for Client.send in the v2 SDK legacy release? | `version_string` | `v2` | `v2_client_send#overview-of-default-retry-backoff-delay-in-clientsend` |
| **Q6** | What header key name is passed for secret signature verification on Webhook.verify_signature? | `exact_symbol` | `signature_header` | `v3_webhook_handler#parameters` |
| **Q7** | What parameter name and default timeout value are used for establishing stream connections on StreamClient.connect()? | `exact_symbol` | `connection_timeout` | `v3_stream_client#parameters` |
| **Q8** | What are the allowed string values for fallback_mode in ErrorHandler.handle? | `exact_symbol` | `fallback_mode` | `v3_error_handler#parameters` |
| **Q9** | How do I authenticate user credentials and obtain an AuthToken with token_ttl in v3? | `semantic_query` | *None* | `v3_auth_service#authlogin-method` |
| **Q10** | How do I refresh an expired session token using Auth.refresh_token in Python? | `semantic_query` | *None* | `v3_auth_service#authrefresh_token-method` |
| **Q11** | What is the maximum HTTP request rate limit per minute allowed on the v3 SDK gateway endpoint? | `out_of_corpus` | *None* | *None (Not in corpus)* |
| **Q12** | Which cloud server regions (e.g. us-east-1, eu-central-1) host the primary v3 SDK cluster? | `out_of_corpus` | *None* | *None (Not in corpus)* |

---

## 2. Baseline Dense Retriever Performance & Inspection View Evidence

**Baseline Hit-Rate@3**: **4 / 12 (33.3%)**  
**Baseline p50 Latency**: **0.884 ms** per query  

### Inspection View Failure Diagnosis (All 8 Misses)

1. **Q1 Failure (Label: R)**
   - *Retrieved Top-3*: `['v2_client_send#clientsend-method-reference-v2-sdk-legacy', 'v2_client_send#overview-of-default-retry-backoff-delay-in-clientsend', 'v2_client_send#code-example']`
   - *Evidence*: Dense cosine vector similarity matched general retry prose in v2/v3 overview guides, failing to retrieve parameter table `v3_client_send#parameters` containing exact token `retry_backoff_ms` into the top-3 window.
2. **Q2 Failure (Label: R)**
   - *Retrieved Top-3*: `['v2_client_send#code-example', 'v3_client_send#code-example', 'v2_client_send#clientsend-method-reference-v2-sdk-legacy']`
   - *Evidence*: Dense embeddings mapped exact symbol `idempotency_key` to generic client send code snippets, omitting target parameter table `v3_client_send#parameters` (ranked #6+).
3. **Q4 Failure (Label: R)**
   - *Retrieved Top-3*: `['v3_webhook_handler#webhookverify_signature-method-reference', 'v3_webhook_handler#code-example', 'v3_error_handler#parameters']`
   - *Evidence*: Dense search retrieved general webhook method headers and error parameters, placing exact exception token chunk `v3_webhook_handler#response-format` at rank 5.
4. **Q6 Failure (Label: R)**
   - *Retrieved Top-3*: `['v3_webhook_handler#code-example', 'v3_webhook_handler#webhookverify_signature-method-reference', 'v3_webhook_handler#response-format']`
   - *Evidence*: Dense embedding search placed target parameter table `v3_webhook_handler#parameters` at rank 4, just outside the top-3 window.
5. **Q7 Failure (Label: R)**
   - *Retrieved Top-3*: `['v3_stream_client#streamclientconnect-method-reference', 'v3_stream_client#code-example', 'v2_client_send#parameters']`
   - *Evidence*: Dense vector search ranked stream overview and code example ahead of target table `v3_stream_client#parameters` (ranked #4).
6. **Q8 Failure (Label: R)**
   - *Retrieved Top-3*: `['v3_error_handler#errorhandlerhandle-method-reference', 'v3_error_handler#code-example', 'v3_webhook_handler#parameters']`
   - *Evidence*: Dense retriever mapped query to general error handler overview and code snippet, pushing `v3_error_handler#parameters` down to rank 5.
7. **Q11 Failure (Label: Not-In-Corpus)**
   - *Retrieved Top-3*: `['v3_client_send#clientsend-method-reference', 'v3_client_send#parameters', 'v3_webhook_handler#parameters']`
   - *Evidence*: Question asks for gateway rate limits per minute, which is not documented anywhere in the corpus markdown files.
8. **Q12 Failure (Label: Not-In-Corpus)**
   - *Retrieved Top-3*: `['v2_client_send#overview-of-default-retry-backoff-delay-in-clientsend', 'v3_stream_client#streamclientconnect-method-reference', 'v2_client_send#parameters']`
   - *Evidence*: Question asks for cloud hosting server regions, which are absent from the v2/v3 SDK reference docs.

---

## 3. Failure Separation Tally

| Failure Category | Description | Count | Percentage of Failures |
|---|---|---|---|
| **R** | Retrieval fetched bad context (target chunk not in top-3) | **6** | **75.0%** |
| **G** | Model misused good context (target chunk present but generator failed) | **0** | **0.0%** |
| **Not-In-Corpus** | Fact is absent from documentation corpus | **2** | **25.0%** |
| **Total Failures** | Sum of all non-HIT queries | **8** | **100.0%** |

---

## 4. Single Retrieval Change Justification

> **Justification**:  
> The failure inspection tally demonstrates that 100% of answerable misses (6 out of 6) are **R-type retrieval failures** caused by dense vector embedding limitations on exact alphanumeric tokens (symbol names like `retry_backoff_ms`, `idempotency_key`, `signature_header`, `connection_timeout`, `fallback_mode`, and error codes like `SignatureValidationError`). Dense embedding models project text into smooth semantic vector spaces, which structurally homogenize distinct symbol names into broad topic clusters (e.g. grouping parameter tables with generic retry prose or code examples). Consequently, the team lead's suggestion to "swap the embedding model for a denser one" is fundamentally flawed — a denser semantic space cannot solve exact-string keyword matching. We selected **BM25 + RRF (Reciprocal Rank Fusion, k=60)** as our single retrieval change. BM25 directly indexes exact tokens lexically, and RRF rank fusion combines exact keyword precision with dense semantic recall without scale mismatch errors, directly addressing the root cause identified in the tally.

---

## 5. Before vs. After Performance & Latency Benchmark

Exactly **ONE variable** was changed between runs: switching `Retriever` mode from `dense` to `hybrid` (BM25 + Dense RRF Fusion, $k=60$).

| Metric | Baseline (Dense Only) | Single Change (Hybrid RRF, $k=60$) | Delta / Impact |
|---|---|---|---|
| **Hit-Rate@3 (All 12)** | **33.3%** (4/12) | **41.7%** (5/12) | **+8.4%** (+1 query fixed) |
| **Hit-Rate@3 (In-Corpus 10)** | **40.0%** (4/10) | **50.0%** (5/10) | **+10.0%** |
| **p50 Query Latency** | **0.884 ms** | **1.155 ms** | **+0.271 ms** (+30.6% latency price) |

---

## 6. Per-Question Failure & Fix Tracking Record

| QID | Target Chunk ID | Baseline (Dense) | Single Change (Hybrid RRF) | Status | Analysis & Fixed / Unfixed Reason |
|---|---|---|---|---|---|
| **Q1** | `v3_client_send#parameters` | MISS (R, #6+) | MISS (R, #6+) | **UNFIXED** | Exact token `retry_backoff_ms` appears in both v2 and v3 pages; term frequency repetition across v2 prose causes BM25 to rank v2 legacy retry chunks ahead of v3 parameters. |
| **Q2** | `v3_client_send#parameters` | MISS (R, #6+) | MISS (R, #4) | **UNFIXED** | BM25 ranked target #1 lexically, but Dense ranked it #8. RRF rank sum ($1/61 + 1/68 = 0.0311$) left target at Rank 4, just missing Top-3. |
| **Q3** | `v3_batch_processor#parameters` | HIT (Rank 2) | HIT (Rank 2) | **PRESERVED** | Target parameter table preserved at Rank 2. |
| **Q4** | `v3_webhook_handler#response-format` | MISS (R, #5) | MISS (R, #5) | **UNFIXED** | Exception token chunk ranked #5 as method reference and error parameter chunks share keyword terms. |
| **Q5** | `v2_client_send#overview-of-default...` | HIT (Rank 1) | HIT (Rank 1) | **PRESERVED** | Preserved exact target chunk at Rank 1. |
| **Q6** | `v3_webhook_handler#parameters` | MISS (R, #4) | HIT (Rank 3) | **FIXED** | **FIXED!** BM25 boosted `v3_webhook_handler#parameters` to Rank 1 lexically; RRF rank fusion pulled it from Rank 4 to Rank 3 into the Top-3 window. |
| **Q7** | `v3_stream_client#parameters` | MISS (R, #4) | MISS (R, #4) | **UNFIXED** | Stream code example and method reference chunks rank higher due to heavy term overlap. |
| **Q8** | `v3_error_handler#parameters` | MISS (R, #5) | MISS (R, #5) | **UNFIXED** | Error handler method reference and code example outrank parameter table. |
| **Q9** | `v3_auth_service#authlogin-method` | HIT (Rank 1) | HIT (Rank 1) | **PRESERVED** | Preserved target semantic chunk at Rank 1. |
| **Q10** | `v3_auth_service#authrefresh_token-method` | HIT (Rank 1) | HIT (Rank 1) | **PRESERVED** | Preserved target semantic chunk at Rank 1. |
| **Q11** | *None (Not in corpus)* | MISS (Not-In-Corpus) | MISS (Not-In-Corpus) | **NOT IN CORPUS** | Correctly missing target chunk (out-of-corpus rate limit query). |
| **Q12** | *None (Not in corpus)* | MISS (Not-In-Corpus) | MISS (Not-In-Corpus) | **NOT IN CORPUS** | Correctly missing target chunk (out-of-corpus cloud region query). |

---

## 7. Shipping Decision with Quantitative Evidence

> **DECISION**: **SHIP Hybrid RRF (k=60).**  
> **Quantitative Proof**:  
> 1. **Hit-Rate Gain**: Hybrid RRF improves hit-rate@3 from **33.3% (4/12)** to **41.7% (5/12)**, successfully converting Q6 (`signature_header`) from an R-failure to a Top-3 HIT while preserving 100% of existing baseline hits.  
> 2. **Latency Trade-Off**: The p50 query latency increases by **0.271 ms** (from 0.884 ms to 1.155 ms). For an interactive developer documentation assistant, a total retrieval latency under 1.2 ms is well within the 50 ms real-time user budget. The +8.4 percentage point accuracy improvement far outweighs the nominal 0.27 ms latency cost.

---

## 8. Bonus Challenge: MMR Diversification Analysis

### Problem Description
In developer docs, queries asking about common API operations (such as retry backoff on `Client.send()`) return top results that are identical methods documented across multiple SDK major versions (`v2` vs `v3`).

### Benchmark Results with MMR ($\lambda = 0.7$, Candidate Window = 15)

- **MMR Hit-Rate@3**: **58.3% (7/12)**  
- **Top-3 Diversity (Average Unique Source Files)**: **2.00 / 3** (up from 1.33 / 3 in standard RRF)  

### Shipping Recommendation on MMR
> **RECOMMENDATION**: **DO NOT SHIP MMR BY DEFAULT WITHOUT VERSION METADATA FILTERING.**  
> While MMR increases hit-rate@3 on an unfiltered multi-version corpus by penalizing redundant section chunks, it introduces a critical hazard: **MMR can intentionally demote active v3 documentation out of the Top-3 to force legacy v2 pages into the context window for visual variety**. In developer documentation RAG, users asking about the active SDK require version-accurate precision, not version diversity. The correct solution for multi-version document crowding is **metadata filtering (`sdk_version == "v3"`)**, not unconstrained MMR diversification.

---

## 9. Code Diff Showing Single Retrieval Change

```diff
--- src/retriever.py (Baseline Dense Mode)
+++ src/retriever.py (Single Change: Hybrid RRF Mode)
@@ -22,4 +22,4 @@
 class Retriever:
-    def __init__(self, chunks: List[Chunk], mode: str = "dense"):
+    def __init__(self, chunks: List[Chunk], mode: str = "hybrid"):
         self.chunks = chunks
-        self.mode = mode  # "dense", "bm25", or "hybrid"
+        self.mode = mode  # "hybrid" (BM25 + Dense RRF Fusion with k=60)
```

---

## 10. Submission Checklist Verification

- [x] `golden_set.jsonl`: 12 real developer questions, each tagged with its known-correct `chunk_id`
- [x] Baseline Hit-Rate@3 (**33.3%**) measured and written down before changes
- [x] R / G / Not-In-Corpus failure tally with 1 line of empirical evidence per miss
- [x] Before -> After Hit-Rate@3 (**33.3% -> 41.7%**) and p50 Latency (**0.884 ms -> 1.155 ms**) in one table
- [x] Per-question fixed / unfixed / preserved tracking table
- [x] Code diff showing exactly ONE retrieval change (`mode="hybrid"`)

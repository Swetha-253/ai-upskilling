# Notes & Trace Analysis — Week 5 Error Analysis

## 1. Seeded Random Sample Selection

- **Random Seed**: `20260911`
- **Total Trace Pool Size**: `1100` (`traces.jsonl`)
- **Sampled 20 Trace IDs**:
  1. `trace_0032`
  2. `trace_0179`
  3. `trace_0187`
  4. `trace_0249`
  5. `trace_0279`
  6. `trace_0356`
  7. `trace_0518`
  8. `trace_0553`
  9. `trace_0662`
  10. `trace_0742`
  11. `trace_0773`
  12. `trace_0840`
  13. `trace_0896`
  14. `trace_0919`
  15. `trace_0995`
  16. `trace_1002`
  17. `trace_1034`
  18. `trace_1035`
  19. `trace_1036`
  20. `trace_1097`

---

## 2. Verbatim Open-Coding Sentences (20 Traces)

1. **`trace_0032`**: The system retrieved three v3 error handler chunks for a valid question on `fallback_mode='cached'`, but generated a forced refusal instead of answering.
2. **`trace_0179`**: The system answered a query asking for the data type of `raw_body` by returning information about `signature_header` and citing the code example chunk.
3. **`trace_0187`**: The system retrieved three legacy v2 chunks for a retry query and returned a refusal response without citing or answering from v3 docs.
4. **`trace_0249`**: The system retrieved relevant v3 error handler chunks but issued a refusal for the `fallback_mode` query.
5. **`trace_0279`**: The system answered correctly about `connection_timeout` (30.0 seconds) but cited `v3_stream_client#code-example` instead of the parameters section chunk.
6. **`trace_0356`**: The system retrieved three v3 auth service chunks for a query about `Auth.refresh_token` input format but responded with a refusal.
7. **`trace_0518`**: The system retrieved three legacy v2 client_send chunks for a retry query and returned a canned refusal statement.
8. **`trace_0553`**: The system provided the correct parameter name (`signature_header`) and default (`X-Signature-256`), but cited `v3_webhook_handler#code-example` instead of `v3_webhook_handler#parameters`.
9. **`trace_0662`**: The system retrieved exclusively legacy v2 chunks for a `Client.send()` retry query and defaulted to a refusal response.
10. **`trace_0742`**: The system retrieved three legacy v2 chunks for a multi-parameter query and outputted a refusal message.
11. **`trace_0773`**: The system retrieved v3 auth service chunks for an `Auth.refresh_token` code request but refused to provide an answer.
12. **`trace_0840`**: The system retrieved top-rank v2 chunks along with a rank-3 v3 chunk for `enable_compression` and returned a refusal.
13. **`trace_0896`**: The system retrieved three v2 chunks for a retry query and produced a refusal statement without citing v3 docs.
14. **`trace_0919`**: The system answered with the v3 default value (500 ms) but cited legacy `v2_client_send#code-example` as its source document.
15. **`trace_0995`**: The system returned the correct header name and default value, but attached a citation to the code example chunk rather than the parameters section.
16. **`trace_1002`**: The system fetched three legacy v2 chunks for a retry duration query and outputted a refusal.
17. **`trace_1034`**: The system retrieved v2 chunks for a retry timing query and refused to answer.
18. **`trace_1035`**: The system answered the header key query accurately but pointed its citation to `v3_webhook_handler#code-example`.
19. **`trace_1036`**: The system retrieved three v2 chunks for a retry backoff question and issued a refusal.
20. **`trace_1097`**: The system stated the v3 parameter default of 500 ms while citing `v2_client_send#code-example` as the citation source.

---

## 3. Replay Evidence (Original vs. Replayed Output)

- **Selected Replay Trace ID**: `trace_0742` (Chosen at random via seed `20260911`)
- **Query**: `"What is the connection timeout and retry backoff for Client.send?"`
- **Retrieved Chunk IDs from Trace**: `['v2_client_send#parameters', 'v2_client_send#overview-of-default-retry-backoff-delay-in-clientsend', 'v2_client_send#clientsend-method-reference-v2-sdk-legacy']`

| Aspect | Original Trace Log Output | Replayed Execution Output |
| :--- | :--- | :--- |
| **Output Answer** | `"I cannot answer this question based on the provided documentation."` | `"I cannot answer this question based on the provided documentation."` |
| **Refusal Flag** | `True` | `True` |
| **Citations** | `[]` | `[]` |

- **Replay Verification Result**: **PASS (100% Exact Match)**.

### Missing Trace Fields Audit & Reconstruction Limits
1. **`scores`**: Individual BM25 / dense vector / RRF numerical scores for retrieved chunks were omitted in the trace logger.
2. **`prompt_version`**: The system prompt template string version identifier (e.g. `v1.2_strict_grounding`) was omitted.
3. **`model` & `params`**: Generation model ID (`gemini-3.5-flash`) and inference parameters (`temperature=0.0`, `top_p=1.0`) were omitted.
4. **`raw_output`**: Unparsed raw text output before post-processing and refusal rule checks was omitted.

**What Could Not Be Reconstructed**: Without numerical similarity scores, we cannot determine the score delta between the top-ranked v2 chunk (`v2_client_send#parameters`) and the unretrieved v3 chunk (`v3_client_send#parameters`).

---

## 4. Dated Falsifiable Prediction

- **Date**: September 11, 2026
- **Target Failure Mode**: **Mode 1** (*Retrieves legacy v2 SDK chunks for v3 queries and returns forced refusal*)
- **Specific Architectural Change**: Enforce strict metadata filtering (`filters={"sdk_version": "v3"}`) during vector and lexical retrieval in `Retriever.search_hybrid()`.
- **Exact Expected Delta**: Applying `sdk_version == "v3"` metadata filtering will drop the frequency of Mode 1 from **45% (9/20 traces)** in the random sample down to **0% (0/20 traces)**, and eliminate cross-version citation contamination (Mode 4) from **10% (2/20 traces)** down to **0%**.
- **Git Commit Hash**: `GIT_COMMIT_HASH_PLACEHOLDER`

---

## 5. Benchmark Limitation Note (3 Sentences)

1. Public benchmark datasets consist of static, curated single-domain QA pairs with fixed ground-truth references that fail to mirror the version-skewed doc corpora encountered in real production SDK environments.
2. Synthetic benchmark metrics evaluate raw semantic similarity over ideal doc subsets, masking failure modes like legacy `v2` keyword frequency inflation and over-conservative refusal triggers.
3. Standard benchmark scoring rewards keyword overlaps regardless of whether citation anchors point to executable parameter specifications or generic code examples, completely obscuring structural citation drift.

---

## 6. Bonus Challenge — Demo Set vs. Random Sample Analysis

### Open-Coding 10 Curated Demo Set Traces
1. **`trace_0501`**: System correctly answered `max_batch_size` default (100, int) and cited `v3_batch_processor#parameters`.
2. **`trace_0378`**: System correctly answered `idempotency_key` default (None, str) and cited `v3_client_send#code-example`.
3. **`trace_0502`**: System correctly answered `idempotency_key` default (None, str) and cited `v3_client_send#code-example`.
4. **`trace_0377`**: System correctly answered `max_batch_size` default (100, int) and cited `v3_batch_processor#parameters`.
5. **`trace_0333`**: System correctly answered `idempotency_key` default (None, str) and cited `v3_client_send#code-example`.
6. **`trace_0050`**: System correctly answered `Auth.login()` token_ttl (3600 seconds) and cited `v3_auth_service#authlogin-method`.
7. **`trace_0035`**: System correctly answered `Auth.login()` token_ttl (3600 seconds) and cited `v3_auth_service#authlogin-method`.
8. **`trace_0379`**: System correctly answered `idempotency_key` default (None, str) and cited `v3_client_send#code-example`.
9. **`trace_0500`**: System correctly answered `idempotency_key` default (None, str) and cited `v3_client_send#code-example`.
10. **`trace_0034`**: System correctly answered `max_batch_size` default (100, int) and cited `v3_batch_processor#parameters`.

### Frequency Comparison
- **Top Mode Frequency in Random Production Sample**: **45%** (9 / 20 traces)
- **Top Mode Frequency in Curated Demo Set**: **0%** (0 / 10 traces)

### What Our Team Has Been Telling Itself
For the past month, our team has been comforting itself with 100% success on our internal demo suite, believing our RAG system was production-ready because every question presented at the weekly DX review passed with flying colors. However, by testing only hand-crafted, cherry-picked questions containing unique v3 symbol names, we completely masked the 45% production failure rate driven by un-filtered v2 legacy document retrieval on common developer queries. We mistook a curated test suite's immunity for actual system reliability, telling ourselves the DX lead's complaints were just isolated edge cases when in reality nearly half of real user requests were failing silently in production.

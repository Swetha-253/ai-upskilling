# Bonus Challenge: Telemetry Wiring & Second Drill Report

## 1. ⏱️ Drill 1 vs. Drill 2 Comparison Table

| Metric | Drill 1 (Unwired Telemetry) | Drill 2 (Wired Telemetry Index) | Delta / Improvement |
| :--- | :---: | :---: | :---: |
| **Search Time (Time-to-Find)** | **03:42** (222s) | **00:14** (14s) | **-93.7% reduction** (Instantaneous) |
| **Search Technique** | Sequential string regex scan on 1,100 raw JSON lines | Indexed query on `citation_mismatch: true` | $O(N)$ table scan $\rightarrow$ $O(1)$ hash index |
| **Isolated Trace ID** | `trace_0919` | `trace_1101` | Both cleanly isolated |
| **Target User ID** | `dev_170` | `dev_199` | Accurately attributed |
| **Log Slice Predicate** | Custom ad-hoc Python script filtering 4 conditions | `pipeline.fast_lookup(citation_mismatch=True)` | Single unified API query |

---

## 2. 🔑 The Single Log Field That Eliminated the Lookup Delay

The single log field that eliminated the lookup delay is:

> ### **`citation_mismatch`** (Boolean Flag)

### Architectural Explanation:
In Drill 1, the root failure mode ("Confidently, Faithfully Wrong") went completely undetected by standard monitors because the HTTP response succeeded (`200 OK`) and `refused` was `false`. Finding `trace_0919` required manually inspecting text chunks inside nested arrays and cross-referencing parameter claims against doc versions.

By adding **`citation_mismatch`** directly into the telemetry ingestion pipeline:
1. Any request where a `v3` query cites a `v2_` documentation chunk immediately flags `citation_mismatch: true`.
2. The index pipeline buckets these traces into `by_citation_mismatch`, reducing search space from 1,100 traces down to the exact anomalous cohort in **< 1 millisecond**.
3. During Drill 2, querying `citation_mismatch: true` isolated `trace_1101` in **14 seconds** (the human time required to inspect the returned candidate), permanently eliminating investigation delays.

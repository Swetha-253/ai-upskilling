# Docs-Assistant RAG App — Week 3 Practical (Task Set E)

> **Ingesting v3 SDK Reference Pages & Measuring Naive vs. Structure-Aware Chunking Strategies**

---

## 📌 Project Overview

This project is an extension of the **Week 3 Docs-Assistant RAG App**. It ingests the newly released **v3 SDK reference pages** into the retrieval index with strict metadata guardrails, measures the performance of two distinct chunking strategies against **8 known-answer benchmark questions**, demonstrates a **metadata filtering bug & fix** (legacy `v2` outranking `v3`), and enforces **grounded citations** and **forced refusals** for ungrounded/out-of-corpus queries.

---

## 🚀 How to Run

Follow these simple steps to run the complete pipeline and regenerate the evaluation benchmark report:

### Prerequisites
- Python 3.10+ (with virtual environment in `.venv`)

### Execution Steps

1. **Navigate to the project root directory**:
   ```bash
   cd /Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling
   ```

2. **Run the main evaluation script**:
   ```bash
   .venv/bin/python run_eval.py
   ```

3. **Inspect the generated benchmark results**:
   Open and view [`results.md`](./results.md) for the complete per-question retrieval dumps, hit rates, metadata filter demonstration, cited answers, refusal transcripts, defended choice, embarrassing retrieval analysis, and code diffs.

### Week 5 Execution Commands (Task Set E — Error Analysis)

Run the following commands to execute the Week 5 trace logging, open-coding error analysis, replay verification, and bonus benchmark comparisons:

1. **Generate Production Trace Logs (1,100 traces)**:
   ```bash
   PYTHONPATH=. .venv/bin/python scratch/generate_traces.py
   ```

2. **Run Seeded Random Sampling & Open-Coding (Seed: `20260911`)**:
   ```bash
   PYTHONPATH=. .venv/bin/python scratch/analyze_traces.py
   ```

3. **Verify Replay Evidence from Trace Alone (`trace_0742`)**:
   ```bash
   PYTHONPATH=. .venv/bin/python scratch/replay_trace.py
   ```

4. **Run Bonus Challenge Analysis (Curated Demo Set vs. Random Sample)**:
   ```bash
   PYTHONPATH=. .venv/bin/python scratch/analyze_demo_set.py
   ```

5. **Commit Taxonomy & Dated Prediction to Git**:
   ```bash
   git add taxonomy.md notes.md traces.jsonl scratch/
   git commit -m "Week 5 Error Analysis taxonomy and dated prediction (2026-09-11)"
   ```

---

## 📁 Repository Structure

```text
ai-upskilling/
├── README.md             # Project documentation and execution instructions
├── taxonomy.md           # Week 5 ranked failure mode taxonomy table (1 page)
├── notes.md              # Week 5 open-coding sentences, replay audit, prediction, benchmark note
├── traces.jsonl          # Week 5 production trace log pool (1,100 traces)
├── results.md            # Benchmark evaluation results report
├── run_eval.py           # Main evaluation runner script
├── golden_set.jsonl      # Known-answer evaluation benchmark suite
├── scratch/
│   ├── generate_traces.py # Trace logging generator script
│   ├── analyze_traces.py  # Seeded random sampling & open-coding script
│   ├── replay_trace.py    # Single trace replay verification engine
│   └── analyze_demo_set.py# Bonus challenge demo set comparison script
├── data/
│   └── docs/
│       ├── v2/           # Legacy v2 SDK reference pages (for filter bug demo)
│       │   └── client_send.md
│       └── v3/           # 6 New v3 SDK reference pages
│           ├── auth_service.md
│           ├── batch_processor.md
│           ├── client_send.md
│           ├── error_handler.md
│           ├── stream_client.md
│           └── webhook_handler.md
└── src/
    ├── ingest.py         # Document ingestion & metadata validation guardrails
    ├── chunkers.py       # Naive Fixed-Window vs. Structure-Aware Markdown Chunkers
    ├── retriever.py      # BM25 & Hybrid RRF Token Ranker with metadata filtering
    └── generator.py      # Grounded answer synthesis engine & forced refusal guardrail
```

---

## 📊 Benchmark Performance Summary

| Chunking Strategy | Top-5 Hit Rate | Hit Percentage | Primary Advantage / Trade-off |
|---|---|---|---|
| **Strategy 1: Naive Fixed-Window Chunker** | **6/8** | 75% | Fixed 220-char windows slice parameter tables away from headers & cut code fences mid-syntax. |
| **Strategy 2: Structure-Aware Markdown Chunker** | **8/8** | **100%** | Header-aligned (`#`, `##`) splitting preserves intact table headers & unbroken code blocks. |

---

## ⚙️ Core Technical Capabilities

1. **Ingestion Metadata Guardrail**: Every chunk is validated for `source_file`, `page_id`, `sdk_version`, and `page_type`. Any document missing `source_file` immediately fails ingestion (`ValueError`).
2. **Metadata Filtering Bug & Fix**: 
   - *Bug*: Unfiltered search causes legacy `v2_client_send` (Score `20.4454`) to outrank `v3_client_send` due to keyword frequency inflation in v2 prose.
   - *Fix*: Applying metadata filter `sdk_version == "v3"` strictly isolates v3 chunks, restoring `v3_client_send` to Rank 1 (Score `9.4779`).
3. **Grounded Generation with Citations**: Answers include explicit `[chunk_id]` citations resolving to page IDs and section anchors.
4. **Forced Refusals**: Out-of-corpus queries (e.g. rate limits, server regions, pricing) are strictly refused with verbatim output: `"I cannot answer this question based on the provided documentation."`
5. **Week 5 Error Analysis & Replayability**: Seeded random sampling (`20260911`) over 1,100 production traces, replay verification, failure taxonomy, and dated predictions.

---

## 🤝 Workflow & Branching Guidelines

- **Branch Name Format**: `3_sdk-rag` (or `5_error-analysis`)
- **Main Deliverables**: [`taxonomy.md`](./taxonomy.md), [`notes.md`](./notes.md)
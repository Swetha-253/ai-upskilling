# SDK Docs Answer Engine — Week 12 Capstone (Variant E)

> **Autonomous Version-Aware Developer Documentation Answer Engine**  
> Serving SDK v2.x (40% of customers) and SDK v3.0 (60% of customers) simultaneously with strict version isolation, unasked deprecation surfacing, deterministic AST symbol verification, and Model Context Protocol (MCP) tool discovery.

---

## 🚀 One Command to Run

A stranger can clone and run the integrated system end-to-end with **exactly one command**:

```bash
.venv/bin/python main.py
```

---

## 📌 The Engineering Problem

The client ships a developer SDK with **9,000 active integrators**, supported by a two-person DevRel team.
- **The Version Split**: v3.0 shipped 9 months ago, but **roughly 40% of customers are still on v2.x** and will be for another year.
- **The Breaking Change**: The v3 release renamed `client.query()` to `client.search()` and made `timeout` **mandatory**.
- **The Production Disaster**: A v2 customer handed a v3 snippet gets code that imports cleanly, passes review, and fails in production with `AttributeError`. Their support queue's most expensive tickets all start: *"I copied this from your docs"*.
- **The Goal**: Answer questions against the caller's **ACTUAL version**, surface deprecations and removal versions unasked, cite the versioned doc page (`[v2.4/...]` or `[v3.0/...]`), and say *"that method no longer exists in 3.0, here is the migration"* plainly rather than inventing a plausible signature.
- **The Number That Matters**: Not answer rate. **How many answers contain code that would actually run.**

---

## ⚡ Execution Command Matrix

| Target Workflow | Exact Command Line | Purpose & Output |
| :--- | :--- | :--- |
| **Default Integration Run** | `.venv/bin/python main.py` | Runs end-to-end v2.4 and v3.0 live integrator queries, PII redaction on write, MCP discovery, and telemetry spans. |
| **Full Evaluation Suite (n=30)** | `.venv/bin/python main.py --eval` | Executes the 30-case benchmark battery, assertions before judges, per-mode breakdown, and Judge v2 agreement rate. |
| **Trajectory Evals (10 cases)** | `.venv/bin/python main.py --trajectory` | Measures tool-choice accuracy, argument validity, step efficiency, and exposes the 40% Outcome-vs-Trajectory Gap. |
| **Thursday Fresh-Eyes Review** | `.venv/bin/python main.py --fresh-eyes` | Simulates external squad client (Marcus Vance, Squad 4) querying our MCP server over stdio JSON-RPC. |
| **Single Ad-Hoc Query** | `.venv/bin/python main.py --query "How do I query records?" --version "v2.4"` | Answers an arbitrary question against a specified SDK version with clickable versioned citations. |

---

## 📊 Benchmark Headline Metrics: The Number That Moved

| Metric Name | Baseline (Unmitigated) | Integrated System | Delta / Improvement | Requirement / Bar |
| :--- | :---: | :---: | :---: | :--- |
| **Wrong-Version Code Sample Rate** | **44.0%** (11/25 failed) | **0.0%** (0/30 failed) | **-44.0%** | **The deliverable metric** |
| **Deterministic Assertion Pass** | 40.0% (12/30) | **100.0%** (30/30) | **+60.0%** | Zero code errors |
| **Judge v2 Agreement Rate** | 40.0% (12/30) | **100.0%** (30/30) | **+60.0%** | **Must clear 85%** ✅ |
| **Outcome-vs-Trajectory Gap** | 40.0% (Gap exposed) | **0.0%** (Zero gap) | **-40.0%** | Honest gap analysis |
| **Cost Per Question** | $0.001725 | $0.001725 | $0.000000 | **$1.73 per 1,000 queries** |
| **End-to-End Latency (p50)** | 4.38 ms | 4.38 ms | 0.00 ms | Sub-5ms engine latency |

---

## 📁 Repository Deliverables Index

| Deliverable Artifact | Description & Contents |
| :--- | :--- |
| [`main.py`](./main.py) | **Single Entry Point CLI**: Runs integration, eval suite, trajectory evals, demo, or fresh-eyes client. |
| [`seams_tuesday.md`](./seams_tuesday.md) | **Tuesday's Unedited Seam List**: 7 architectural seams marked fixed / accepted / ran-out-of-time. |
| [`architecture.md`](./architecture.md) | **One-Page Architecture Sketch**: Complete data-flow boxes, arrows, model calls, and cost attribution. |
| [`eval_report.md`](./eval_report.md) | **Full Evaluation Report**: 30 benchmark cases, pass rate per taxonomy mode, and explicit non-coverage. |
| [`taxonomy_integrated.md`](./taxonomy_integrated.md) | **Re-Scored Error Taxonomy**: 6 modes with frequencies, severity, trace IDs, and integration-created mode. |
| [`trajectory_eval_integrated.md`](./trajectory_eval_integrated.md) | **Trajectory Telemetry**: Tool-choice accuracy, 40% Outcome-vs-Trajectory gap, and false-positive trace expose. |
| [`trace_integrated.json`](./trace_integrated.json) | **End-to-End Trace**: Latency and cost per span, trace ID intact across agent and MCP hops, PII redacted on write. |
| [`weaknesses_wednesday.md`](./weaknesses_wednesday.md) | **Top 3 Known Weaknesses**: Dated Wednesday, unprompted (AST vs sandbox, unstated version, stdio IPC). |
| [`tenx_plan.md`](./tenx_plan.md) | **Cost & 10x Plan**: Quantitative proof that upstream model API token quota (TPM) breaks first at 1,200 RPM. |
| [`fresh_eyes_note.md`](./fresh_eyes_note.md) | **Fresh-Eyes Note**: Thursday's review with Marcus Vance (Squad 4), where he stumbled, and immediate fixes. |
| [`demo_script.md`](./demo_script.md) | **10-Minute Demo Script**: 4-part standard script clocked to 10 minutes with hostile question defenses. |

---

## 🛡️ Core Architectural Guardrails

1. **Version Resolution Before Retrieval**:
   The caller's version (`v2.4` or `v3.0`) is parsed before any retrieval call. Retrieval executes with strict metadata filtering (`filters={"sdk_version": caller_version_family}`). Version numbers are never treated as mere lexical words inside text.
2. **Clickable Versioned Citations**:
   Every citation explicitly names the SDK version: `[v2.4/v2/client_query.md#parameters]` or `[v3.0/v3/client_search.md#parameters]`. Citations omitting the version tag are rejected.
3. **Unasked Deprecation Surfacing**:
   When a caller inquires about a deprecated method, the engine automatically checks the deprecation registry and surfaces the notice, replacement symbol, and exact removal version (`v3.0.0`) unasked.
4. **Deterministic AST Code Validation Gate**:
   Emitted code samples are parsed via Python `ast` and verified against the caller version's symbol table. If code imports v3 modules in v2, calls removed methods, or omits mandatory arguments (e.g. `timeout` on `client.search`), the validation gate fails it deterministically.
5. **PII Redaction on Write**:
   Integrator API keys (`sk_live_...`, `AKIA...`) and database connection strings (`postgres://user:pass@host/db`) are sanitized immediately upon entering `DocsAgent.run()`, ensuring zero plaintext credentials hit disk logs or memory stores.
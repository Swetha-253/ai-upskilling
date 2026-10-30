# Week 12 Capstone Evaluation Benchmark Report (`eval_report.md`)

## 1. 📊 Benchmark Summary & Headline Telemetry

- **Total Test Cases ($n$)**: **30**
- **Test Suite Execution Duration**: **2.56 seconds**
- **Deterministic Assertion Pass Rate**: **30/30 (100.0%)**
- **Judge v2 Pass Rate**: **30/30 (100.0%)**
- **Judge Agreement Rate Against Human Ground-Truth Labels**: **30/30 (100.0%)** *(Requirement: Must clear 85%)*

---

## 2. 📋 Pass Rate Breakdown Per Taxonomy Failure Mode

| Failure Mode Name | Total Cases ($n$) | Assertion Pass | Judge v2 Pass | Pass Rate (%) | Primary Guardrail Enforced |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Cross-Version Code Hallucination** | 10 | 10 | 10 | **100.0%** | Metadata filter (`sdk_version == caller`) + AST Symbol Table check |
| **2. Unnoted Deprecation Omission** | 6 | 6 | 6 | **100.0%** | Unasked Deprecation Changelog lookup (`v3.0.0` removal version surfaced) |
| **3. Stack Overflow Dead-API Leakage** | 4 | 4 | 4 | **100.0%** | Dead API AST filter (`client.execute_query` prohibited in emitted code) |
| **4. Anchor Citation Drift** | 3 | 3 | 3 | **100.0%** | Structure-Aware Markdown Chunker + Clickable Versioned Citation Format |
| **5. Unwarranted Refusal on Valid Query** | 4 | 4 | 4 | **100.0%** | Version-scoped retrieval context injection |
| **6. Agent-MCP Version Desync (NEW)** | 3 | 3 | 3 | **100.0%** | Stdio IPC parameter normalization & tool argument verification |
| **TOTAL BENCHMARK** | **30** | **30** | **30** | **100.0%** | **Full 8-Assertion Deterministic Battery + Judge v2** |

---

## 3. 📈 The Number That Moved

> **Named Metric**: **Wrong-Version Code Sample Emission Rate**  
> **Definition**: The percentage of generated answers that contain Python code snippets importing or calling methods that do NOT exist or fail execution in the caller's active SDK version (e.g. emitting `client.search()` or `client.paginate()` to a v2.4 integrator, or omitting mandatory `timeout` in v3.0).

- **Sample Size ($n$)**: **25 cases (Baseline) → 30 cases (Integrated System)**
- **Before (Baseline System without Version Filtering & AST Symbol Check)**: **44.0%** (11 out of 25 answers emitted non-executable or wrong-version code samples).
- **After (Integrated System with Pinned Metadata Filtering + AST Symbol Assertion Gate)**: **0.0%** (0 out of 30 answers emitted wrong-version code).
- **Net Delta**: **-44.0 percentage points** reduction in breaking production code emissions.
- **Judge Agreement Rate on Integrated Outputs**: **100.0%** (30/30 agreement against human ground truth labels).

---

## 4. ⚠️ Explicit Statement of Non-Coverage (What the Suite Does NOT Measure)

To maintain absolute scientific and engineering integrity, the evaluation suite explicitly does **NOT** measure:

1. **Live Remote Network Transmission**: The suite validates local syntax parsing, OpenAPI schema compliance, and version symbol tables, but does **not** execute live HTTP/TLS socket roundtrips against the client's deployed production cloud API gateway.
2. **Polyglot SDK Runtimes Outside Python**: The suite deterministically validates Python AST parse trees and method signatures; it does **not** compile or type-check code snippets in Java, Go, C#, or TypeScript SDK bindings.
3. **Stateful WebSocket Packet Loss Degradation**: The suite validates that streaming connection parameters (e.g. `heartbeat_sec=15` on `StreamClient.connect`) match specification; it does **not** simulate network partition reconnections or TCP socket half-open recovery curves.
4. **Ad-Hoc Custom Monkey-Patching in Integrator Codebases**: The suite validates against official SDK public APIs; it cannot predict if an integrator has monkey-patched private internal SDK attributes (`_client_transport`).

# Trajectory Evaluation & Outcome-vs-Trajectory Gap Analysis (`trajectory_eval_integrated.md`)

## 1. 📊 Integrated Trajectory Telemetry Summary (10 Benchmark Cases)

| Metric Dimension | Baseline Agent (Unverified Retrieval) | Mitigated Integrated Agent (Guided Multi-Lap Workflow) | Delta / Trade-off |
| :--- | :---: | :---: | :---: |
| **Outcome Pass Rate (%)** | **100.0%** | **100.0%** | **0.0%** |
| **Trajectory Pass Rate (%)** | **60.0%** | **100.0%** | **+40.0%** |
| **Outcome-vs-Trajectory Gap** | **40.0%** | **0.0%** | **-40.0%** |
| **Tool-Choice Accuracy (%)** | **72.73%** | **100.0%** | **+27.27%** |
| **Argument Validity Rate (%)** | **97.33%** | **100.0%** | **+2.67%** |
| **Step Efficiency (Ratio)** | **1.064** | **1.000** | **-0.064** |
| **Cost Distribution (p50)** | **$0.001725** | **$0.001725** | **+$0.000000** |
| **Cost Distribution (Max Loop)**| **$0.001725** | **$0.001725** | **-$0.000000** |

---

## 2. 🚨 The Honest Gap: Exposing the False Positive Trace

> **The Outcome-vs-Trajectory Gap was 40.0%**.  
> The agent achieved a **100% Outcome Pass Rate** while failing **40% of its trajectory executions**. It gave superficially "correct" answers by reciting values memorized in training weights or system prompts, while completely bypassing schema and symbol verification tools!

### Verbatim False Positive Trace (`Q2`):
- **Query**: `"What is the default value of retry_backoff_ms in v3 Client.send?"`
- **Caller Version**: `v3.0`
- **Outcome Result**: **PASS** (Generated text correctly stated `500 milliseconds`).
- **Trajectory Result**: **FAIL** (Agent called `['search_docs']` only, bypassing `check_deprecation` and `check_symbol_exists` verification).
- **Execution Log Trace**:
  ```json
  {
    "question_id": "Q2",
    "passed": true,
    "trajectory_passed": false,
    "tool_calls": ["search_docs"],
    "failure_mode": "Tool-Choice Bypass (Reciting from Memory)"
  }
  ```
- **Why It Embarrasses Us**: Had the SDK engineering team shipped a patch altering the default backoff from 500ms to 250ms, the baseline agent would have continued reciting 500ms with 100% confidence because it never verified the active symbol table.

---

## 3. 🛠️ Targeted Mitigation & Zero Regression Verification

- **Mitigation**: Implemented **Guided Multi-Lap Workflow & Deterministic AST Symbol Assertion Gate**.
- **Trajectory Pass Rate**: Moved from **60.0% → 100.0%**.
- **Gap Elimination**: Moved from **40.0% → 0.0%**.
- **Measured Trade-offs**:
  - Added Latency Overhead: `+0.10 ms` (Local JSON-RPC IPC dispatch).
  - Token Overhead: `0.0 tokens` (Local deterministic tool execution).
  - Cost Delta Per Query: `+$0.000000`.

---

## 4. 📋 Per-Mode Trajectory Regression Matrix

| Failure Mode Name | Baseline Failures | Mitigated Failures | Status |
| :--- | :---: | :---: | :--- |
| **Tool-Choice Bypass (Reciting from Memory)** | 1 | 0 | **Eliminated** |
| **Argument Schema Hallucination** | 1 | 0 | **Eliminated** |
| **Step Loop Inefficiency (Unbounded Retries)** | 1 | 0 | **Eliminated** |
| **Legacy Unfiltered Retrieval & Refusal** | 1 | 0 | **Eliminated** |
| **Code Anchor Citation Misalignment** | 0 | 0 | **Zero / No Regression** |

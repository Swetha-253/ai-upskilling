# Failure Mode Taxonomy — Week 5 Error Analysis

| Failure Mode Name | Count | Freq % | Severity | Example Trace ID |
| :--- | :---: | :---: | :--- | :---: |
| **Retrieves legacy v2 SDK chunks for v3 queries and returns forced refusal** | 9 | 45% | Merely annoys the reader | `trace_0187` |
| **Returns forced refusal on valid v3 queries despite retrieving relevant v3 chunks** | 4 | 20% | Merely annoys the reader | `trace_0032` |
| **Cites code-example anchor chunk instead of parameters reference section** | 4 | 20% | Merely annoys the reader | `trace_0279` |
| **Outputs v3 default value while attaching legacy v2 chunk citation** | 2 | 10% | Ships broken code to a user's repo | `trace_0919` |
| **Answers a specific parameter property query with details for a different parameter** | 1 | 5% | Ships broken code to a user's repo | `trace_0179` |

---

## 📌 Summary & Executive Takeaway

In a seeded random sample of 20 production traces (Seed: `20260911`), **55% of failure instances** (11 out of 20) stem directly from **unfiltered retrieval mixing legacy v2 documentation with v3 SDK docs** (where legacy `v2_client_send` outranks `v3_client_send`). 

Attacking this single retrieval filtering bug next week will eliminate **Mode 1** (45%) and **Mode 4** (10%), immediately reducing overall production failure rate by **55%**.

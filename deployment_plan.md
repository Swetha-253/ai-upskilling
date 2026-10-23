# Production Deployment Safety & Rollback Plan

## 1. Prompt Version Bump Record

- **Previous Production Version**: `v1.0.0` (Unfiltered retrieval context; no cross-version citation validation)
- **New Production Version**: `v1.1.0` (Enforced metadata version filtering `version='v3'`; explicit cross-version citation isolation instructions)
- **Semantic Diff**: Eliminates legacy `v2_*` chunk citations on v3 queries, resolving the "Confidently, Faithfully Wrong" failure mode.

---

## 2. Concise Two-Line Canary Deployment & Rollback Strategy

1. **Canary Deployment**: Route 5% of production traffic to prompt/retrieval version `v1.1.0` while monitoring the cross-version citation error metric and p99 latency for 15 minutes before progressively ramping to 25%, 50%, and 100%.
2. **Rollback Strategy**: If the cross-version citation error rate exceeds 0.01% or p99 latency spikes beyond 1.5s in the canary cohort, instantly toggle the runtime feature flag back to `v1.0.0` with zero container redeployments.

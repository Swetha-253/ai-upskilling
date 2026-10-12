# Failure Injection & Resilience Check — Injected Worker HTTP 500

## 1. Experiment Setup & Failure Injected

- **Target Evaluation Case**: **Q8** (`"Migrate code using v2 request_body on Client.send to v3. Is request_body supported in v3?"`)
- **Target Specialist Worker**: `VersionDeprecationWorker` (`version_worker`)
- **Injected Failure Mode**: Simulated upstream HTTP 500 Internal Server Error (`HTTP 500: Deprecation registry service unavailable at /v3/registry/deprecations`).
- **Simulated Condition**: Upstream deprecation metadata database outage / network timeout.

---

## 2. Orchestrator Response & Behavioral Audit

| Behavioral Question | Observed Orchestrator Action | Audit Verdict & Evidence |
| :--- | :--- | :--- |
| **Did it retry the request?** | **YES** — Executed **3 total attempts** (Initial dispatch + 2 exponential backoff retries at 1ms, 2ms intervals). | **Verified**: Max retries limit (`max_retries=2`) prevented infinite loop cascades. |
| **Did it degrade gracefully?** | **YES** — Upon retry exhaustion, transitioned to **Graceful Degradation Mode**. Produced a partial answer utilizing the available OpenAPI v3 endpoint schema while explicitly attaching a prominent degradation header. | **Verified**: Downstream synthesis proceeded with defensive scoping instead of unhandled exception crash. |
| **Did it hallucinate or lie?** | **NO** — Explicitly declared that parameter deprecation status for `request_body` could **not** be verified due to the registry 500 error. Did **not** fabricate a false confirmation. | **Verified**: Refused to lie about version safety. |

---

## 3. Verbatim Execution Trace & Generated Output

### Orchestrator Console & Log Excerpt:
```text
[WARN] [HOP 1] VersionDeprecationWorker failed with HTTP 500 Internal Server Error.
[INFO] Orchestrator initiating Retry 1 of 2 after exponential backoff delay...
[WARN] [HOP 1] Retry 1 failed with HTTP 500 Internal Server Error.
[INFO] Orchestrator initiating Retry 2 of 2 after exponential backoff delay...
[WARN] [HOP 1] Retry 2 failed with HTTP 500 Internal Server Error. Max retries (2) exhausted.
[INFO] Orchestrator activating GRACEFUL DEGRADATION POLICY: Proceeding to CodeSampleWorker with unverified version warning flag.
[INFO] [HOP 3] Context Re-Send dispatching to CodeSampleWorker (degradation_mode=True).
[INFO] [HOP 5] Final synthesis generating partial response with prominent degradation warning disclaimer.
```

### Generated Assistant Answer:
```markdown
[GRACEFUL DEGRADATION NOTICE: Deprecation Service returned HTTP 500 Internal Server Error. Could not verify deprecation status for 'request_body'.]
Partial Answer grounded in active OpenAPI v3 spec for endpoint `/v3/client/send`:
```python
from sdk.v3 import Client
client = Client()
res = client.send(payload={'action': 'test'}, retry_backoff_ms=500, enable_compression=True)
```
Caution: Parameter compatibility between v2 and v3 could not be verified by the deprecation registry.
```

---

## 4. Architectural Resilience Verdict

When an isolated specialist worker fails in a multi-agent system:
1. **Unbounded Hand-offs Threat**: Without strict retry limits and timeout policies, worker failures cause cascading thread deadlocks.
2. **Hallucination Risk**: A naive orchestrator would have concealed the worker failure and shipped hallucinated migration advice, potentially breaking production client code.
3. **Graceful Degradation Requirement**: The orchestrator must separate what it knows (OpenAPI schema from `CodeSampleWorker`) from what it failed to verify (`VersionDeprecationWorker`), communicating partial truth transparently to the user.

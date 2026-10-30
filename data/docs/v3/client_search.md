# Client.search Method Reference

The `Client.search()` method executes search queries against the v3 search gateway.

> [!IMPORTANT]
> **Breaking Change from v2**:
> In SDK v3.0, the legacy method `Client.query()` has been permanently **REMOVED**.
> Callers must update their code to call `Client.search()`.
> In addition, the `timeout` parameter is now **mandatory** (required) on all search invocations. Calling `client.search()` without a `timeout` argument will fail validation.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| query | str | N/A | True | Search query expression. |
| timeout | float | 10.0 | True | **MANDATORY**: Network timeout deadline in seconds (e.g. 10.0). |

## Code Example

```python
from sdk import Client

client = Client(api_key="sk_live_v3_ready")
results = client.search(query="SELECT * FROM events", timeout=10.0)
print("Search hits:", len(results))
```

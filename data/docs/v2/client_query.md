# Client.query Method Reference (v2 SDK Legacy)

The `Client.query()` method in v2 SDK executes query expressions against the data engine with optional connection timeout.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| query | str | N/A | True | The query string expression to execute against the database. |
| timeout | float | None | False | Optional connection timeout in seconds. If omitted, uses default client timeout. |

## Deprecation Notice

> [!WARNING]
> `Client.query()` was deprecated in SDK version 2.4.0 and is **REMOVED** in SDK version 3.0.0.
> In v3.0, use `Client.search(query=..., timeout=10.0)`. Note that `timeout` is now **mandatory** in v3.0.

## Code Example

```python
from sdk_v2 import Client

client = Client()
results = client.query("SELECT * FROM metrics WHERE service = 'analytics'")
print(results)
```

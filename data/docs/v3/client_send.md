# Client.send Method Reference

The `Client.send()` method submits a payload request to the SDK gateway asynchronously with retry mechanisms and rate limiting handling.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| payload | dict | N/A | True | The data object payload to transmit to the API endpoint. |
| retry_backoff_ms | int | 500 | False | Exponential backoff delay between retry attempts in milliseconds. |
| idempotency_key | str | None | False | Unique identifier to prevent duplicate request execution. |
| enable_compression | bool | True | False | Enables gzip compression on request body payloads. |

## Response Format

Returns a `Response` object containing the HTTP status code and parsed JSON data payload.

## Code Example

```python
from sdk import Client

client = Client(api_key="sk_live_12345")
response = client.send(
    payload={"query": "analytics"},
    retry_backoff_ms=500,
    idempotency_key="req_unique_99",
    enable_compression=True
)
print(response.status_code)
```

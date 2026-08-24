# Client.send Method Reference (v2 SDK Legacy)

The `Client.send()` method in v2 SDK handles outgoing HTTP network requests and default retry backoff delay configuration.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| request_body | dict | N/A | True | The JSON request body dictionary sent to server. |
| retry_backoff_ms | int | 1000 | False | Default retry backoff delay milliseconds for Client.send retry requests in v2 SDK. |
| timeout | float | 10.0 | False | Connection timeout limit. |

## Overview of Default Retry Backoff Delay in Client.send

In v2 SDK, the default retry backoff delay when sending client requests with `Client.send()` was 1000 milliseconds. Note that in v3 SDK this default was changed to 500 milliseconds.

## Code Example

```python
from sdk_v2 import Client

client = Client()
client.send(request_body={"data": "test"}, retry_backoff_ms=1000)
```

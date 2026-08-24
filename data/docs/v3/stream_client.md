# StreamClient.connect Method Reference

The `StreamClient.connect()` method establishes a persistent WebSocket connection to stream real-time data events from the server.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| endpoint_url | str | N/A | True | The WebSocket stream target URL. |
| connection_timeout | float | 30.0 | False | Time in seconds to wait for initial WebSocket handshake before failing. |
| heartbeat_interval | int | 15 | False | Frequency of ping heartbeats sent to maintain stream alive status. |
| auto_reconnect | bool | True | False | Automatically attempt reconnection upon disconnection. |

## Response Format

Returns a `StreamConnection` context manager yieldable for listening to event streams.

## Code Example

```python
from sdk import StreamClient

client = StreamClient(api_key="sk_live_12345")
with client.connect(
    endpoint_url="wss://stream.example.com/v3/events",
    connection_timeout=30.0,
    heartbeat_interval=15
) as stream:
    for event in stream.listen():
        print(event.data)
```

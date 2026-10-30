# Tag: v3.0 - Client Send with Payload
from sdk import Client
client = Client()
res = client.send(payload={'batch_id': 57}, retry_backoff_ms=500, enable_compression=True)
print(res)

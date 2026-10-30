# Tag: v2.4 - Client Send with Request Body
from sdk_v2 import Client
client = Client()
res = client.send(request_body={'batch_id': 58}, retry_backoff_ms=1000)
print(res)

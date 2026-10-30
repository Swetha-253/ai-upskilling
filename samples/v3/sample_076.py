# Tag: v3.0 - Search with Mandatory Timeout
from sdk import Client
client = Client()
res = client.search(query='SELECT * FROM data_76', timeout=10.0)
print(res)

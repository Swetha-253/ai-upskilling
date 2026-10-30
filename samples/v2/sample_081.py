# Tag: v2.4 - Query Execution
from sdk_v2 import Client
client = Client()
res = client.query('SELECT * FROM data_81')
print(res)

# Tag: v2.4 - Cursor Pagination
from sdk_v2 import Client
client = Client()
page = client.query_paginated(cursor='cur_67', limit=50)
print(page)

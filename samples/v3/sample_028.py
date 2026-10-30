# Tag: v3.0 - Asynchronous Pagination
from sdk import Client
client = Client()
page = client.paginate(page_size=100, cursor='cur_28')
print(page)

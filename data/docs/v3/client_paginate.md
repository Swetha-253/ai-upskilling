# Client.paginate Method Reference

The `Client.paginate()` method in v3 SDK replaces the legacy `client.query_paginated()` method, providing asynchronous cursor pagination.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| page_size | int | 100 | False | Page size limit for results (default: 100). |
| cursor | str | None | False | Opaque cursor token from the previous page response. |

## Code Example

```python
from sdk import Client

client = Client()
pager = client.paginate(page_size=100, cursor=None)
for item in pager.items:
    print(item)
```

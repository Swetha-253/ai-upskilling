# Client.query_paginated Method Reference (v2 SDK Legacy)

The `Client.query_paginated()` method in v2 SDK performs cursor-based pagination over large result sets.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| cursor | str | None | False | Opaque pagination cursor token returned from previous page. |
| limit | int | 50 | False | Maximum number of records to return per page (default 50). |

## Deprecation Notice

> [!WARNING]
> `Client.query_paginated()` was deprecated in SDK version 2.4.0 and is **REMOVED** in SDK version 3.0.0.
> In v3.0, use `Client.paginate(page_size=..., cursor=...)`.

## Code Example

```python
from sdk_v2 import Client

client = Client()
page = client.query_paginated(cursor=None, limit=50)
for record in page.items:
    print(record.id)
```

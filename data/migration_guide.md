# SDK v2 to v3 Migration Guide

This guide details all breaking changes, renamed methods, parameter changes, and removed symbols when migrating from SDK v2.x to SDK v3.0.

---

## 1. Summary of Breaking Changes

| v2.x Method / Symbol | v3.0 Replacement | Nature of Breaking Change |
| :--- | :--- | :--- |
| `client.query(query, timeout=None)` | `client.search(query, timeout=10.0)` | **Renamed & Removed**. Method `query()` no longer exists in v3.0. `timeout` is now **mandatory**. |
| `client.send(request_body=...)` | `client.send(payload=...)` | **Parameter Renamed**. `request_body` removed, replaced by `payload`. Default backoff reduced from 1000ms to 500ms. |
| `client.query_paginated()` | `client.paginate(page_size=..., cursor=...)` | **Replaced**. Cursor parameter signature updated. |
| `Auth.login(old_ttl=...)` | `Auth.login(token_ttl=...)` | **Parameter Renamed**. `old_ttl` removed, replaced by `token_ttl` (in seconds). |
| `Auth.old_token_renew(token)` | `Auth.refresh_token(refresh_token=...)` | **Removed**. Method `old_token_renew()` no longer exists. Use `refresh_token()`. |
| `/v2/legacy/batch` | `/v3/batch/process` | **Endpoint Removed**. Synchronous batch endpoint removed in favor of `BatchProcessor.process()`. |

---

## 2. Detailed Code Migrations

### Migration 1: `client.query()` to `client.search()`

**Legacy v2 Code (Fails in v3):**
```python
from sdk_v2 import Client

client = Client()
# Fails in v3 with AttributeError: 'Client' object has no attribute 'query'
results = client.query("SELECT * FROM users")
```

**v3.0 Replacement Code:**
```python
from sdk import Client

client = Client()
# Mandatory timeout parameter must be supplied!
results = client.search(query="SELECT * FROM users", timeout=10.0)
```

---

### Migration 2: `client.send()` Parameter Update

**Legacy v2 Code (Fails in v3):**
```python
from sdk_v2 import Client

client = Client()
# Fails in v3 with TypeError: unexpected keyword argument 'request_body'
client.send(request_body={"event": "signup"}, retry_backoff_ms=1000)
```

**v3.0 Replacement Code:**
```python
from sdk import Client

client = Client()
# Use payload and note 500ms default retry backoff
client.send(payload={"event": "signup"}, retry_backoff_ms=500, enable_compression=True)
```

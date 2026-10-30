# SDK CHANGELOG

## [3.0.0] - 2025-01-15

### Breaking Changes & Removals
- **REMOVED**: `client.query()` has been removed. Use `client.search(query=..., timeout=10.0)`. Note that `timeout` is now **mandatory**.
- **REMOVED**: `request_body` parameter on `client.send()` has been removed. Use `payload`.
- **REMOVED**: `old_ttl` parameter on `Auth.login()` has been removed. Use `token_ttl`.
- **REMOVED**: `Auth.old_token_renew()` has been removed. Use `Auth.refresh_token(refresh_token=...)`.
- **REMOVED**: `client.query_paginated()` has been removed. Use `client.paginate(page_size=..., cursor=...)`.
- **REMOVED**: Legacy endpoint `/v2/legacy/batch` removed in favor of `/v3/batch/process`.

### Changed
- `client.send()`: Default `retry_backoff_ms` changed from `1000` to `500`. Added `enable_compression` (default `True`).

---

## [2.4.0] - 2024-06-10

### Deprecations
- **DEPRECATED**: `client.query()` is deprecated. Removal version: **v3.0.0**. Replaced by `client.search()`.
- **DEPRECATED**: `request_body` on `client.send()` is deprecated. Removal version: **v3.0.0**. Replaced by `payload`.
- **DEPRECATED**: `old_ttl` on `Auth.login()` is deprecated. Removal version: **v3.0.0**. Replaced by `token_ttl`.
- **DEPRECATED**: `Auth.old_token_renew()` is deprecated. Removal version: **v3.0.0**. Replaced by `Auth.refresh_token()`.
- **DEPRECATED**: `client.query_paginated()` is deprecated. Removal version: **v3.0.0**. Replaced by `client.paginate()`.

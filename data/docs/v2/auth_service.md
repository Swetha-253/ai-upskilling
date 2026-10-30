# Auth API Reference (v2 SDK Legacy)

The `Auth` service in v2 SDK manages session authentication and credential exchange.

## Auth.login Method

Authenticates account credentials and issues authentication tokens.

### Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| username | str | N/A | True | Account login identifier. |
| password | str | N/A | True | Account password. |
| old_ttl | int | 7200 | False | Token expiration lifespan in seconds. |

### Deprecation Notice

> [!WARNING]
> Parameter `old_ttl` was deprecated in v2.4.0 and is **REMOVED** in v3.0.0. In v3.0, use `token_ttl`.
> Method `Auth.old_token_renew()` is deprecated and removed in v3.0.0. In v3.0, use `Auth.refresh_token()`.

### Code Example

```python
from sdk_v2 import Auth

auth = Auth()
token = auth.login(username="dev_user", password="secret_password", old_ttl=7200)
print(token.access_token)
```

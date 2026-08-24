# Auth API Reference

The `Auth` service handles user authentication, session token issuance, and token renewal.

## Auth.login Method

Authenticates credentials and issues access tokens.

### Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| username | str | N/A | True | User login account name or email address. |
| password | str | N/A | True | Account password string. |
| token_ttl | int | 3600 | False | Token time-to-live expiration period in seconds. |

### Response Format

Returns an `AuthToken` object containing `access_token` and `expires_in`.

### Code Example

```python
from sdk import Auth

auth = Auth()
token_info = auth.login(
    username="user@example.com",
    password="secret_password",
    token_ttl=3600
)
print("Access token:", token_info.access_token)
```

## Auth.refresh_token Method

Refreshes an existing expired session token.

### Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| refresh_token | str | N/A | True | Valid refresh token string obtained during initial authentication. |

### Response Format

Returns a refreshed `AuthToken` instance.

### Code Example

```python
new_token = auth.refresh_token(refresh_token="ref_abc123xyz")
print("Refreshed token expiry:", new_token.expires_in)
```

# Webhook.verify_signature Method Reference

The `Webhook.verify_signature()` method validates cryptographic signature headers attached to incoming HTTP webhook notifications.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| raw_body | bytes | N/A | True | Unparsed raw request body bytes. |
| signature_header | str | "X-Signature-256" | True | Header name containing the HMAC-SHA256 signature hash. |
| secret_key | str | N/A | True | Shared secret key for verifying signature validity. |
| tolerance_sec | int | 300 | False | Maximum allowed timestamp drift in seconds to prevent replay attacks. |

## Response Format

Returns a boolean `True` if signature verification succeeds, or raises `SignatureValidationError`.

## Code Example

```python
from sdk import Webhook

is_valid = Webhook.verify_signature(
    raw_body=b'{"event":"user.created"}',
    signature_header="X-Signature-256",
    secret_key="whsec_secret123",
    tolerance_sec=300
)
print("Signature valid:", is_valid)
```

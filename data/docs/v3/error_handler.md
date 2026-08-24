# ErrorHandler.handle Method Reference

The `ErrorHandler.handle()` method intercepts SDK runtime exceptions, logging error telemetry and applying configurable fallback policies.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| exception | Exception | N/A | True | The raised python exception object caught during SDK operations. |
| max_retries | int | 3 | False | Maximum retry attempts to execute before invoking error fallback handlers. |
| fallback_mode | str | "raise" | False | Action to take when retries exhaust ("raise", "ignore", or "cached"). |

## Response Format

Returns fallback result data or re-raises the original exception depending on configuration.

## Code Example

```python
from sdk import ErrorHandler

try:
    # operation
    pass
except Exception as err:
    res = ErrorHandler.handle(
        exception=err,
        max_retries=3,
        fallback_mode="raise"
    )
```

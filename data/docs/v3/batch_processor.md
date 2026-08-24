# BatchProcessor.process Method Reference

The `BatchProcessor.process()` method processes a list of item payloads in batches to optimize network throughput and reduce API call overhead.

## Parameters

| Name | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| items | list | N/A | True | List of item dictionaries to process in batch mode. |
| max_batch_size | int | 100 | False | Maximum number of items bundled into a single network request. |
| timeout_sec | float | 60.0 | False | Overall processing timeout limit in seconds. |
| concurrency | int | 4 | False | Number of parallel worker threads handling batches. |

## Response Format

Returns a `BatchResult` object detailing total successful records, failed records, and error traces.

## Code Example

```python
from sdk import BatchProcessor

processor = BatchProcessor(api_key="sk_live_12345")
results = processor.process(
    items=[{"id": 1}, {"id": 2}, {"id": 3}],
    max_batch_size=100,
    timeout_sec=60.0,
    concurrency=4
)
print(f"Processed {results.success_count} items")
```

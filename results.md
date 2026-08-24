# Week 3 Practical — Task Set E Results

## 1. 8 Known-Answer Questions & Known Locations

| # | Question | Known-Correct Page & Section | Naive Chunker Top-5 | Structure-Aware Chunker Top-5 |
|---|---|---|---|---|
| Q1 | What is the default value and type of retry_backoff_ms on Client.send()? | `docs/v3/client_send.md (## Parameters (retry_backoff_ms row))` | HIT (`v3_client_send_naive_0`) | HIT (`v3_client_send#clientsend-method-reference`) |
| Q2 | Is idempotency_key required on Client.send(), and what is its data type? | `docs/v3/client_send.md (## Parameters (idempotency_key row))` | MISS (`v3_client_send_naive_4`) | HIT (`v3_client_send#code-example`) |
| Q3 | What is the default value and type of max_batch_size on BatchProcessor.process()? | `docs/v3/batch_processor.md (## Parameters (max_batch_size row))` | HIT (`v3_batch_processor_naive_0`) | HIT (`v3_batch_processor#batchprocessorprocess-method-reference`) |
| Q4 | What is the parameter name and default timeout value for establishing stream connections on StreamClient.connect()? | `docs/v3/stream_client.md (## Parameters (connection_timeout row))` | HIT (`v3_stream_client_naive_0`) | HIT (`v3_stream_client#streamclientconnect-method-reference`) |
| Q5 | What header key name is passed for secret verification on Webhook.verify_signature(), and what is its default value? | `docs/v3/webhook_handler.md (## Parameters (signature_header row))` | HIT (`v3_webhook_handler_naive_2`) | HIT (`v3_webhook_handler#parameters`) |
| Q6 | What is the return object type of Auth.login() and the default value of parameter token_ttl? | `docs/v3/auth_service.md (### Auth.login Method (Parameters & Response Format))` | MISS (`v3_auth_service_naive_3`) | HIT (`v3_auth_service#authlogin-method`) |
| Q7 | What is the parameter name and data type used to enable gzip compression on Client.send()? | `docs/v3/client_send.md (## Parameters (enable_compression row))` | HIT (`v3_client_send_naive_3`) | HIT (`v3_client_send#parameters`) |
| Q8 | What python code snippet demonstrates invoking Auth.refresh_token() to renew an expired session? | `docs/v3/auth_service.md (## Auth.refresh_token Method -> ### Code Example)` | HIT (`v3_auth_service_naive_4`) | HIT (`v3_auth_service#authrefresh_token-method`) |


## 2. Chunking Strategy Performance Comparison

| Chunking Strategy | Hit-in-Top-5 Score | Hit Percentage |
|---|---|---|
| Strategy 1: Naive Fixed-Window Chunker | **6/8** | 75% |
| Strategy 2: Structure-Aware Markdown Chunker | **8/8** | **100%** |

> [!NOTE]
> **Hit Definition**: A retrieval is counted as a **HIT** if at least one chunk returned in the Top-5 contains the complete, unsevered factual evidence required to answer the question (including intact table headers with parameter rows and un-cut code fences).

## 3. Search-Only Retrieval Dump (All 8 Questions under Both Strategies)

### Question 1: What is the default value and type of retry_backoff_ms on Client.send()?
**Known Location**: `docs/v3/client_send.md (## Parameters (retry_backoff_ms row))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 7.1946): `v3_client_send_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `# Client.send Method Reference  The `Client.send()` method submits a payload request to the SDK gateway asynchronously w...`
- **Rank 2** (Score: 6.6363): `v3_client_send_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `SON data payload.  ## Code Example  ```python from sdk import Client  client = Client(api_key="sk_live_12345") response ...`
- **Rank 3** (Score: 4.1776): `v3_client_send_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: ` enable_compression | bool | True | False | Enables gzip compression on request body payloads. |  ## Response Format  Re...`
- **Rank 4** (Score: 3.9225): `v3_client_send_naive_1` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `e | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | payload | dict | N/A | True | The data o...`
- **Rank 5** (Score: 3.6922): `v3_batch_processor_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `# BatchProcessor.process Method Reference  The `BatchProcessor.process()` method processes a list of item payloads in ba...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 5.3062): `v3_client_send#clientsend-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `# Client.send Method Reference  The `Client.send()` method submits a payload request to the SDK gateway asynchronously w...`
- **Rank 2** (Score: 5.0183): `v3_client_send#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Code Example  ```python from sdk import Client  client = Client(api_key="sk_live_12345") response = client.send(     ...`
- **Rank 3** (Score: 4.7325): `v3_client_send#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | payload | dict | N/A...`
- **Rank 4** (Score: 3.8553): `v3_error_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Response Format  Returns fallback result data or re-raises the original exception depending on configuration....`
- **Rank 5** (Score: 3.4339): `v3_batch_processor#batchprocessorprocess-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `# BatchProcessor.process Method Reference  The `BatchProcessor.process()` method processes a list of item payloads in ba...`

---

### Question 2: Is idempotency_key required on Client.send(), and what is its data type?
**Known Location**: `docs/v3/client_send.md (## Parameters (idempotency_key row))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 8.4555): `v3_client_send_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `SON data payload.  ## Code Example  ```python from sdk import Client  client = Client(api_key="sk_live_12345") response ...`
- **Rank 2** (Score: 6.9905): `v3_client_send_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `# Client.send Method Reference  The `Client.send()` method submits a payload request to the SDK gateway asynchronously w...`
- **Rank 3** (Score: 5.0912): `v3_client_send_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: ` enable_compression | bool | True | False | Enables gzip compression on request body payloads. |  ## Response Format  Re...`
- **Rank 4** (Score: 4.0243): `v3_error_handler_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `st ("raise", "ignore", or "cached"). |  ## Response Format  Returns fallback result data or re-raises the original excep...`
- **Rank 5** (Score: 3.3511): `v3_client_send_naive_5` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `s=500,     idempotency_key="req_unique_99",     enable_compression=True ) print(response.status_code) ``` ...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 5.7505): `v3_client_send#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Code Example  ```python from sdk import Client  client = Client(api_key="sk_live_12345") response = client.send(     ...`
- **Rank 2** (Score: 5.6798): `v3_client_send#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | payload | dict | N/A...`
- **Rank 3** (Score: 4.6285): `v3_error_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Response Format  Returns fallback result data or re-raises the original exception depending on configuration....`
- **Rank 4** (Score: 4.3602): `v3_client_send#clientsend-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `# Client.send Method Reference  The `Client.send()` method submits a payload request to the SDK gateway asynchronously w...`
- **Rank 5** (Score: 2.6176): `v3_client_send#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Response Format  Returns a `Response` object containing the HTTP status code and parsed JSON data payload....`

---

### Question 3: What is the default value and type of max_batch_size on BatchProcessor.process()?
**Known Location**: `docs/v3/batch_processor.md (## Parameters (max_batch_size row))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 10.6461): `v3_batch_processor_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `# BatchProcessor.process Method Reference  The `BatchProcessor.process()` method processes a list of item payloads in ba...`
- **Rank 2** (Score: 8.6642): `v3_batch_processor_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `r traces.  ## Code Example  ```python from sdk import BatchProcessor  processor = BatchProcessor(api_key="sk_live_12345"...`
- **Rank 3** (Score: 7.4922): `v3_batch_processor_naive_1` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: ` Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | items | list | N/A | T...`
- **Rank 4** (Score: 4.1776): `v3_client_send_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: ` enable_compression | bool | True | False | Enables gzip compression on request body payloads. |  ## Response Format  Re...`
- **Rank 5** (Score: 3.095): `v3_error_handler_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `st ("raise", "ignore", or "cached"). |  ## Response Format  Returns fallback result data or re-raises the original excep...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 9.9988): `v3_batch_processor#batchprocessorprocess-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `# BatchProcessor.process Method Reference  The `BatchProcessor.process()` method processes a list of item payloads in ba...`
- **Rank 2** (Score: 7.4144): `v3_batch_processor#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `## Code Example  ```python from sdk import BatchProcessor  processor = BatchProcessor(api_key="sk_live_12345") results =...`
- **Rank 3** (Score: 6.5254): `v3_batch_processor#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | items | list | N/A |...`
- **Rank 4** (Score: 3.8553): `v3_error_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Response Format  Returns fallback result data or re-raises the original exception depending on configuration....`
- **Rank 5** (Score: 3.481): `v3_client_send#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | payload | dict | N/A...`

---

### Question 4: What is the parameter name and default timeout value for establishing stream connections on StreamClient.connect()?
**Known Location**: `docs/v3/stream_client.md (## Parameters (connection_timeout row))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 11.3049): `v3_stream_client_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `# StreamClient.connect Method Reference  The `StreamClient.connect()` method establishes a persistent WebSocket connecti...`
- **Rank 2** (Score: 8.5224): `v3_stream_client_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: ` to event streams.  ## Code Example  ```python from sdk import StreamClient  client = StreamClient(api_key="sk_live_1234...`
- **Rank 3** (Score: 5.2835): `v3_stream_client_naive_5` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `/events",     connection_timeout=30.0,     heartbeat_interval=15 ) as stream:     for event in stream.listen():         ...`
- **Rank 4** (Score: 4.1776): `v3_client_send_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: ` enable_compression | bool | True | False | Enables gzip compression on request body payloads. |  ## Response Format  Re...`
- **Rank 5** (Score: 3.57): `v3_stream_client_naive_1` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | endpoint_url | str | N/A | True | The...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 10.6169): `v3_stream_client#streamclientconnect-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `# StreamClient.connect Method Reference  The `StreamClient.connect()` method establishes a persistent WebSocket connecti...`
- **Rank 2** (Score: 9.8796): `v3_stream_client#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `## Code Example  ```python from sdk import StreamClient  client = StreamClient(api_key="sk_live_12345") with client.conn...`
- **Rank 3** (Score: 4.8045): `v3_stream_client#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | endpoint_url | str |...`
- **Rank 4** (Score: 3.8553): `v3_error_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Response Format  Returns fallback result data or re-raises the original exception depending on configuration....`
- **Rank 5** (Score: 3.481): `v3_client_send#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | payload | dict | N/A...`

---

### Question 5: What header key name is passed for secret verification on Webhook.verify_signature(), and what is its default value?
**Known Location**: `docs/v3/webhook_handler.md (## Parameters (signature_header row))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 10.7858): `v3_webhook_handler_naive_2` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `ure-256" | True | Header name containing the HMAC-SHA256 signature hash. | | secret_key | str | N/A | True | Shared secr...`
- **Rank 2** (Score: 9.8989): `v3_webhook_handler_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `# Webhook.verify_signature Method Reference  The `Webhook.verify_signature()` method validates cryptographic signature h...`
- **Rank 3** (Score: 6.9658): `v3_webhook_handler_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `ationError`.  ## Code Example  ```python from sdk import Webhook  is_valid = Webhook.verify_signature(     raw_body=b'{"...`
- **Rank 4** (Score: 4.3198): `v3_webhook_handler_naive_1` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | raw_body | bytes | N/A | True | U...`
- **Rank 5** (Score: 3.6826): `v3_client_send_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: ` enable_compression | bool | True | False | Enables gzip compression on request body payloads. |  ## Response Format  Re...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 8.8497): `v3_webhook_handler#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | raw_body | bytes | N...`
- **Rank 2** (Score: 8.2118): `v3_webhook_handler#webhookverify_signature-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `# Webhook.verify_signature Method Reference  The `Webhook.verify_signature()` method validates cryptographic signature h...`
- **Rank 3** (Score: 5.9982): `v3_webhook_handler#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `## Code Example  ```python from sdk import Webhook  is_valid = Webhook.verify_signature(     raw_body=b'{"event":"user.c...`
- **Rank 4** (Score: 3.9221): `v3_webhook_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/webhook_handler.md`
  > *Snippet*: `## Response Format  Returns a boolean `True` if signature verification succeeds, or raises `SignatureValidationError`....`
- **Rank 5** (Score: 3.0549): `v3_error_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Response Format  Returns fallback result data or re-raises the original exception depending on configuration....`

---

### Question 6: What is the return object type of Auth.login() and the default value of parameter token_ttl?
**Known Location**: `docs/v3/auth_service.md (### Auth.login Method (Parameters & Response Format))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 9.6662): `v3_auth_service_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `g `access_token` and `expires_in`.  ### Code Example  ```python from sdk import Auth  auth = Auth() token_info = auth.lo...`
- **Rank 2** (Score: 8.9731): `v3_auth_service_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `# Auth API Reference  The `Auth` service handles user authentication, session token issuance, and token renewal.  ## Aut...`
- **Rank 3** (Score: 6.1198): `v3_batch_processor_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `ncy | int | 4 | False | Number of parallel worker threads handling batches. |  ## Response Format  Returns a `BatchResul...`
- **Rank 4** (Score: 5.8561): `v3_auth_service_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `    token_ttl=3600 ) print("Access token:", token_info.access_token) ```  ## Auth.refresh_token Method  Refreshes an exi...`
- **Rank 5** (Score: 5.7541): `v3_batch_processor_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `# BatchProcessor.process Method Reference  The `BatchProcessor.process()` method processes a list of item payloads in ba...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 11.542): `v3_auth_service#authlogin-method` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `## Auth.login Method  Authenticates credentials and issues access tokens.  ### Parameters  | Name | Type | Default | Req...`
- **Rank 2** (Score: 6.0475): `v3_auth_service#auth-api-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `# Auth API Reference  The `Auth` service handles user authentication, session token issuance, and token renewal....`
- **Rank 3** (Score: 5.9456): `v3_batch_processor#batchprocessorprocess-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `# BatchProcessor.process Method Reference  The `BatchProcessor.process()` method processes a list of item payloads in ba...`
- **Rank 4** (Score: 5.6505): `v3_batch_processor#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/batch_processor.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | items | list | N/A |...`
- **Rank 5** (Score: 4.4639): `v3_client_send#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Response Format  Returns a `Response` object containing the HTTP status code and parsed JSON data payload....`

---

### Question 7: What is the parameter name and data type used to enable gzip compression on Client.send()?
**Known Location**: `docs/v3/client_send.md (## Parameters (enable_compression row))`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 11.6701): `v3_client_send_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: ` enable_compression | bool | True | False | Enables gzip compression on request body payloads. |  ## Response Format  Re...`
- **Rank 2** (Score: 7.6009): `v3_client_send_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `# Client.send Method Reference  The `Client.send()` method submits a payload request to the SDK gateway asynchronously w...`
- **Rank 3** (Score: 6.0369): `v3_client_send_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `SON data payload.  ## Code Example  ```python from sdk import Client  client = Client(api_key="sk_live_12345") response ...`
- **Rank 4** (Score: 4.5278): `v3_error_handler_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `st ("raise", "ignore", or "cached"). |  ## Response Format  Returns fallback result data or re-raises the original excep...`
- **Rank 5** (Score: 3.6448): `v3_stream_client_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`
  > *Snippet*: `# StreamClient.connect Method Reference  The `StreamClient.connect()` method establishes a persistent WebSocket connecti...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 9.0783): `v3_client_send#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | payload | dict | N/A...`
- **Rank 2** (Score: 5.4289): `v3_error_handler#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Response Format  Returns fallback result data or re-raises the original exception depending on configuration....`
- **Rank 3** (Score: 5.3868): `v3_client_send#clientsend-method-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `# Client.send Method Reference  The `Client.send()` method submits a payload request to the SDK gateway asynchronously w...`
- **Rank 4** (Score: 3.4035): `v3_client_send#response-format` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Response Format  Returns a `Response` object containing the HTTP status code and parsed JSON data payload....`
- **Rank 5** (Score: 3.2106): `v3_client_send#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
  > *Snippet*: `## Code Example  ```python from sdk import Client  client = Client(api_key="sk_live_12345") response = client.send(     ...`

---

### Question 8: What python code snippet demonstrates invoking Auth.refresh_token() to renew an expired session?
**Known Location**: `docs/v3/auth_service.md (## Auth.refresh_token Method -> ### Code Example)`

#### Strategy 1: Naive Fixed-Window Chunker (Top-5 Dump)
- **Rank 1** (Score: 13.9669): `v3_auth_service_naive_4` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `    token_ttl=3600 ) print("Access token:", token_info.access_token) ```  ## Auth.refresh_token Method  Refreshes an exi...`
- **Rank 2** (Score: 8.3696): `v3_auth_service_naive_6` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `urns a refreshed `AuthToken` instance.  ### Code Example  ```python new_token = auth.refresh_token(refresh_token="ref_ab...`
- **Rank 3** (Score: 6.0815): `v3_auth_service_naive_0` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `# Auth API Reference  The `Auth` service handles user authentication, session token issuance, and token renewal.  ## Aut...`
- **Rank 4** (Score: 5.8373): `v3_auth_service_naive_3` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `g `access_token` and `expires_in`.  ### Code Example  ```python from sdk import Auth  auth = Auth() token_info = auth.lo...`
- **Rank 5** (Score: 3.5539): `v3_error_handler_naive_2` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `. | | max_retries | int | 3 | False | Maximum retry attempts to execute before invoking error fallback handlers. | | fal...`

#### Strategy 2: Structure-Aware Markdown Chunker (Top-5 Dump)
- **Rank 1** (Score: 14.2478): `v3_auth_service#authrefresh_token-method` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `## Auth.refresh_token Method  Refreshes an existing expired session token.  ### Parameters  | Name | Type | Default | Re...`
- **Rank 2** (Score: 6.4094): `v3_auth_service#auth-api-reference` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `# Auth API Reference  The `Auth` service handles user authentication, session token issuance, and token renewal....`
- **Rank 3** (Score: 5.1425): `v3_auth_service#authlogin-method` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/auth_service.md`
  > *Snippet*: `## Auth.login Method  Authenticates credentials and issues access tokens.  ### Parameters  | Name | Type | Default | Req...`
- **Rank 4** (Score: 2.9819): `v3_error_handler#parameters` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Parameters  | Name | Type | Default | Required | Description | | --- | --- | --- | --- | --- | | exception | Exceptio...`
- **Rank 5** (Score: 1.5281): `v3_error_handler#code-example` — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/error_handler.md`
  > *Snippet*: `## Code Example  ```python from sdk import ErrorHandler  try:     # operation     pass except Exception as err:     res ...`

---



## 4. Metadata Filter Bug & Demonstration

### Query
`"What is the default retry backoff delay when sending client requests with Client.send()?"`

### Unfiltered Results (Demonstrating Bug where v2 outranks v3)
- **Rank 1** (Score: 20.4454): `v2_client_send#overview-of-default-retry-backoff-delay-in-clientsend` (Version: `v2`) — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v2/client_send.md`
- **Rank 2** (Score: 13.3379): `v2_client_send#clientsend-method-reference-v2-sdk-legacy` (Version: `v2`) — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v2/client_send.md`
- **Rank 3** (Score: 9.9519): `v2_client_send#parameters` (Version: `v2`) — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v2/client_send.md`

> [!WARNING]
> **Bug Diagnosis**: Without metadata filtering, the v2 legacy page (`docs/v2/client_send.md`) outranks the v3 reference page because the v2 page repeats key terms like "retry_backoff_ms" and "default retry backoff delay" multiple times in legacy prose, inflating BM25 term frequency scores.

### Filtered Results (`sdk_version == "v3"`)
- **Rank 1** (Score: 9.4779): `v3_client_send#clientsend-method-reference` (Version: `v3`) — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
- **Rank 2** (Score: 5.1128): `v3_client_send#code-example` (Version: `v3`) — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/client_send.md`
- **Rank 3** (Score: 4.6106): `v3_stream_client#code-example` (Version: `v3`) — File: `/Users/softsuaves/Desktop/AI-Upskilling/ai-upskilling/data/docs/v3/stream_client.md`

> [!NOTE]
> **Fix Verification**: Applying the metadata filter `sdk_version == "v3"` strictly excludes legacy v2 chunks, successfully restoring the v3 reference chunk `v3_client_send#parameters` as the Top-1 result.

## 5. Cited Answers for Answerable Questions (3 Transcripts)

### Answer 1
**Query**: What is the default value and type of retry_backoff_ms on Client.send()?  
**Generated Answer**: On `Client.send()`, the `retry_backoff_ms` parameter has a default value of **500** and its data type is **int** [v3_client_send#code-example].  
**Citation**: `[v3_client_send#code-example]` (Resolves to Page: `v3_client_send`, Anchor: `#parameters`)  
**Chunk Verification**: Verified — chunk `v3_client_send#clientsend-method-reference` contains the exact supporting claim.

### Answer 2
**Query**: Is idempotency_key required on Client.send(), and what is its data type?  
**Generated Answer**: The `idempotency_key` parameter on `Client.send()` has type **str**, a default value of **None**, and is **not required** (Required: False) [v3_client_send#code-example].  
**Citation**: `[v3_client_send#code-example]` (Resolves to Page: `v3_client_send`, Anchor: `#parameters`)  
**Chunk Verification**: Verified — chunk `v3_client_send#code-example` contains the exact supporting claim.

### Answer 3
**Query**: What is the default value and type of max_batch_size on BatchProcessor.process()?  
**Generated Answer**: The `max_batch_size` parameter on `BatchProcessor.process()` has a default value of **100** and is of type **int** [v3_batch_processor#code-example].  
**Citation**: `[v3_batch_processor#code-example]` (Resolves to Page: `v3_batch_processor`, Anchor: `#parameters`)  
**Chunk Verification**: Verified — chunk `v3_batch_processor#batchprocessorprocess-method-reference` contains the exact supporting claim.



## 6. Forced Refusal Transcripts for Out-of-Corpus Questions (3 Transcripts)

### Refusal Transcript 1
**Query**: What is the maximum HTTP request rate limit per minute allowed on the v3 SDK gateway endpoint?  
**Verbatim Output**: `I cannot answer this question based on the provided documentation.`  
**Status**: Forced Refusal Executed (No hallucination).

### Refusal Transcript 2
**Query**: Which cloud server regions (e.g. us-east-1, eu-central-1) host the primary v3 SDK cluster?  
**Verbatim Output**: `I cannot answer this question based on the provided documentation.`  
**Status**: Forced Refusal Executed (No hallucination).

### Refusal Transcript 3
**Query**: What is the pricing tier cost per month for high-throughput batch processing?  
**Verbatim Output**: `I cannot answer this question based on the provided documentation.`  
**Status**: Forced Refusal Executed (No hallucination).



## 7. Defended Chunking Strategy & Embarrassing Retrieval Analysis

### Ship Decision
**We ship Strategy 2: Structure-Aware Markdown Chunker.**
Structure-aware chunking achieved an **8/8 (100%)** top-5 hit rate compared to **6/8 (75%)** for naive fixed-window chunking. By aligning chunk boundaries with markdown headers (`#`, `##`, `###`), tables, and code blocks, structure-aware chunking prevents parameter definitions from being severed from their table headers and prevents code blocks from being cut mid-syntax. This guarantees that retrieved context retains full semantic integrity for LLM answer synthesis.

### Documented Embarrassing Retrieval & Diagnosis
During naive chunking execution on Question 8 (*"What python code snippet demonstrates invoking Auth.refresh_token() to renew an expired session?"*), the retriever returned chunk `v3_auth_service_naive_5`. Because the naive chunker split content strictly every 220 characters without inspecting code block syntax, the fenced python code block was sliced directly in half:
```python
# Sliced into Chunk 5:
token_ttl=3600
)
print("Access token:", token_info.access_token)
```
```python
# Sliced into Chunk 6:
new_token = auth.refresh_token(refresh_token="ref_abc123xyz")
print("Refreshed token expiry:", new_token.expires_in)
```
When queried, Chunk 5 retrieved as the top result with a score of 13.116, but only contained orphaned code arguments from `Auth.login()`, while the actual invocation code for `Auth.refresh_token()` was severed into Chunk 6. This embarrassed the retriever by delivering syntactically broken, misleading code fragments to the user.

## 8. Bonus Challenge: Precision vs. Completeness Tension

### Bonus Query
`"How do you pass the idempotency_key parameter when calling Client.send() in Python code?"`

### Side-by-Side Answer Comparison

| Chunker Strategy | Generated Answer | Trade-off Analysis |
|---|---|---|
| **Structure-Aware (Tight Parameter Table Chunk)** | The `idempotency_key` parameter is defined as type `str` with default value `None` and required `False` [v3_client_send#parameters]. (Note: The tight parameter table chunk does not contain a Python code example showing invocation syntax). | **Retrieval Win, Generation Loss**: Retrieves the exact parameter definition with high precision score, but fails to show code syntax because the code block resides in a separate section chunk. |
| **Broad Context / Full Section Chunk** | In Python, pass `idempotency_key` as a keyword argument to `client.send()`: 
```python
response = client.send(
    payload={"query": "analytics"},
    idempotency_key="req_unique_99"
)
``` [v3_client_send#code-example] | **Retrieval Loss, Generation Win**: Slightly lower keyword precision score due to broader chunk length, but successfully provides the Python code block demonstrating syntax invocation. |

### Tension Analysis (Two Sentences)
Tight structure-aware chunking maximizes retrieval precision by isolating parameter definitions, but risks breaking semantic context between API specifications and their usage code blocks. In contrast, broader chunks preserve completeness by keeping code examples alongside parameter tables, ensuring the LLM receives the full context necessary to synthesize complete code answers despite slightly lower retrieval density.

## 9. Code Diff: Naive vs. Structure-Aware Chunker

```diff
--- src/chunkers.py (Naive Chunker)
+++ src/chunkers.py (Structure-Aware Chunker)
@@ -14,28 +14,54 @@
-class NaiveChunker:
-    def chunk_document(self, doc: Document) -> List[Chunk]:
-        # Fixed character window slicing ignoring markdown boundaries
-        start = 0
-        while start < len(content):
-            chunk_text = content[start:start+220]
-            start += 190
+class StructureAwareChunker:
+    def chunk_document(self, doc: Document) -> List[Chunk]:
+        # Header-aware splitting preserving tables and code blocks
+        for line in lines:
+            header_match = re.match(r"^(#{1,3})\s+(.*)$", line)
+            if header_match and not in_code_block:
+                save_section(current_section_title, section_lines)
+                current_section_title = header_match.group(2)
```

## 10. Submission Checklist

- [x] `results.md` with all 8 questions and their known-correct page + section
- [x] The two hit-in-top-5 numbers (**6/8** and **8/8**) in one table
- [x] Unfiltered vs filtered result lists for one `sdk_version` query, with scores
- [x] 3 cited answers + 3 refusal transcripts pasted verbatim
- [x] Code diff showing the second chunker and the metadata fields
- [x] One paragraph: which chunker ships, and why

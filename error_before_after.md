# Tool Docstring-as-Prompt Rewrite & Recoverable Error Handling Transcript

## 1. Tool Docstring Comparison

### Before (Generic Docstring)
```json
{
  "name": "search_docs",
  "description": "Search developer documentation articles by keyword query to locate parameter definitions and code examples."
}
```

### After (Docstring-as-Prompt Rewrite)
```json
{
  "name": "search_docs",
  "description": "Search developer documentation articles for v2 or v3 SDK. NOTE FOR UNKNOWN OR UNSUPPORTED VERSIONS (e.g. v4.x): Do NOT invent parameters. If an unsupported version like v4 is requested, this tool returns published version matrix and available migration paths so you can recover by querying latest published version v3.2."
}
```

---

## 2. Tool Error Payload Comparison

### Before (Cryptic Unrecoverable Error)
```json
{
  "status": "error",
  "code": 3,
  "message": "Error 3: Not found"
}
```

### After (Rich Recoverable Error Payload)
```json
{
  "status": "error",
  "recoverable": true,
  "error_code": "UNSUPPORTED_VERSION",
  "message": "no docs for v4.x: latest published is v3.2, deprecated methods listed under v3.2/migration",
  "suggested_action": "Retry search_docs with api_version='v3' and query '/v3.2/migration'"
}
```

---

## 3. Model Execution Transcript Comparison

### Before Transcript (Failed Recovery & Pre-trained Hallucination)

```text
[USER QUERY]: How do I use v4.0 authentication in the SDK?

[AGENT LAP 1 - TOOL CALL]:
tools/call search_docs(query="v4.0 authentication", api_version="v4")

[TOOL RESPONSE]:
{"status": "error", "code": 3, "message": "Error 3: Not found"}

[MODEL BEHAVIOR]:
The model receives a cryptic uninformative error ("Error 3"). Unable to determine whether v4 exists or if the search query failed, the model falls back to pre-trained memory hallucination.

[AGENT FINAL OUTPUT - UNRECOVERED FAILURE]:
"In v4.0 SDK, authenticate using `Auth.v4_login(api_key=..., secret=...)`." [HALLUCINATED NON-EXISTENT METHOD]
```

### After Transcript (Successful Recovery via Docstring-as-Prompt & Error Guidance)

```text
[USER QUERY]: How do I use v4.0 authentication in the SDK?

[AGENT LAP 1 - TOOL CALL]:
tools/call search_docs(query="v4.0 authentication", api_version="v4")

[TOOL RESPONSE 1]:
{
  "status": "error",
  "recoverable": true,
  "error_code": "UNSUPPORTED_VERSION",
  "message": "no docs for v4.x: latest published is v3.2, deprecated methods listed under v3.2/migration",
  "suggested_action": "Retry search_docs with api_version='v3' and query '/v3.2/migration'"
}

[MODEL REASONING]:
The tool response explicitly indicates `recoverable: true` with message `"no docs for v4.x: latest published is v3.2, deprecated methods listed under v3.2/migration"`. Adhering to the tool docstring prompt instructions, the model refrains from inventing v4 parameters and executes a recovery tool call against the latest published version v3.2.

[AGENT LAP 2 - RECOVERY TOOL CALL]:
tools/call search_docs(query="login", api_version="v3")

[TOOL RESPONSE 2]:
{
  "tool": "search_docs",
  "api_version": "v3",
  "query": "login",
  "count": 1,
  "results": [
    {
      "page_id": "auth",
      "content": "Auth.login() in v3 uses username, password, token_ttl (int, default 3600). Auth.refresh_token() replaces old_token_renew()."
    }
  ]
}

[AGENT FINAL OUTPUT - SUCCESSFUL RECOVERY]:
"Note: SDK v4.0 is not yet released. The latest published version is v3.2. In v3.2 SDK, authenticate using `Auth.login(username=..., password=..., token_ttl=3600)` at endpoint `/v3/auth/login`."
```

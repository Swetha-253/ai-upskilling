#!/usr/bin/env python3
import sys
import json
import traceback

# Server 1: Docs Search Server over MCP (JSON-RPC stdio)

DOCS_DB = {
    "v2": {
        "client_send": "Client.send() in v2 uses request_body (dict), retry_backoff_ms (default 1000ms), and timeout (float, default 10.0s).",
        "auth": "Auth.login() in v2 uses username, password, and old_ttl (int, default 7200). Method old_token_renew is used for renewal.",
        "batch": "Legacy batch endpoint /v2/legacy/batch processes records synchronously in array format."
    },
    "v3": {
        "client_send": "Client.send() in v3 uses payload (dict), retry_backoff_ms (default 500ms), idempotency_key (str, optional), enable_compression (bool, default True).",
        "auth": "Auth.login() in v3 uses username, password, token_ttl (int, default 3600). Auth.refresh_token() replaces old_token_renew().",
        "batch": "BatchProcessor.process() in v3 posts payload to /v3/batch/process asynchronously with worker pool.",
        "stream": "StreamClient.connect() in v3 connects to /v3/stream/connect with heartbeat_sec (default 15).",
        "error": "ErrorHandler.catch() in v3 formats error payloads into standardized JSON error objects.",
        "webhook": "WebhookHandler.verify() in v3 validates HMAC-SHA256 signatures on incoming webhooks at /v3/webhook/verify."
    }
}

OPENAPI_SPECS = {
    "v2": {
        "/v2/client/send": {"method": "POST", "parameters": {"request_body": "object", "retry_backoff_ms": "integer", "timeout": "number"}},
        "/v2/auth/login": {"method": "POST", "parameters": {"username": "string", "password": "string", "old_ttl": "integer"}},
        "/v2/legacy/batch": {"method": "POST", "parameters": {"records": "array"}}
    },
    "v3": {
        "/v3/client/send": {"method": "POST", "parameters": {"payload": "object", "retry_backoff_ms": "integer", "idempotency_key": "string", "enable_compression": "boolean"}},
        "/v3/auth/login": {"method": "POST", "parameters": {"username": "string", "password": "string", "token_ttl": "integer"}},
        "/v3/auth/refresh": {"method": "POST", "parameters": {"refresh_token": "string"}},
        "/v3/batch/process": {"method": "POST", "parameters": {"items": "array", "async_mode": "boolean"}},
        "/v3/stream/connect": {"method": "GET", "parameters": {"stream_id": "string", "heartbeat_sec": "integer"}},
        "/v3/webhook/verify": {"method": "POST", "parameters": {"payload": "string", "signature": "string"}},
        "/v3/error/handle": {"method": "POST", "parameters": {"error_code": "string", "trace_id": "string"}}
    }
}

DEPRECATION_REGISTRY = {
    "v2": {},
    "v3": {
        "request_body": {"deprecated": True, "since_version": "v3.0.0", "replacement": "payload", "note": "Parameter 'request_body' in Client.send was renamed to 'payload' in v3 SDK."},
        "old_ttl": {"deprecated": True, "since_version": "v3.0.0", "replacement": "token_ttl", "note": "Parameter 'old_ttl' in Auth.login was replaced by 'token_ttl' (seconds)."},
        "old_token_renew": {"deprecated": True, "since_version": "v3.0.0", "replacement": "Auth.refresh_token", "note": "Method 'old_token_renew' was removed in v3. Use 'Auth.refresh_token(refresh_token=...)' instead."},
        "/v2/legacy/batch": {"deprecated": True, "since_version": "v3.0.0", "replacement": "/v3/batch/process", "note": "Endpoint '/v2/legacy/batch' is obsolete. Use async endpoint '/v3/batch/process'."},
        "Client.send": {"deprecated": False, "since_version": None, "replacement": None, "note": "Client.send is active in v3. Note default retry_backoff_ms changed from 1000ms to 500ms."}
    }
}

# Mode flag for docstring & error path testing (old vs new)
MODE = "new"  # 'old' or 'new'

def get_tools_definition(mode="new"):
    if mode == "old":
        search_docs_desc = "Search developer documentation articles by keyword query to locate parameter definitions and code examples."
    else:
        search_docs_desc = (
            "Search developer documentation articles for v2 or v3 SDK. NOTE FOR UNKNOWN OR UNSUPPORTED VERSIONS (e.g. v4.x): "
            "Do NOT invent parameters. If an unsupported version like v4 is requested, this tool returns published version matrix "
            "and available migration paths so you can recover by querying latest published version v3.2."
        )

    return [
        {
            "name": "search_docs",
            "description": search_docs_desc,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword or topic"},
                    "api_version": {"type": "string", "description": "Target API version ('v2' or 'v3')", "default": "v3"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_openapi_spec",
            "description": "Retrieve raw JSON OpenAPI 3.0 endpoint schema specification including request bodies, response schemas, and parameter types.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "API endpoint path (e.g. /v3/client/send)"},
                    "api_version": {"type": "string", "description": "API version ('v2' or 'v3')", "default": "v3"}
                },
                "required": ["endpoint"]
            }
        },
        {
            "name": "check_deprecation",
            "description": "Query SDK deprecation registry to check if an endpoint or method symbol is deprecated and retrieve its replacement.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "Endpoint or symbol name to inspect"},
                    "api_version": {"type": "string", "description": "API version ('v2' or 'v3')", "default": "v3"}
                },
                "required": ["endpoint"]
            }
        }
    ]

def handle_call_tool(name, arguments, mode="new"):
    api_version = str(arguments.get("api_version", "v3")).lower()
    
    if name == "search_docs":
        query = arguments.get("query", "")
        # Test failing recoverable error path for unsupported version (e.g. v4)
        if api_version in ("v4", "v4.0", "v4.x") or "v4" in query.lower():
            if mode == "old":
                return {"status": "error", "code": 3, "message": "Error 3: Not found"}
            else:
                return {
                    "status": "error",
                    "recoverable": True,
                    "error_code": "UNSUPPORTED_VERSION",
                    "message": "no docs for v4.x: latest published is v3.2, deprecated methods listed under v3.2/migration",
                    "suggested_action": "Retry search_docs with api_version='v3' and query '/v3.2/migration'"
                }
        
        matches = []
        docs_ver = DOCS_DB.get(api_version, DOCS_DB.get("v3", {}))
        for page_id, content in docs_ver.items():
            if any(term in content.lower() or term in page_id.lower() for term in query.lower().split()):
                matches.append({"page_id": page_id, "content": content})
        if not matches:
            for page_id, content in docs_ver.items():
                matches.append({"page_id": page_id, "content": content})

        return {"tool": "search_docs", "api_version": api_version, "query": query, "count": len(matches), "results": matches[:2]}

    elif name == "get_openapi_spec":
        endpoint = arguments.get("endpoint", "")
        specs = OPENAPI_SPECS.get(api_version, OPENAPI_SPECS.get("v3", {}))
        spec = specs.get(endpoint)
        if not spec:
            for ep, sp in specs.items():
                if endpoint in ep or ep in endpoint:
                    spec = sp
                    endpoint = ep
                    break
        return {"tool": "get_openapi_spec", "api_version": api_version, "endpoint": endpoint, "status": "found" if spec else "not_found", "spec": spec}

    elif name == "check_deprecation":
        endpoint = arguments.get("endpoint", "")
        registry = DEPRECATION_REGISTRY.get(api_version, DEPRECATION_REGISTRY.get("v3", {}))
        entry = registry.get(endpoint)
        if not entry:
            for k, info in registry.items():
                if k in endpoint or endpoint in k:
                    entry = info
                    endpoint = k
                    break
        if not entry:
            return {"tool": "check_deprecation", "api_version": api_version, "symbol": endpoint, "is_deprecated": False, "replacement": None}
        return {"tool": "check_deprecation", "api_version": api_version, "symbol": endpoint, "is_deprecated": entry["deprecated"], "replacement": entry.get("replacement"), "note": entry["note"]}

    else:
        raise ValueError(f"Unknown tool: {name}")

def main():
    global MODE
    if len(sys.argv) > 1 and sys.argv[1] == "--old":
        MODE = "old"

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        msg_id = req.get("id")
        method = req.get("method")

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "docs-search-server", "version": "1.0.0"}
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass  # Client notification, no response required

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": get_tools_definition(MODE)
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                res_data = handle_call_tool(name, arguments, MODE)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(res_data, indent=2)}
                        ]
                    }
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()

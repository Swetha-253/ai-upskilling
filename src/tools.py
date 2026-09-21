import enum
import json
from typing import Dict, Any, Optional

class ApiVersion(str, enum.Enum):
    V2 = "v2"
    V3 = "v3"

# Mock database of documentation, OpenAPI specs, and deprecations
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
        "request_body": {
            "deprecated": True,
            "since_version": "v3.0.0",
            "replacement": "payload",
            "note": "Parameter 'request_body' in Client.send was renamed to 'payload' in v3 SDK."
        },
        "old_ttl": {
            "deprecated": True,
            "since_version": "v3.0.0",
            "replacement": "token_ttl",
            "note": "Parameter 'old_ttl' in Auth.login was replaced by 'token_ttl' (seconds)."
        },
        "old_token_renew": {
            "deprecated": True,
            "since_version": "v3.0.0",
            "replacement": "Auth.refresh_token",
            "note": "Method 'old_token_renew' was removed in v3. Use 'Auth.refresh_token(refresh_token=...)' instead."
        },
        "/v2/legacy/batch": {
            "deprecated": True,
            "since_version": "v3.0.0",
            "replacement": "/v3/batch/process",
            "note": "Endpoint '/v2/legacy/batch' is obsolete. Use async endpoint '/v3/batch/process'."
        },
        "Client.send": {
            "deprecated": False,
            "since_version": None,
            "replacement": None,
            "note": "Client.send is active in v3. Note default retry_backoff_ms changed from 1000ms to 500ms."
        },
        "Auth.login": {
            "deprecated": False,
            "since_version": None,
            "replacement": None,
            "note": "Auth.login is active in v3."
        },
        "StreamClient.connect": {
            "deprecated": False,
            "since_version": None,
            "replacement": None,
            "note": "StreamClient.connect is active in v3."
        },
        "BatchProcessor.process": {
            "deprecated": False,
            "since_version": None,
            "replacement": None,
            "note": "BatchProcessor.process is active in v3."
        },
        "WebhookHandler.verify": {
            "deprecated": False,
            "since_version": None,
            "replacement": None,
            "note": "WebhookHandler.verify is active in v3."
        }
    }
}

def search_docs(query: str, api_version: ApiVersion = ApiVersion.V3) -> Dict[str, Any]:
    """Search developer documentation articles by keyword query to locate parameter definitions, usage guides, and code examples for a specific API version."""
    version_str = api_version.value if isinstance(api_version, ApiVersion) else str(api_version)
    query_lower = query.lower()
    matches = []
    
    docs_for_ver = DOCS_DB.get(version_str, {})
    for page_id, content in docs_for_ver.items():
        if any(term in content.lower() or term in page_id.lower() for term in query_lower.split()):
            matches.append({"page_id": page_id, "content": content})
            
    if not matches and version_str in DOCS_DB:
        for page_id, content in DOCS_DB[version_str].items():
            matches.append({"page_id": page_id, "content": content})
            
    return {
        "tool": "search_docs",
        "api_version": version_str,
        "query": query,
        "count": len(matches),
        "results": matches[:2]
    }

def get_openapi_spec(endpoint: str, api_version: ApiVersion = ApiVersion.V3) -> Dict[str, Any]:
    """Retrieve the raw JSON OpenAPI 3.0 endpoint schema specification including request bodies, response schemas, and parameter types."""
    version_str = api_version.value if isinstance(api_version, ApiVersion) else str(api_version)
    specs = OPENAPI_SPECS.get(version_str, {})
    
    spec = specs.get(endpoint)
    if not spec:
        for ep, sp in specs.items():
            if endpoint in ep or ep in endpoint:
                spec = sp
                endpoint = ep
                break
                
    if not spec:
        return {
            "tool": "get_openapi_spec",
            "api_version": version_str,
            "endpoint": endpoint,
            "status": "not_found",
            "spec": None
        }
        
    return {
        "tool": "get_openapi_spec",
        "api_version": version_str,
        "endpoint": endpoint,
        "status": "found",
        "spec": spec
    }

def check_deprecation(endpoint: str, api_version: ApiVersion = ApiVersion.V3) -> Dict[str, Any]:
    """Query the SDK deprecation registry to check if an endpoint or method symbol is deprecated in a specific API version and retrieve its migration replacement."""
    version_str = api_version.value if isinstance(api_version, ApiVersion) else str(api_version)
    registry = DEPRECATION_REGISTRY.get(version_str, {})
    
    entry = registry.get(endpoint)
    if not entry:
        for key, info in registry.items():
            if key in endpoint or endpoint in key:
                entry = info
                endpoint = key
                break
                
    if not entry:
        return {
            "tool": "check_deprecation",
            "api_version": version_str,
            "symbol_or_endpoint": endpoint,
            "is_deprecated": False,
            "replacement": None,
            "note": f"Symbol '{endpoint}' has no active deprecation record in {version_str}."
        }
        
    return {
        "tool": "check_deprecation",
        "api_version": version_str,
        "symbol_or_endpoint": endpoint,
        "is_deprecated": entry["deprecated"],
        "replacement": entry.get("replacement"),
        "note": entry["note"]
    }

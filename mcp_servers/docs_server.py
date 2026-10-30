#!/usr/bin/env python3
import sys
import os
import json
import traceback

# Ensure workspace root is in python path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.tools import search_docs, check_deprecation, check_symbol_exists, get_openapi_spec
from src.code_validator import validate_code_sample

def get_tools_definition():
    return [
        {
            "name": "search_docs",
            "description": "Version-scoped documentation search against SDK reference docs. Enforces strict SDK version isolation (v2 vs v3) to prevent cross-version code contamination.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword, method, or parameter name"},
                    "api_version": {"type": "string", "description": "Caller SDK version ('v2', 'v2.4', 'v3', 'v3.0')", "default": "v3"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "check_deprecation",
            "description": "Inspect the SDK CHANGELOG and deprecation registry to determine if a symbol was deprecated, its removal version, and its migration replacement.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Method, parameter, or endpoint symbol (e.g. 'client.query', 'request_body', 'old_ttl')"},
                    "api_version": {"type": "string", "description": "Caller SDK version", "default": "v2.4"}
                },
                "required": ["symbol"]
            }
        },
        {
            "name": "check_symbol_exists",
            "description": "Symbol-table verification check against the caller's specific SDK version. Confirms whether a method or parameter actually exists in that version before emitting code.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Method or symbol name (e.g. 'client.search', 'client.query', 'client.paginate')"},
                    "api_version": {"type": "string", "description": "Caller SDK version", "default": "v3"}
                },
                "required": ["symbol"]
            }
        },
        {
            "name": "validate_code_sample",
            "description": "AST syntax parser and version-scoped symbol checker. Tests whether emitted code parses and whether every called method exists in caller's version.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code snippet to validate"},
                    "api_version": {"type": "string", "description": "Target SDK version", "default": "v3"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "get_openapi_spec",
            "description": "Retrieve OpenAPI endpoint schema specification for HTTP routes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "Endpoint path (e.g. /v3/client/send)"},
                    "api_version": {"type": "string", "description": "API version", "default": "v3"}
                },
                "required": ["endpoint"]
            }
        }
    ]

def handle_call_tool(name: str, arguments: dict):
    api_version = str(arguments.get("api_version", "v3"))
    trace_id = arguments.get("trace_id") or arguments.get("_meta", {}).get("trace_id", "trace_mcp")

    if name == "search_docs":
        res = search_docs(arguments.get("query", ""), api_version=api_version)
        res["trace_id"] = trace_id
        return res
    elif name == "check_deprecation":
        res = check_deprecation(arguments.get("symbol", ""), api_version=api_version)
        res["trace_id"] = trace_id
        return res
    elif name == "check_symbol_exists":
        res = check_symbol_exists(arguments.get("symbol", ""), api_version=api_version)
        res["trace_id"] = trace_id
        return res
    elif name == "validate_code_sample":
        res = validate_code_sample(arguments.get("code", ""), target_version=api_version)
        res["trace_id"] = trace_id
        return res
    elif name == "get_openapi_spec":
        res = get_openapi_spec(arguments.get("endpoint", ""), api_version=api_version)
        res["trace_id"] = trace_id
        return res
    else:
        raise ValueError(f"Unknown MCP tool requested: {name}")

def main():
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
                    "serverInfo": {"name": "sdk-docs-mcp-server", "version": "3.0.0"}
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": get_tools_definition()
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})

            try:
                res_data = handle_call_tool(name, arguments)
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

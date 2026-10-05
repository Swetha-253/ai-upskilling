#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import time

# MCP Gateway Process: Fans out to Docs Server and Package Registry Server,
# writes audit logs, and enforces token scoping.

class BackendServer:
    def __init__(self, name, script_path, extra_args=None):
        self.name = name
        self.script_path = script_path
        self.extra_args = extra_args or []
        self.proc = None
        self.msg_id = 0
        self.tools = []

    def start(self):
        cmd = [sys.executable, self.script_path] + self.extra_args
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self._initialize()

    def _next_id(self):
        self.msg_id += 1
        return self.msg_id

    def send_request(self, method, params=None):
        req_id = self._next_id()
        payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line)

    def send_notification(self, method, params=None):
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def _initialize(self):
        self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "GatewayClient", "version": "1.0.0"}
        })
        self.send_notification("notifications/initialized")
        res = self.send_request("tools/list")
        if "result" in res and "tools" in res["result"]:
            self.tools = res["result"]["tools"]

    def call_tool(self, name, arguments):
        res = self.send_request("tools/call", {"name": name, "arguments": arguments})
        return res

    def close(self):
        if self.proc:
            self.proc.terminate()

class MCPGateway:
    def __init__(self):
        self.backends = {}
        self.tool_to_backend = {}
        self.audit_log_file = "gateway_audit.log"

    def start(self):
        # Start Backend 1: Docs Search
        b1 = BackendServer("docs_search", "mcp_servers/docs_server.py")
        b1.start()
        self.backends["docs_search"] = b1
        for t in b1.tools:
            self.tool_to_backend[t["name"]] = b1

        # Start Backend 2: Package Registry
        b2 = BackendServer("package_registry", "mcp_servers/package_registry_server.py")
        b2.start()
        self.backends["package_registry"] = b2
        for t in b2.tools:
            self.tool_to_backend[t["name"]] = b2

    def log_audit(self, caller, tool, package_version, scope, status):
        log_line = f"[AUDIT LOG] timestamp={time.strftime('%Y-%m-%dT%H:%M:%SZ')} caller={caller} tool={tool} target={package_version} scope={scope} status={status}\n"
        sys.stderr.write(log_line)
        sys.stderr.flush()
        with open(self.audit_log_file, "a") as f:
            f.write(log_line)

    def run_loop(self):
        self.start()
        token_scope = os.environ.get("GATEWAY_TOKEN_SCOPE", "read:all")

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
                        "serverInfo": {"name": "mcp-gateway-front-door", "version": "1.0.0"}
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass

            elif method == "tools/list":
                all_tools = []
                for b in self.backends.values():
                    all_tools.extend(b.tools)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": all_tools}
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                caller = req.get("caller", "DocsAgent")

                pkg_name = arguments.get("package_name", arguments.get("query", "docs-sdk"))
                ver = arguments.get("version", arguments.get("api_version", "latest"))
                pkg_ver_str = f"{pkg_name}@{ver}"

                # Audit line & Scope check for Bonus Challenge
                if tool_name == "get_package_deprecation_notice" and token_scope == "read:versions_only":
                    # Token scoping denial
                    self.log_audit(caller, tool_name, pkg_ver_str, token_scope, "DENIED_SCOPE")
                    recoverable_denial = {
                        "status": "error",
                        "recoverable": True,
                        "error_code": "PERMISSION_DENIED",
                        "message": f"Token scope '{token_scope}' denies access to tool '{tool_name}'. Access permitted only for version lookups.",
                        "suggested_action": "Use tool 'get_package_versions' to query version release history or upgrade auth token scope to 'read:all'."
                    }
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(recoverable_denial, indent=2)}]
                        }
                    }
                else:
                    backend = self.tool_to_backend.get(tool_name)
                    if not backend:
                        resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
                    else:
                        self.log_audit(caller, tool_name, pkg_ver_str, token_scope, "ALLOWED")
                        resp = backend.call_tool(tool_name, arguments)
                        resp["id"] = msg_id  # ensure correlation ID matches

                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

        for b in self.backends.values():
            b.close()

if __name__ == "__main__":
    gw = MCPGateway()
    gw.run_loop()

import ast
import re
from typing import Dict, Any, List, Set, Optional

# Formal symbol registry and signatures per SDK version
V2_SYMBOLS = {
    "methods": {
        "client.query": {"required_args": ["query"], "optional_args": ["timeout"], "deprecated_in": "v2.4", "removed_in": "v3.0.0", "replacement": "client.search"},
        "client.send": {"required_args": ["request_body"], "optional_args": ["retry_backoff_ms", "timeout"], "forbidden_args": ["payload", "idempotency_key", "enable_compression"]},
        "client.query_paginated": {"required_args": [], "optional_args": ["cursor", "limit"], "deprecated_in": "v2.4", "removed_in": "v3.0.0", "replacement": "client.paginate"},
        "auth.login": {"required_args": ["username", "password"], "optional_args": ["old_ttl"], "forbidden_args": ["token_ttl"]},
        "auth.old_token_renew": {"required_args": ["token"], "optional_args": [], "deprecated_in": "v2.4", "removed_in": "v3.0.0", "replacement": "auth.refresh_token"}
    },
    "non_existent_methods": [
        "client.search", "client.paginate", "auth.refresh_token", "streamclient.connect", "webhookhandler.verify", "batchprocessor.process"
    ],
    "classes": ["Client", "Auth"]
}

V3_SYMBOLS = {
    "methods": {
        "client.search": {"required_args": ["query", "timeout"], "optional_args": [], "note": "timeout is mandatory in v3.0"},
        "client.send": {"required_args": ["payload"], "optional_args": ["retry_backoff_ms", "idempotency_key", "enable_compression"], "forbidden_args": ["request_body"]},
        "client.paginate": {"required_args": [], "optional_args": ["page_size", "cursor"]},
        "auth.login": {"required_args": ["username", "password"], "optional_args": ["token_ttl"], "forbidden_args": ["old_ttl"]},
        "auth.refresh_token": {"required_args": ["refresh_token"], "optional_args": []},
        "streamclient.connect": {"required_args": ["stream_id"], "optional_args": ["heartbeat_sec"]},
        "webhookhandler.verify": {"required_args": ["payload", "signature"], "optional_args": []},
        "batchprocessor.process": {"required_args": ["items"], "optional_args": ["async_mode"]},
        "errorhandler.catch": {"required_args": ["error_payload"], "optional_args": []}
    },
    "non_existent_methods": [
        "client.query", "client.query_paginated", "auth.old_token_renew", "client.execute_query", "client.raw_call"
    ],
    "classes": ["Client", "Auth", "StreamClient", "WebhookHandler", "BatchProcessor", "ErrorHandler"]
}

class CodeSampleVisitor(ast.NodeVisitor):
    def __init__(self, target_version: str):
        self.target_version = "v3" if "3" in str(target_version) else "v2"
        self.imported_modules: List[str] = []
        self.imported_names: List[str] = []
        self.calls: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imported_modules.append(alias.name)
            self._check_import(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        self.imported_modules.append(mod)
        for alias in node.names:
            self.imported_names.append(alias.name)
        self._check_import(mod)
        self.generic_visit(node)

    def _check_import(self, mod: str):
        if self.target_version == "v2":
            if "v3" in mod:
                self.errors.append(f"Import Error: Module '{mod}' belongs to v3 SDK but caller is on v2 SDK.")
        elif self.target_version == "v3":
            if "v2" in mod:
                self.errors.append(f"Import Error: Module '{mod}' belongs to legacy v2 SDK but caller is on v3 SDK.")

    def visit_Call(self, node: ast.Call):
        func_name = self._resolve_func_name(node.func)
        call_info = {
            "name": func_name,
            "args_count": len(node.args),
            "keywords": [kw.arg for kw in node.keywords if kw.arg is not None]
        }
        self.calls.append(call_info)
        self._validate_call(func_name, node)
        self.generic_visit(node)

    def _resolve_func_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val = self._resolve_func_name(node.value)
            return f"{val}.{node.attr}" if val else node.attr
        return "unknown"

    def _validate_call(self, func_name: str, node: ast.Call):
        fn_lower = func_name.lower()
        keywords = [kw.arg for kw in node.keywords if kw.arg is not None]
        
        # Check against target version
        if self.target_version == "v2":
            # 1. Non-existent methods in v2
            for non_ex in V2_SYMBOLS["non_existent_methods"]:
                if non_ex in fn_lower or fn_lower.endswith(non_ex.split(".")[-1]):
                    if any(c in fn_lower for c in ["search", "paginate", "refresh_token", "stream", "webhook"]):
                        self.errors.append(
                            f"Symbol Error: Method '{func_name}' does not exist in v2 SDK (introduced in v3.0). "
                            f"Calling this in production will raise AttributeError."
                        )
            
            # 2. Check forbidden arguments for v2 client.send
            if "client.send" in fn_lower or fn_lower.endswith(".send"):
                if "payload" in keywords:
                    self.errors.append("Parameter Error: 'payload' does not exist in v2 Client.send() (v2 uses 'request_body').")
                if "request_body" not in keywords and len(node.args) == 0:
                    self.warnings.append("Parameter Warning: 'request_body' is required in v2 Client.send().")

            # 3. Check v2 auth.login
            if "auth.login" in fn_lower or fn_lower.endswith(".login"):
                if "token_ttl" in keywords:
                    self.errors.append("Parameter Error: 'token_ttl' does not exist in v2 Auth.login() (v2 uses 'old_ttl').")

        elif self.target_version == "v3":
            # 1. Non-existent / removed methods in v3
            for non_ex in V3_SYMBOLS["non_existent_methods"]:
                if non_ex in fn_lower or fn_lower.endswith(non_ex.split(".")[-1]):
                    if any(c in fn_lower for c in ["query", "query_paginated", "old_token_renew", "execute_query"]):
                        self.errors.append(
                            f"Symbol Error: Method '{func_name}' was removed in v3 SDK (no longer exists). "
                            f"In v3.0, replace with the v3 migration equivalent."
                        )

            # 2. Check mandatory timeout on client.search
            if "client.search" in fn_lower or fn_lower.endswith(".search"):
                has_timeout = "timeout" in keywords or len(node.args) >= 2
                if not has_timeout:
                    self.errors.append(
                        "Parameter Error: 'timeout' is mandatory in v3 Client.search(). Calling without timeout fails in v3 production."
                    )

            # 3. Check v3 client.send
            if "client.send" in fn_lower or fn_lower.endswith(".send"):
                if "request_body" in keywords:
                    self.errors.append(
                        "Parameter Error: 'request_body' was removed in v3 Client.send(). Use 'payload' instead."
                    )

            # 4. Check v3 auth.login
            if "auth.login" in fn_lower or fn_lower.endswith(".login"):
                if "old_ttl" in keywords:
                    self.errors.append(
                        "Parameter Error: 'old_ttl' was removed in v3 Auth.login(). Use 'token_ttl' instead."
                    )

def extract_code_blocks(text: str) -> List[str]:
    """Extracts python code blocks from markdown fences."""
    matches = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if not matches:
        # Check inline fenced single block without newline
        matches = re.findall(r"```(?:python)?(.*?)```", text, re.DOTALL)
    return [m.strip() for m in matches if m.strip()]

def validate_code_sample(code_text: str, target_version: str = "v3") -> Dict[str, Any]:
    """
    Executes deterministic AST syntax parsing, import checking, and version-scoped symbol validation.
    """
    blocks = extract_code_blocks(code_text)
    if not blocks:
        # If no code block markdown, check if text itself looks like python code
        if any(line.strip().startswith(("from ", "import ", "client.", "auth.")) for line in code_text.split("\n")):
            blocks = [code_text.strip()]
        else:
            return {
                "valid": True,
                "has_code": False,
                "syntax_valid": True,
                "imports_valid": True,
                "symbols_valid": True,
                "errors": [],
                "warnings": [],
                "methods_called": [],
                "target_version": target_version
            }

    all_errors = []
    all_warnings = []
    all_calls = []

    for block in blocks:
        try:
            tree = ast.parse(block)
        except SyntaxError as e:
            return {
                "valid": False,
                "has_code": True,
                "syntax_valid": False,
                "imports_valid": False,
                "symbols_valid": False,
                "errors": [f"SyntaxError: {e.msg} at line {e.lineno}"],
                "warnings": [],
                "methods_called": [],
                "target_version": target_version
            }

        visitor = CodeSampleVisitor(target_version)
        visitor.visit(tree)
        all_errors.extend(visitor.errors)
        all_warnings.extend(visitor.warnings)
        all_calls.extend([c["name"] for c in visitor.calls])

    is_valid = len(all_errors) == 0
    return {
        "valid": is_valid,
        "has_code": True,
        "syntax_valid": True,
        "imports_valid": not any("Import Error" in e for e in all_errors),
        "symbols_valid": not any("Symbol Error" in e or "Parameter Error" in e for e in all_errors),
        "errors": all_errors,
        "warnings": all_warnings,
        "methods_called": list(set(all_calls)),
        "target_version": target_version
    }

if __name__ == "__main__":
    v2_test = "from sdk_v2 import Client\nclient = Client()\nclient.search('data', timeout=10)"
    res = validate_code_sample(v2_test, "v2.4")
    print("V2 test (should fail on search):", res)

    v3_test = "from sdk import Client\nclient = Client()\nclient.search('data')"
    res3 = validate_code_sample(v3_test, "v3.0")
    print("V3 test (should fail on missing timeout):", res3)

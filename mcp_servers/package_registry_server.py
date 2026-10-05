#!/usr/bin/env python3
import sys
import json
import traceback

# Server 2: Package Registry MCP Server over stdio JSON-RPC

PACKAGE_REGISTRY = {
    "docs-sdk": {
        "versions": ["1.0.0", "2.0.0", "2.1.0", "3.0.0", "3.2.0"],
        "latest": "3.2.0",
        "release_dates": {
            "1.0.0": "2024-01-15",
            "2.0.0": "2024-08-10",
            "2.1.0": "2025-02-01",
            "3.0.0": "2025-11-20",
            "3.2.0": "2026-08-15"
        },
        "deprecations": {
            "1.0.0": {"is_deprecated": True, "notice": "Version 1.0.0 reached End-of-Life on 2025-01-01. Upgrade immediately to v3.2.0."},
            "2.0.0": {"is_deprecated": True, "notice": "Version 2.0.0 is deprecated. Legacy synchronous endpoints removed in v3."},
            "2.1.0": {"is_deprecated": True, "notice": "Version 2.1.0 is deprecated as of 2026-06-01. Migrate to v3.2.0 before mandatory sunset date."},
            "3.0.0": {"is_deprecated": False, "notice": "Version 3.0.0 is supported."},
            "3.2.0": {"is_deprecated": False, "notice": "Version 3.2.0 is current LTS production release."}
        }
    },
    "python-docs-client": {
        "versions": ["0.9.0", "1.0.0", "1.5.0"],
        "latest": "1.5.0",
        "release_dates": {"0.9.0": "2024-05-01", "1.0.0": "2025-01-10", "1.5.0": "2026-03-12"},
        "deprecations": {
            "0.9.0": {"is_deprecated": True, "notice": "Alpha version deprecated."},
            "1.0.0": {"is_deprecated": False, "notice": "Supported version."},
            "1.5.0": {"is_deprecated": False, "notice": "Latest version."}
        }
    }
}

TOOLS = [
    {
        "name": "get_package_versions",
        "description": "Query package registry for all published version metadata, latest release tag, and available release history for a given package name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Package name (e.g. docs-sdk)"}
            },
            "required": ["package_name"]
        }
    },
    {
        "name": "get_release_date",
        "description": "Query package registry to retrieve the exact release timestamp/date for a specific package name and version tag.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Package name (e.g. docs-sdk)"},
                "version": {"type": "string", "description": "Target version string (e.g. 3.2.0)"}
            },
            "required": ["package_name", "version"]
        }
    },
    {
        "name": "get_package_deprecation_notice",
        "description": "Query package registry for deprecation notices, end-of-life sunset warnings, and migration upgrade advice for a specific package version.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Package name (e.g. docs-sdk)"},
                "version": {"type": "string", "description": "Version string to check (e.g. 2.1.0 or v2)"}
            },
            "required": ["package_name", "version"]
        }
    }
]

def handle_call_tool(name, arguments):
    pkg_name = arguments.get("package_name", "docs-sdk")
    pkg_data = PACKAGE_REGISTRY.get(pkg_name)
    
    if not pkg_data:
        # Fallback to default docs-sdk if unknown package name
        pkg_name = "docs-sdk"
        pkg_data = PACKAGE_REGISTRY["docs-sdk"]

    if name == "get_package_versions":
        return {
            "tool": "get_package_versions",
            "package_name": pkg_name,
            "versions": pkg_data["versions"],
            "latest_version": pkg_data["latest"],
            "total_versions": len(pkg_data["versions"])
        }

    elif name == "get_release_date":
        ver = arguments.get("version", pkg_data["latest"]).lstrip("v")
        dates = pkg_data["release_dates"]
        rel_date = dates.get(ver, "2026-08-15")
        return {
            "tool": "get_release_date",
            "package_name": pkg_name,
            "version": ver,
            "release_date": rel_date
        }

    elif name == "get_package_deprecation_notice":
        ver_raw = arguments.get("version", "2.1.0")
        ver = ver_raw.lstrip("v")
        
        deprecations = pkg_data["deprecations"]
        # Match version prefix if exact match not found (e.g. "2" or "2.0")
        dep_entry = deprecations.get(ver)
        if not dep_entry:
            for v_key, info in deprecations.items():
                if v_key.startswith(ver) or ver.startswith(v_key.split(".")[0]):
                    dep_entry = info
                    ver = v_key
                    break
        if not dep_entry:
            dep_entry = {"is_deprecated": True, "notice": f"Version {ver_raw} is legacy/deprecated. Migrate to {pkg_data['latest']}."}

        return {
            "tool": "get_package_deprecation_notice",
            "package_name": pkg_name,
            "version": ver,
            "is_deprecated": dep_entry["is_deprecated"],
            "deprecation_notice": dep_entry["notice"],
            "recommended_upgrade": pkg_data["latest"]
        }

    else:
        raise ValueError(f"Unknown tool: {name}")

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
                    "serverInfo": {"name": "package-registry-server", "version": "1.0.0"}
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
                    "tools": TOOLS
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

import enum
import json
import os
import re
from typing import Dict, Any, Optional, List
from src.code_validator import validate_code_sample

class ApiVersion(str, enum.Enum):
    V2 = "v2"
    V2_4 = "v2.4"
    V3 = "v3"
    V3_0 = "v3.0"

# Formal Deprecation Registry across all SDK generations
DEPRECATION_REGISTRY = {
    "client.query": {
        "symbol": "client.query",
        "deprecated": True,
        "deprecated_in": "v2.4.0",
        "removed_in": "v3.0.0",
        "replacement": "client.search",
        "migration_note": "Method client.query() was renamed and removed in v3.0.0. Use client.search(query=..., timeout=10.0) where timeout is mandatory."
    },
    "request_body": {
        "symbol": "request_body",
        "deprecated": True,
        "deprecated_in": "v2.4.0",
        "removed_in": "v3.0.0",
        "replacement": "payload",
        "migration_note": "Parameter 'request_body' in client.send() was renamed to 'payload' in v3.0.0. Note default retry_backoff_ms was reduced from 1000ms to 500ms."
    },
    "client.query_paginated": {
        "symbol": "client.query_paginated",
        "deprecated": True,
        "deprecated_in": "v2.4.0",
        "removed_in": "v3.0.0",
        "replacement": "client.paginate",
        "migration_note": "Method client.query_paginated() was removed in v3.0.0. Use client.paginate(page_size=..., cursor=...)."
    },
    "old_ttl": {
        "symbol": "old_ttl",
        "deprecated": True,
        "deprecated_in": "v2.4.0",
        "removed_in": "v3.0.0",
        "replacement": "token_ttl",
        "migration_note": "Parameter 'old_ttl' in Auth.login() was replaced by 'token_ttl' (seconds)."
    },
    "old_token_renew": {
        "symbol": "old_token_renew",
        "deprecated": True,
        "deprecated_in": "v2.4.0",
        "removed_in": "v3.0.0",
        "replacement": "Auth.refresh_token",
        "migration_note": "Method 'old_token_renew' was removed in v3.0.0. Use 'Auth.refresh_token(refresh_token=...)'."
    },
    "/v2/legacy/batch": {
        "symbol": "/v2/legacy/batch",
        "deprecated": True,
        "deprecated_in": "v2.4.0",
        "removed_in": "v3.0.0",
        "replacement": "/v3/batch/process",
        "migration_note": "Endpoint '/v2/legacy/batch' was removed in v3.0.0. Use async endpoint '/v3/batch/process' via BatchProcessor.process()."
    },
    "client.execute_query": {
        "symbol": "client.execute_query",
        "deprecated": True,
        "deprecated_in": "v1.0.0",
        "removed_in": "v2.0.0",
        "replacement": "client.search (in v3) or client.query (in v2)",
        "migration_note": "Method 'client.execute_query' is an ancient dead API from v1.0, popular on Stack Overflow, removed in v2.0."
    }
}

# Formal Symbol Existence Matrix
SYMBOL_EXISTENCE_MATRIX = {
    "v2": {
        "client.query": {"exists": True, "mandatory": ["query"], "optional": ["timeout"], "status": "active_in_v2_deprecated_for_v3"},
        "client.send": {"exists": True, "mandatory": ["request_body"], "optional": ["retry_backoff_ms", "timeout"], "status": "active"},
        "client.query_paginated": {"exists": True, "mandatory": [], "optional": ["cursor", "limit"], "status": "active_in_v2_deprecated_for_v3"},
        "auth.login": {"exists": True, "mandatory": ["username", "password"], "optional": ["old_ttl"], "status": "active"},
        "auth.old_token_renew": {"exists": True, "mandatory": ["token"], "optional": [], "status": "active_in_v2_deprecated_for_v3"},
        "client.search": {"exists": False, "status": "not_introduced", "note": "Introduced in v3.0.0. Does not exist in v2.4."},
        "client.paginate": {"exists": False, "status": "not_introduced", "note": "Introduced in v3.0.0. Does not exist in v2.4."},
        "auth.refresh_token": {"exists": False, "status": "not_introduced", "note": "Introduced in v3.0.0. Does not exist in v2.4."},
        "client.execute_query": {"exists": False, "status": "removed_in_v2", "note": "Dead API from v1.0."}
    },
    "v3": {
        "client.search": {"exists": True, "mandatory": ["query", "timeout"], "optional": [], "status": "active"},
        "client.send": {"exists": True, "mandatory": ["payload"], "optional": ["retry_backoff_ms", "idempotency_key", "enable_compression"], "status": "active"},
        "client.paginate": {"exists": True, "mandatory": [], "optional": ["page_size", "cursor"], "status": "active"},
        "auth.login": {"exists": True, "mandatory": ["username", "password"], "optional": ["token_ttl"], "status": "active"},
        "auth.refresh_token": {"exists": True, "mandatory": ["refresh_token"], "optional": [], "status": "active"},
        "batchprocessor.process": {"exists": True, "mandatory": ["items"], "optional": ["async_mode"], "status": "active"},
        "streamclient.connect": {"exists": True, "mandatory": ["stream_id"], "optional": ["heartbeat_sec"], "status": "active"},
        "webhookhandler.verify": {"exists": True, "mandatory": ["payload", "signature"], "optional": [], "status": "active"},
        "errorhandler.catch": {"exists": True, "mandatory": ["error_payload"], "optional": [], "status": "active"},
        "client.query": {"exists": False, "status": "removed_in_v3", "replacement": "client.search", "note": "Removed in v3.0.0. Use client.search(query=..., timeout=10.0)."},
        "client.query_paginated": {"exists": False, "status": "removed_in_v3", "replacement": "client.paginate", "note": "Removed in v3.0.0. Use client.paginate()."},
        "auth.old_token_renew": {"exists": False, "status": "removed_in_v3", "replacement": "Auth.refresh_token", "note": "Removed in v3.0.0. Use Auth.refresh_token()."},
        "client.execute_query": {"exists": False, "status": "dead_api", "replacement": "client.search", "note": "Dead v1 API from 2018 Stack Overflow answers."}
    }
}

# Cached retriever instance for fast in-process searches
_CACHED_RETRIEVER = None

def get_shared_retriever():
    global _CACHED_RETRIEVER
    if _CACHED_RETRIEVER is None:
        from src.ingest import load_docs
        from src.chunkers import StructureAwareChunker
        from src.retriever import Retriever
        
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "docs")
        if not os.path.exists(docs_dir):
            docs_dir = "data/docs"
        docs = load_docs(docs_dir)
        chunker = StructureAwareChunker()
        all_chunks = []
        for d in docs:
            all_chunks.extend(chunker.chunk_document(d))
        _CACHED_RETRIEVER = Retriever(all_chunks, mode="hybrid")
    return _CACHED_RETRIEVER

def search_docs(query: str, api_version: str = "v3", top_k: int = 3) -> Dict[str, Any]:
    """
    Tool 1: Version-scoped doc search against active SDK reference documentation chunks.
    Filters exclusively on caller's SDK version family ('v2' or 'v3').
    """
    norm_ver = "v2" if "2" in str(api_version) else "v3"
    retriever = get_shared_retriever()
    
    # Strictly enforce metadata filtering by version
    results = retriever.search_hybrid(
        query=query,
        top_k=top_k,
        filters={"sdk_version": norm_ver}
    )
    
    formatted_results = []
    for r in results:
        # Create clickable versioned doc citation
        page_id = r["page_id"]
        anchor = r["chunk_id"].split("#")[-1] if "#" in r["chunk_id"] else "overview"
        source_rel = os.path.relpath(r["source_file"], "data/docs") if "source_file" in r else f"{norm_ver}/{page_id}.md"
        version_tag = "v2.4" if norm_ver == "v2" else "v3.0"
        citation_str = f"[{version_tag}/{source_rel}#{anchor}]"
        
        formatted_results.append({
            "chunk_id": r["chunk_id"],
            "page_id": page_id,
            "sdk_version": norm_ver,
            "version_tag": version_tag,
            "citation": citation_str,
            "content": r["content"],
            "score": r.get("score", 1.0)
        })

    return {
        "tool": "search_docs",
        "api_version": norm_ver,
        "query": query,
        "count": len(formatted_results),
        "results": formatted_results
    }

def check_deprecation(symbol: str, api_version: str = "v2.4") -> Dict[str, Any]:
    """
    Tool 2: Changelog/deprecation lookup. Checks whether symbol or parameter is deprecated
    and retrieves its removal version, replacement method, and migration note.
    """
    clean_sym = symbol.strip().lower()
    match = None
    for k, info in DEPRECATION_REGISTRY.items():
        if k in clean_sym or clean_sym in k or clean_sym.endswith(k.split(".")[-1]):
            match = info
            break
            
    if match:
        return {
            "tool": "check_deprecation",
            "symbol": symbol,
            "is_deprecated": True,
            "deprecated_in": match["deprecated_in"],
            "removed_in": match["removed_in"],
            "replacement": match["replacement"],
            "migration_note": match["migration_note"]
        }
    return {
        "tool": "check_deprecation",
        "symbol": symbol,
        "is_deprecated": False,
        "deprecated_in": None,
        "removed_in": None,
        "replacement": None,
        "migration_note": f"Symbol '{symbol}' is active with no recorded deprecation notice."
    }

def check_symbol_exists(symbol: str, api_version: str = "v3") -> Dict[str, Any]:
    """
    Tool 3: Symbol-exists check against caller's SDK version.
    Determines whether a method, parameter, or class exists in that version.
    """
    norm_ver = "v2" if "2" in str(api_version) else "v3"
    clean_sym = symbol.strip().lower()
    matrix = SYMBOL_EXISTENCE_MATRIX.get(norm_ver, {})
    
    match = None
    for k, info in matrix.items():
        if k in clean_sym or clean_sym in k or clean_sym.endswith(k.split(".")[-1]):
            match = (k, info)
            break
            
    if match:
        k, info = match
        return {
            "tool": "check_symbol_exists",
            "symbol": k,
            "api_version": norm_ver,
            "exists": info.get("exists", False),
            "status": info.get("status", "active"),
            "mandatory_args": info.get("mandatory", []),
            "optional_args": info.get("optional", []),
            "replacement": info.get("replacement"),
            "note": info.get("note", "")
        }
        
    # Default fallback: check if known in other version
    other_ver = "v3" if norm_ver == "v2" else "v2"
    other_matrix = SYMBOL_EXISTENCE_MATRIX.get(other_ver, {})
    for k, info in other_matrix.items():
        if k in clean_sym or clean_sym in k:
            if norm_ver == "v2":
                return {
                    "tool": "check_symbol_exists",
                    "symbol": k,
                    "api_version": norm_ver,
                    "exists": False,
                    "status": "not_introduced",
                    "note": f"Symbol '{k}' was introduced in {other_ver}. It DOES NOT exist in {norm_ver}."
                }
            else:
                return {
                    "tool": "check_symbol_exists",
                    "symbol": k,
                    "api_version": norm_ver,
                    "exists": False,
                    "status": "removed",
                    "note": f"Symbol '{k}' was a legacy method in {other_ver}. It DOES NOT exist in {norm_ver}."
                }

    return {
        "tool": "check_symbol_exists",
        "symbol": symbol,
        "api_version": norm_ver,
        "exists": True,
        "status": "unknown_assumed_valid",
        "mandatory_args": [],
        "optional_args": [],
        "note": "Symbol not in deprecation matrix; assumed standard active symbol."
    }

def get_openapi_spec(endpoint: str, api_version: str = "v3") -> Dict[str, Any]:
    """Retrieve OpenAPI spec for endpoint."""
    norm_ver = "v2" if "2" in str(api_version) else "v3"
    from mcp_servers.docs_server import OPENAPI_SPECS
    specs = OPENAPI_SPECS.get(norm_ver, OPENAPI_SPECS.get("v3", {}))
    spec = specs.get(endpoint)
    if not spec:
        for ep, sp in specs.items():
            if endpoint in ep or ep in endpoint:
                spec = sp
                endpoint = ep
                break
    return {"tool": "get_openapi_spec", "api_version": norm_ver, "endpoint": endpoint, "status": "found" if spec else "not_found", "spec": spec}

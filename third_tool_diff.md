# Third Tool Description Diff & Enum Parameter Specification

## Tool Definition

```python
class ApiVersion(str, enum.Enum):
    V2 = "v2"
    V3 = "v3"

def check_deprecation(endpoint: str, api_version: ApiVersion = ApiVersion.V3) -> Dict[str, Any]:
    """Query the SDK deprecation registry to check if an endpoint or method symbol is deprecated in a specific API version and retrieve its migration replacement."""
```

## Description Diff & Overlap Audit

```diff
- search_docs: "Search developer documentation articles by keyword query to locate parameter definitions, usage guides, and code examples for a specific API version."
- get_openapi_spec: "Retrieve the raw JSON OpenAPI 3.0 endpoint schema specification including request bodies, response schemas, and parameter types."
+ check_deprecation: "Query the SDK deprecation registry to check if an endpoint or method symbol is deprecated in a specific API version and retrieve its migration replacement."
```

### Single Job & Non-Overlap Verification:
1. **Single Job**: `check_deprecation` strictly queries the deprecation registry for breaking changes and replacement symbols.
2. **Enum Enforcement**: Parameter `api_version` uses strongly typed `ApiVersion` (`v2` | `v3`), preventing illegal string inputs.
3. **Zero Description Overlap**: `search_docs` performs keyword doc search; `get_openapi_spec` returns schema structures; `check_deprecation` exclusively returns deprecation lifecycle metadata.

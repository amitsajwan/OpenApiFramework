import yaml

def load_openapi_spec(file_path):
    """Load OpenAPI spec from YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def extract_api_details(openapi_spec):
    """Extract API details including paths, methods, and schemas."""
    api_map = {}
    base_url = openapi_spec.get("servers", [{}])[0].get("url", "")
    for path, methods in openapi_spec.get("paths", {}).items():
        for method, details in methods.items():
            api_key = f"{method.upper()} {path}"
            api_map[api_key] = {
                "summary": details.get("summary", ""),
                "parameters": details.get("parameters", []),
                "requestBody": details.get("requestBody", {}),
                "responses": details.get("responses", {})
            }
    return base_url, api_map

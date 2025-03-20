import yaml
import os

class OpenAPIParser:
    def __init__(self, openapi_file: str):
        """
        Initialize with the path to the OpenAPI YAML file.
        """
        self.openapi_file = openapi_file
        self.api_map = {}  # Caches API details
        self.schema_definitions = {}  # Stores schema references

    def load_openapi_spec(self):
        """
        Loads and parses the OpenAPI YAML file.
        """
        if not os.path.exists(self.openapi_file):
            raise FileNotFoundError(f"OpenAPI spec not found: {self.openapi_file}")

        with open(self.openapi_file, "r", encoding="utf-8") as file:
            spec = yaml.safe_load(file)

        self.schema_definitions = spec.get("components", {}).get("schemas", {})  # Extract reusable schemas
        return spec

    def extract_api_endpoints(self):
        """
        Extracts API endpoints and request details (methods, parameters, request body).
        """
        spec = self.load_openapi_spec()
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                operation_id = details.get("operationId", f"{method.upper()} {path}")
                self.api_map[operation_id] = {
                    "method": method.upper(),
                    "path": path,
                    "parameters": details.get("parameters", []),
                    "request_body": self.extract_request_body(details),
                }

    def extract_request_body(self, details):
        """
        Extracts request body, resolving `$ref` if present.
        """
        request_body = details.get("requestBody", {}).get("content", {}).get("application/json", {})
        schema = request_body.get("schema", {})

        if "$ref" in schema:
            ref_key = schema["$ref"].split("/")[-1]
            return self.resolve_schema(ref_key)
        return self.extract_example_payload(schema)

    def resolve_schema(self, schema_name):
        """
        Resolves `$ref` schema references recursively.
        """
        schema = self.schema_definitions.get(schema_name, {})
        resolved_schema = {}

        for key, value in schema.get("properties", {}).items():
            if "$ref" in value:
                ref_key = value["$ref"].split("/")[-1]
                resolved_schema[key] = self.resolve_schema(ref_key)
            elif "enum" in value:
                resolved_schema[key] = value["enum"][0]  # Use the first enum value
            else:
                resolved_schema[key] = self.extract_example_payload(value)

        return resolved_schema

    def extract_example_payload(self, schema):
        """
        Generates an example payload based on schema properties.
        """
        if "example" in schema:
            return schema["example"]
        elif schema.get("type") == "string":
            return "sample_string"
        elif schema.get("type") == "integer":
            return 123
        elif schema.get("type") == "boolean":
            return True
        elif schema.get("type") == "array":
            return [self.extract_example_payload(schema.get("items", {}))]
        elif schema.get("type") == "object":
            return {k: self.extract_example_payload(v) for k, v in schema.get("properties", {}).items()}
        return None  # Default case

    def get_all_endpoints(self):
        """
        Returns all extracted API endpoints as a structured dictionary.
        """
        if not self.api_map:
            self.extract_api_endpoints()
        return self.api_map


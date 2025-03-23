import yaml
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

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

        try:
            with open(self.openapi_file, "r", encoding="utf-8") as file:
                spec = yaml.safe_load(file)
                self.schema_definitions = spec.get("components", {}).get("schemas", {})
                self.api_map = spec.get("paths", {})
                logging.info("OpenAPI spec loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load OpenAPI spec: {e}")
            self.schema_definitions = {}
            self.api_map = {}

    def extract_api_endpoints(self):
        """
        Extracts API endpoints and request details (methods, parameters, request body).
        """
        if not self.api_map:
            self.load_openapi_spec()

        extracted_endpoints = {}
        for path, methods in self.api_map.items():
            for method, details in methods.items():
                operation_id = details.get("operationId", f"{method.upper()} {path}")
                extracted_endpoints[operation_id] = {
                    "method": method.upper(),
                    "path": path,
                    "parameters": details.get("parameters", []),
                    "request_body": self.extract_request_body(details),
                }
        return extracted_endpoints

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

    def resolve_schema(self, schema_name, depth=0):
        """
        Recursively resolves OpenAPI `$ref` schema references, `allOf`, `oneOf`, and `anyOf`.

        :param schema_name: The schema name to resolve.
        :param depth: Recursion depth to prevent infinite loops.
        :return: The fully resolved schema.
        """
        if depth > 10:  # Prevent infinite loops
            return {}

        schema = self.schema_definitions.get(schema_name, {})
        resolved_schema = {}

        # Handle `allOf` - Merge all schemas
        if "allOf" in schema:
            for subschema in schema["allOf"]:
                ref_key = subschema.get("$ref", "").split("/")[-1] if "$ref" in subschema else None
                resolved_part = self.resolve_schema(ref_key, depth + 1) if ref_key else subschema
                resolved_schema.update(resolved_part)

        # Handle `oneOf` and `anyOf` - Pick the first valid schema
        elif "oneOf" in schema or "anyOf" in schema:
            options = schema.get("oneOf", schema.get("anyOf", []))
            ref_key = options[0].get("$ref", "").split("/")[-1] if options and "$ref" in options[0] else None
            return self.resolve_schema(ref_key, depth + 1) if ref_key else options[0]

        # Process `properties`
        if "properties" in schema:
            for key, value in schema["properties"].items():
                if "$ref" in value:
                    ref_key = value["$ref"].split("/")[-1]
                    resolved_schema[key] = self.resolve_schema(ref_key, depth + 1)
                elif "enum" in value:
                    resolved_schema[key] = value["enum"][0]  # Pick first enum value
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
        return self.extract_api_endpoints()

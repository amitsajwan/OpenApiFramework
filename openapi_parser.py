import yaml
import os

class OpenAPIParser:
    def __init__(self, openapi_file: str):
        """Initialize with the path to the OpenAPI YAML file."""
        self.openapi_file = openapi_file
        self.api_map = {}
        self.schema_definitions = {}

    def load_openapi_spec(self):
        """Loads and parses the OpenAPI YAML file with error handling."""
        if not os.path.exists(self.openapi_file):
            raise FileNotFoundError(f"OpenAPI spec not found: {self.openapi_file}")

        try:
            with open(self.openapi_file, "r", encoding="utf-8") as file:
                spec = yaml.safe_load(file)
                self.api_map = spec.get("paths", {})
                self.schema_definitions = spec.get("components", {}).get("schemas", {})
                return spec
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {self.openapi_file}: {e}")

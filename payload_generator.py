import random
import string

def generate_random_value(schema):
    """Generate example values for a given schema."""
    if "type" in schema:
        if schema["type"] == "string":
            return ''.join(random.choices(string.ascii_letters, k=8))
        elif schema["type"] == "integer":
            return random.randint(1, 100)
        elif schema["type"] == "boolean":
            return random.choice([True, False])
        elif schema["type"] == "array":
            return [generate_random_value(schema["items"]) for _ in range(2)]
        elif schema["type"] == "object":
            return {key: generate_random_value(value) for key, value in schema["properties"].items()}
    return None

def generate_payload(api_details):
    """Generate a valid payload from OpenAPI schema."""
    request_body = api_details.get("requestBody", {})
    if "content" in request_body:
        for content_type, content_schema in request_body["content"].items():
            if "schema" in content_schema:
                return generate_random_value(content_schema["schema"])
    return {}

import random
import string

def resolve_ref(schema, components):
    """Recursively resolve $ref references in OpenAPI schemas."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"].split("/")[-1]
            if ref_path in components:
                return resolve_ref(components[ref_path], components)  # Recursively resolve
            else:
                return {"error": f"Unresolved reference: {ref_path}"}
        else:
            return {key: resolve_ref(value, components) for key, value in schema.items()}
    elif isinstance(schema, list):
        return [resolve_ref(item, components) for item in schema]
    return schema

def generate_example_value(schema):
    """Generate realistic example values based on schema type."""
    if "enum" in schema:
        return random.choice(schema["enum"])
    elif schema.get("type") == "string":
        return "".join(random.choices(string.ascii_letters, k=8))
    elif schema.get("type") == "integer":
        return random.randint(1, 100)
    elif schema.get("type") == "boolean":
        return random.choice([True, False])
    return None

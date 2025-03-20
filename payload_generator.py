import random
import string

def resolve_ref(schema, components):
    """Recursively resolve $ref references in OpenAPI schemas."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"].split("/")[-1]
            resolved = components.get(ref_path, {})
            return resolve_ref(resolved, components)  # Recursively resolve
        else:
            return {key: resolve_ref(value, components) for key, value in schema.items()}
    elif isinstance(schema, list):
        return [resolve_ref(item, components) for item in schema]
    return schema

def generate_example_value(schema):
    """Generate realistic example values based on schema type."""
    if "enum" in schema:
        return random.choice(schema["enum"])
    
    schema_type = schema.get("type", "")
    
    if schema_type == "string":
        return ''.join(random.choices(string.ascii_letters, k=8))
    elif schema_type == "integer":
        return random.randint(1, 100)
    elif schema_type == "boolean":
        return random.choice([True, False])
    elif schema_type == "array":
        item_schema = schema.get("items", {})
        return [generate_example_value(item_schema)]
    elif schema_ty

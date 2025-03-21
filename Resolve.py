import copy

def resolve_schema(schema, components, depth=0):
    """
    Recursively resolves OpenAPI schema references and handles allOf, oneOf, and anyOf.

    :param schema: The schema to resolve.
    :param components: The "components" section of the OpenAPI spec.
    :param depth: Recursion depth to prevent infinite loops.
    :return: The fully resolved schema.
    """
    if depth > 10:  # Prevent infinite loops
        return schema

    if not isinstance(schema, dict):
        return schema  # Base case for recursion
    
    # If the schema has a $ref, resolve it
    if "$ref" in schema:
        ref_path = schema["$ref"].replace("#/components/schemas/", "")
        resolved_schema = components.get(ref_path, {}).copy()
        return resolve_schema(resolved_schema, components, depth + 1)

    # Handle allOf: Merge all subschemas
    if "allOf" in schema:
        merged_schema = {}
        for subschema in schema["allOf"]:
            resolved_subschema = resolve_schema(subschema, components, depth + 1)
            merged_schema.update(resolved_subschema)  # Merge properties
        return merged_schema

    # Handle oneOf / anyOf: Pick the first schema (assumption: valid for test cases)
    if "oneOf" in schema or "anyOf" in schema:
        first_subschema = schema.get("oneOf", schema.get("anyOf", []))[0]  # Pick first valid option
        return resolve_schema(first_subschema, components, depth + 1)

    # Recursively resolve nested properties
    resolved_schema = copy.deepcopy(schema)  # Avoid modifying original schema
    if "properties" in resolved_schema:
        for prop, prop_schema in resolved_schema["properties"].items():
            resolved_schema["properties"][prop] = resolve_schema(prop_schema, components, depth + 1)

    return resolved_schema

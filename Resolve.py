def resolve_schema(self, schema_name, depth=0):
    """
    Recursively resolves OpenAPI `$ref` schema references, `allOf`, `oneOf`, and `anyOf`.

    :param schema_name: The schema name to resolve.
    :param depth: Recursion depth to prevent infinite loops.
    :return: The fully resolved schema.
    """
    if depth > 10:  # Prevent infinite loops
        return {}

    # Fetch schema definition
    schema = self.schema_definitions.get(schema_name, {})
    resolved_schema = {}

    # If schema has 'allOf', merge all subschemas
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            ref_key = subschema.get("$ref", "").split("/")[-1] if "$ref" in subschema else None
            resolved_part = self.resolve_schema(ref_key, depth + 1) if ref_key else self.extract_example_payload(subschema)
            resolved_schema.update(resolved_part)  # Merge properties

    # Handle `oneOf` and `anyOf`: Pick the first valid schema
    elif "oneOf" in schema or "anyOf" in schema:
        options = schema.get("oneOf", schema.get("anyOf", []))
        ref_key = options[0].get("$ref", "").split("/")[-1] if options and "$ref" in options[0] else None
        return self.resolve_schema(ref_key, depth + 1) if ref_key else self.extract_example_payload(options[0])

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

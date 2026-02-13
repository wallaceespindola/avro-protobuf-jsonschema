"""
JSON Schema standalone example: schema + validate JSON

Install: pip install jsonschema
"""

from jsonschema import Draft202012Validator


def main() -> None:
    """Demonstrate JSON Schema validation."""

    # Define the JSON Schema
    USER_SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "name": {"type": "string", "minLength": 1},
            "email": {"type": ["string", "null"], "format": "email"},
            "is_active": {"type": "boolean"},
        },
        "required": ["id", "name", "is_active"],
    }

    # Valid user
    valid_user = {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}

    # Invalid user (multiple validation errors)
    invalid_user = {"id": 0, "name": "", "is_active": "yes"}  # < 1  # empty string  # wrong type

    validator = Draft202012Validator(USER_SCHEMA)

    # Validate valid user
    print("✅ Validating valid user:")
    if validator.is_valid(valid_user):
        print("  Valid! ✓")
        print(f"  {valid_user}")
    print()

    # Validate invalid user
    print("❌ Validating invalid user:")
    errors = sorted(validator.iter_errors(invalid_user), key=lambda e: e.path)

    if errors:
        print(f"  Found {len(errors)} validation errors:")
        for e in errors:
            path = ".".join([str(p) for p in e.path]) or "<root>"
            print(f"  - {path}: {e.message}")
    print()

    print("💡 JSON Schema is commonly used with REST APIs and OpenAPI/Swagger")


if __name__ == "__main__":
    main()

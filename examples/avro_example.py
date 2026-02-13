"""
Avro standalone example: schema + serialize/deserialize

Install: pip install fastavro
"""

from io import BytesIO

from fastavro import parse_schema, reader, writer


def main() -> None:
    """Demonstrate Avro serialization and deserialization."""

    # Define the Avro schema
    USER_SCHEMA = {
        "type": "record",
        "name": "User",
        "namespace": "com.example",
        "fields": [
            {"name": "id", "type": "long"},
            {"name": "name", "type": "string"},
            {"name": "email", "type": ["null", "string"], "default": None},
            {"name": "is_active", "type": "boolean", "default": True},
        ],
    }

    parsed_schema = parse_schema(USER_SCHEMA)

    # Create sample records
    records = [
        {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True},
        {"id": 2, "name": "Nia", "email": None, "is_active": False},
    ]

    # Serialize to Avro binary
    buf = BytesIO()
    writer(buf, parsed_schema, records)
    avro_bytes = buf.getvalue()

    print(f"✅ Serialized {len(records)} records to Avro")
    print(f"📦 Avro bytes length: {len(avro_bytes)} bytes")
    print()

    # Deserialize from Avro binary
    buf2 = BytesIO(avro_bytes)
    decoded = list(reader(buf2))

    print("✅ Deserialized records:")
    for record in decoded:
        print(
            f"  - ID: {record['id']}, Name: {record['name']}, Email: {record['email']}, "
            f"Active: {record['is_active']}"
        )
    print()

    print("💡 Note: For streaming systems (Kafka), Avro is commonly paired with a schema registry")


if __name__ == "__main__":
    main()

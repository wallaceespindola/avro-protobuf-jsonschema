"""
Test Avro endpoint - Python client

Prerequisites:
1. Install: pip install requests fastavro
2. Start server: make run
"""

import sys
from io import BytesIO

import requests
from fastavro import parse_schema, schemaless_reader, schemaless_writer


def main() -> None:
    """Test the Avro endpoint."""

    # Define schema (must match server schema)
    schema = parse_schema(
        {
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
    )

    # Create user record
    user = {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}

    # Serialize to Avro
    buf = BytesIO()
    schemaless_writer(buf, schema, user)
    payload = buf.getvalue()

    print(f"📤 Sending Avro message ({len(payload)} bytes)...")
    print(f"  {user}")
    print()

    # Send to endpoint
    try:
        r = requests.post(
            "http://127.0.0.1:8000/avro/user",
            data=payload,
            headers={"Content-Type": "application/avro"},
            timeout=5,
        )
        r.raise_for_status()

        print(f"✅ Response received ({r.status_code})")
        print(f"📥 Response size: {len(r.content)} bytes")
        print()

        # Deserialize response
        decoded = schemaless_reader(BytesIO(r.content), schema)

        print("Decoded response:")
        print(f"  ID: {decoded['id']}")
        print(f"  Name: {decoded['name']}")
        print(f"  Email: {decoded['email']}")
        print(f"  Active: {decoded['is_active']}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("Make sure the server is running: make run")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

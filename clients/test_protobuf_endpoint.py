"""
Test Protobuf endpoint - Python client

Prerequisites:
1. Install: pip install requests protobuf
2. Generate protobuf code: make proto
3. Start server: make run
"""

import sys
from pathlib import Path

import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from schemas import user_pb2
except ImportError:
    print("❌ Error: Protobuf module not generated.")
    print("Run 'make proto' or './generate_proto.sh' first")
    sys.exit(1)


def main() -> None:
    """Test the Protobuf endpoint."""

    # Create a User message
    u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)

    # Serialize to binary
    data = u.SerializeToString()

    print(f"📤 Sending Protobuf message ({len(data)} bytes)...")
    print(f"  ID: {u.id}, Name: {u.name}, Email: {u.email}, Active: {u.is_active}")
    print()

    # Send to endpoint
    try:
        r = requests.post(
            "http://127.0.0.1:8000/protobuf/user",
            data=data,
            headers={"Content-Type": "application/x-protobuf"},
            timeout=5,
        )
        r.raise_for_status()

        print(f"✅ Response received ({r.status_code})")
        print(f"📥 Response size: {len(r.content)} bytes")
        print()

        # Deserialize response
        u2 = user_pb2.User()
        u2.ParseFromString(r.content)

        print("Decoded response:")
        print(f"  ID: {u2.id}")
        print(f"  Name: {u2.name}")
        print(f"  Email: {u2.email}")
        print(f"  Active: {u2.is_active}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("Make sure the server is running: make run")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

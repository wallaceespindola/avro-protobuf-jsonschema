"""
Protobuf standalone example: .proto + serialize/deserialize

Prerequisites:
1. Install protobuf: pip install protobuf
2. Generate Python code: make proto (or ./generate_proto.sh)
"""

import sys
from pathlib import Path

# Add parent directory to path to import generated protobuf
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from schemas import user_pb2
except ImportError:
    print("❌ Error: Protobuf module not generated.")
    print("Run 'make proto' or './generate_proto.sh' first")
    sys.exit(1)


def main() -> None:
    """Demonstrate Protobuf serialization and deserialization."""

    # Create a User message
    u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)

    # Serialize to binary
    data = u.SerializeToString()

    print("✅ Serialized User to Protobuf")
    print(f"📦 Protobuf bytes length: {len(data)} bytes")
    print()

    # Deserialize from binary
    u2 = user_pb2.User()
    u2.ParseFromString(data)

    print("✅ Deserialized User:")
    print(f"  - ID: {u2.id}")
    print(f"  - Name: {u2.name}")
    print(f"  - Email: {u2.email}")
    print(f"  - Active: {u2.is_active}")
    print()

    print("💡 Note on presence: proto3 uses defaults; use 'optional' for true field presence")


if __name__ == "__main__":
    main()

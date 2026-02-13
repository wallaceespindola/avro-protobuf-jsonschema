#!/bin/bash
# Generate Python code from Protobuf schema
# Requires protoc to be installed: brew install protobuf (macOS) or apt-get install protobuf-compiler (Linux)

if ! command -v protoc &> /dev/null; then
    echo "Error: protoc not found. Please install Protocol Buffers compiler:"
    echo "  macOS: brew install protobuf"
    echo "  Linux: apt-get install protobuf-compiler"
    echo "  Or download from: https://github.com/protocolbuffers/protobuf/releases"
    exit 1
fi

echo "Generating Python code from schemas/user.proto..."
protoc --python_out=. --pyi_out=. schemas/user.proto

if [ $? -eq 0 ]; then
    echo "Successfully generated schemas/user_pb2.py and schemas/user_pb2.pyi"
else
    echo "Error generating Protobuf code"
    exit 1
fi

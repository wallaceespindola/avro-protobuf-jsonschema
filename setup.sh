#!/bin/bash
# Quick setup script for schemas-demo project

set -e

echo "🚀 Setting up Schemas Demo project..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo "⚠️  protoc is not installed. Protobuf features will not be available."
    echo "Install with:"
    echo "  macOS: brew install protobuf"
    echo "  Linux: apt-get install protobuf-compiler"
    echo ""
    PROTOC_AVAILABLE=false
else
    echo "✅ protoc is installed"
    PROTOC_AVAILABLE=true
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install -r requirements.txt

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from .env.example..."
    cp .env .env
    echo "✅ Created .env file. Please edit it with your information."
else
    echo ""
    echo "ℹ️  .env file already exists, skipping creation."
fi

# Generate Protobuf code if protoc is available
if [ "$PROTOC_AVAILABLE" = true ]; then
    echo ""
    echo "🔧 Generating Protobuf Python code..."
    ./generate_proto.sh
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your author information"
echo "  2. Activate virtual environment: source .venv/bin/activate"
echo "  3. Run the server: make run"
echo "  4. Visit http://localhost:8000/docs"
echo ""

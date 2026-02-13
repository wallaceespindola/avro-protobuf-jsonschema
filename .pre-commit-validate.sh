#!/bin/bash
# Pre-commit configuration validation script
# This script validates the .pre-commit-config.yaml file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.pre-commit-config.yaml"

echo "================================"
echo "Pre-commit Configuration Check"
echo "================================"
echo ""

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

echo "✓ Configuration file found"
echo ""

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "⚠️  pre-commit is not installed"
    echo "Install with: pip install pre-commit"
    exit 1
fi

echo "✓ pre-commit is installed"
pre-commit --version
echo ""

# Validate configuration
echo "Validating configuration..."
if pre-commit validate-config "$CONFIG_FILE"; then
    echo "✓ Configuration is valid"
else
    echo "❌ Configuration validation failed"
    exit 1
fi

echo ""
echo "================================"
echo "Configuration check complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Install hooks: bash .pre-commit-setup.sh"
echo "2. Run all hooks: pre-commit run --all-files"
echo ""

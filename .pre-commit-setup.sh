#!/bin/bash
# Setup script for pre-commit hooks
# This script installs and initializes pre-commit hooks for the project

set -e

echo "================================"
echo "Setting up Pre-commit Hooks"
echo "================================"
echo ""

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "❌ pre-commit is not installed"
    echo "Installing pre-commit..."
    pip install pre-commit
else
    echo "✓ pre-commit is already installed"
fi

echo ""
echo "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type pre-push

echo ""
echo "Running pre-commit on all files (first run)..."
pre-commit run --all-files || true

echo ""
echo "================================"
echo "Pre-commit setup complete!"
echo "================================"
echo ""
echo "Usage:"
echo "  • Hooks will run automatically on 'git commit'"
echo "  • To run manually: pre-commit run --all-files"
echo "  • To skip hooks: git commit --no-verify"
echo "  • To update hooks: pre-commit autoupdate"
echo ""

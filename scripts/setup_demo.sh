#!/bin/bash
# Setup script for math-trace demo
# Installs dependencies and builds the example paper

set -e

echo "🚀 Setting up math-trace..."
echo ""

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Python $PYTHON_VERSION ✓"

# Check uv
echo "📦 Checking uv..."
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing from pip..."
    python3 -m pip install uv
fi
echo "   uv installed ✓"

# Check Typst
echo "📦 Checking Typst..."
if ! command -v typst &> /dev/null; then
    echo "⚠️  Typst not found."
    echo "   Install with: cargo install typst-cli"
    echo "   Or download from: https://github.com/typst/typst/releases"
    read -p "   Continue without Typst? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "   Typst installed ✓"
fi

# Install Python dependencies
echo ""
echo "📚 Installing Python dependencies..."
uv sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. cd examples/membrane-dynamics"
echo "  2. just paper     # Build the example paper"
echo ""
echo "Or see: README.md for more options"

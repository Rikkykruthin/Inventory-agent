#!/bin/bash
# Setup script for Inventory Agent System

echo "🚀 Setting up Inventory Agent System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -e .

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "   Please create .env from .env.example and add your ANTHROPIC_API_KEY"
    echo ""
    echo "   Run: cp .env.example .env"
    echo "   Then edit .env and add your API key"
else
    echo "✅ .env file found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Set your API key in .env file"
echo "  3. Run CLI demo: python main.py"
echo ""

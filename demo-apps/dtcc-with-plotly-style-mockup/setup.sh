#!/bin/bash

# DTCC OpenBB Dashboard System - Setup Script
echo "🚀 Setting up DTCC OpenBB Dashboard System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🧪 Running verification..."
python verify_installation.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 To start the DTCC Dashboard System:"
    echo "   1. Activate virtual environment: source venv/bin/activate"
    echo "   2. Start server: uvicorn main:app --reload --port 8000"
    echo "   3. Open browser: http://localhost:8000"
else
    echo ""
    echo "❌ Verification failed. Please check the errors above."
    exit 1
fi
echo ""
echo "📊 Available endpoints:"
echo "   • Widgets JSON: http://localhost:8000/widgets.json"
echo "   • Apps JSON: http://localhost:8000/apps.json"
echo "   • Example widget: http://localhost:8000/market_surveillance/activity_metrics"
echo ""
echo "🌟 Ready for OpenBB Workspace integration!"
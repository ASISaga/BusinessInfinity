#!/bin/bash
# BusinessInfinity MVP Startup Script

echo "🚀 Starting BusinessInfinity MVP..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ to continue."
    exit 1
fi

# Check Python version
python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $python_version"

# Run MVP tests
echo "🧪 Running MVP tests..."
if python mvp_test.py; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🎉 MVP is ready to launch!"
echo ""
echo "Starting server in 3 seconds..."
sleep 3

# Start the server
python mvp_server.py
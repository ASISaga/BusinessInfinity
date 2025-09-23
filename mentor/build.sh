#!/bin/bash

# Build script for Business Infinity Mentor Mode VS Code Extension

echo "🔨 Building Business Infinity Mentor Mode Extension..."

# Check if we're in the mentor directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the mentor directory"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --no-package-lock
fi

# Compile TypeScript
echo "🔧 Compiling TypeScript..."
npm run compile

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Open VS Code"
    echo "  2. Go to Extensions view (Ctrl+Shift+X)"
    echo "  3. Click ... menu → Install from VSIX"
    echo "  4. Or use: code --install-extension <path-to-vsix-file>"
    echo ""
    echo "🔧 Available commands (use Ctrl+Shift+P):"
    echo "  - Mentor Mode: Manage Mentor Mode"
    echo "  - Mentor Mode: List Business Agents"
    echo "  - Mentor Mode: Chat with Agent"
    echo "  - Mentor Mode: Fine Tune Agent LoRA"
    echo "  - Mentor Mode: View Training Logs"
    echo "  - Mentor Mode: Deploy LoRA Adapter"
    echo "  - Mentor Mode: Compare LoRA Versions"
else
    echo "❌ Build failed!"
    exit 1
fi
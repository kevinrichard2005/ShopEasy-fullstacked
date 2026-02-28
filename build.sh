#!/bin/bash
# ShopEasy Build Script for Render

echo "🚀 Starting ShopEasy build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating static directories..."
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p instance

# Copy CSS and JS files to static directories if they exist in root
echo "📋 Copying static assets..."
if [ -f "admin.css" ]; then
    cp admin.css static/css/ 2>/dev/null || echo "admin.css not found"
fi

if [ -f "responsive.css" ]; then
    cp responsive.css static/css/ 2>/dev/null || echo "responsive.css not found"
fi

if [ -f "script.js" ]; then
    cp script.js static/js/ 2>/dev/null || echo "script.js not found"
fi

# Create empty CSS files if they don't exist to prevent 404s
touch static/css/admin.css 2>/dev/null
touch static/css/responsive.css 2>/dev/null
touch static/js/script.js 2>/dev/null

echo "✅ Build completed successfully!"
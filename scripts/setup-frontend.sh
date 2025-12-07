#!/bin/bash

echo "🚀 Setting up Live Data RAG Frontend..."

# Install dependencies
npm install

# Create environment file
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_VERSION=1.0.0
EOF

echo "✅ Frontend setup complete!"
echo "📦 To start development server:"
echo "   npm run dev"
echo ""
echo "📦 To build for production:"
echo "   npm run build"
echo "   npm run preview"
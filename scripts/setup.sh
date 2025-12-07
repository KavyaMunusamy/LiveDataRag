#!/bin/bash

echo "🚀 Setting up Live Data RAG with Actions Project..."

# Create directory structure
mkdir -p frontend/public
mkdir -p frontend/src/{components/{Dashboard,RulesManager,QueryInterface,common},services,contexts,styles}
mkdir -p backend/src/{config,data_pipeline/{connectors},rag_engine,action_engine/{actions},monitoring,utils}

# Create all the files
echo "📁 Creating project files..."

# Frontend files
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Data RAG with Actions</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2220%22 fill=%22%231976d2%22/><path d=%22M30 30 L70 30 L70 45 L55 45 L55 70 L45 70 L45 45 L30 45 Z%22 fill=%22white%22/><circle cx=%2250%22 cy=%2220%22 r=%228%22 fill=%22%234caf50%22/><circle cx=%2220%22 cy=%2280%22 r=%226%22 fill=%22%23ff9800%22/><circle cx=%2280%22 cy=%2280%22 r=%226%22 fill=%22%23f44336%22/></svg>" type="image/svg+xml">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap">
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/index.js"></script>
</body>
</html>
EOF

echo "✅ Setup complete!"
echo "📦 Next steps:"
echo "1. cd backend && pip install -r requirements.txt"
echo "2. cd frontend && npm install"
echo "3. Set up your .env files with API keys"
echo "4. Run: docker-compose up --build"
# LiveDataRAG - Complete Setup Guide

## Prerequisites

Before starting, ensure you have:
- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Docker & Docker Compose** (for containerized setup)
- **Git** installed

## Setup Options

Choose one of these methods:

---

## Option 1: Docker Setup (Recommended - Easiest)

### Step 1: Clone and Navigate
```bash
cd LiveDataRAG
```

### Step 2: Create Environment File
Create `Backend/.env` file:
```bash
# Backend/.env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=live-data-rag

DATABASE_URL=postgresql://postgres:password@db:5432/live_rag
REDIS_URL=redis://redis:6379

# Optional: News API
NEWS_API_KEY=your_newsapi_key

# Optional: Financial Data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Optional: Notifications
SLACK_WEBHOOK_URL=your_slack_webhook
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Step 3: Create Prometheus Config
Create `infrastructure/prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

### Step 4: Start All Services
```bash
docker-compose up --build
```

This will start:
- Backend API (http://localhost:8000)
- Frontend (http://localhost:3000)
- PostgreSQL (localhost:5432)
- Redis (localhost:6379)
- Prometheus (http://localhost:9090)
- Grafana (http://localhost:3001)

### Step 5: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)

---

## Option 2: Local Development Setup (For Development)

### Backend Setup

#### Step 1: Navigate to Backend
```bash
cd Backend
```

#### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Create .env File
Create `Backend/.env` (same as Docker setup above)

#### Step 5: Start Required Services
You need PostgreSQL and Redis running. Use Docker:
```bash
# Start only database services
docker run -d -p 5432:5432 -e POSTGRES_DB=live_rag -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine

docker run -d -p 6379:6379 redis:7-alpine
```

#### Step 6: Run Backend
```bash
# From Backend directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

---

### Frontend Setup

#### Step 1: Navigate to Frontend
```bash
cd Frontend
```

#### Step 2: Install Dependencies
```bash
npm install
```

#### Step 3: Create Environment File
Create `Frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_VERSION=1.0.0
```

#### Step 4: Start Development Server
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173 (Vite default)

---

## Post-Setup Configuration

### 1. Setup Pinecone Vector Database

1. Sign up at https://www.pinecone.io/
2. Create a new index:
   - Name: `live-data-rag`
   - Dimensions: `384` (for sentence-transformers)
   - Metric: `cosine`
3. Copy API key and environment to `.env`

### 2. Setup OpenAI API

1. Get API key from https://platform.openai.com/
2. Add to `.env` file

### 3. Optional: Setup News API

1. Get free API key from https://newsapi.org/
2. Add to `.env` file

### 4. Optional: Setup Financial Data

1. Get free API key from https://www.alphavantage.co/
2. Add to `.env` file

---

## Verification Steps

### 1. Check Backend Health
```bash
curl http://localhost:8000/
```

Should return: `{"message": "Live Data RAG with Actions API"}`

### 2. Check API Documentation
Visit: http://localhost:8000/docs

### 3. Check Frontend
Visit: http://localhost:3000 (or 5173 for local dev)

### 4. Test WebSocket Connection
Open browser console on frontend and check for WebSocket connection messages

---

## Common Issues & Solutions

### Issue: Port Already in Use
**Solution**: Change ports in `docker-compose.yml` or stop conflicting services

### Issue: Database Connection Failed
**Solution**: Ensure PostgreSQL is running and credentials match `.env`

### Issue: Pinecone Connection Error
**Solution**: Verify API key and index name in `.env`

### Issue: Frontend Can't Connect to Backend
**Solution**: Check CORS settings and ensure backend is running

### Issue: Module Import Errors
**Solution**: 
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Running Tests
```bash
# Backend (when tests are added)
cd Backend
pytest

# Frontend (when tests are added)
cd Frontend
npm test
```

### Building for Production

#### Backend
```bash
docker build -t live-data-rag-backend ./Backend
```

#### Frontend
```bash
cd Frontend
npm run build
# Output in Frontend/dist
```

---

## Stopping the Application

### Docker Setup
```bash
docker-compose down

# To remove volumes (database data)
docker-compose down -v
```

### Local Development
- Press `Ctrl+C` in terminal running backend
- Press `Ctrl+C` in terminal running frontend
- Stop Docker containers for PostgreSQL and Redis

---

## Next Steps

1. **Create Your First Rule**: Go to Rules Manager in the UI
2. **Test a Query**: Use the Query Interface to ask questions
3. **Monitor System**: Check the Dashboard for system health
4. **Setup Data Streams**: Configure financial or news data streams
5. **Review Logs**: Check backend logs for any issues

---

## Getting Help

- Check API documentation: http://localhost:8000/docs
- Review logs: `docker-compose logs -f backend`
- Check system health: Dashboard → System Health

---

## Security Notes

⚠️ **Important for Production:**
- Change default PostgreSQL password
- Use strong secrets for JWT tokens
- Enable HTTPS/TLS
- Restrict CORS origins
- Use environment-specific `.env` files
- Never commit `.env` files to version control

# Quick Start - You're Almost There!

## What You Have:
✅ OpenAI API Key configured
✅ Virtual environment set up
✅ Dependencies partially installed

## What You Need:

### 1. Get Pinecone API Key (5 minutes)

1. Go to: https://www.pinecone.io/
2. Sign up (free tier is fine)
3. Click "Create Index":
   - Name: `live-data-rag`
   - Dimensions: `384`
   - Metric: `cosine`
4. Go to "API Keys" in dashboard
5. Copy your API key and environment

### 2. Update Backend/.env

Replace these two lines:
```
PINECONE_API_KEY=your_actual_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
```

Example:
```
PINECONE_API_KEY=pcsk_xxxxx_your_key
PINECONE_ENVIRONMENT=us-west1-gcp
```

### 3. Fix Missing Dependencies

Run this in your CMD (with venv activated):
```cmd
venv\Scripts\pip.exe install pydantic-settings==2.1.0
```

### 4. Start Services

**Option A: Docker (Easiest)**
```cmd
cd Backend
docker-compose up --build
```

**Option B: Manual**
```cmd
# Terminal 1: Start PostgreSQL
docker run -d --name postgres-liverag -p 5432:5432 -e POSTGRES_DB=live_rag -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine

# Terminal 2: Start Redis
docker run -d --name redis-liverag -p 6379:6379 redis:7-alpine

# Terminal 3: Start Backend
cd Backend
venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

### 5. Access the Application

- Backend API: http://localhost:8000/docs
- Test endpoint: http://localhost:8000/

---

## About Anthropic/Claude

**You DON'T need it!** 

- Anthropic = Company that makes Claude
- Claude = AI model (like GPT-4)
- You already have OpenAI (GPT), so you're good!

You can leave `ANTHROPIC_API_KEY=your_anthropic_api_key_here` as is - it's optional.

---

## Next Steps After Backend is Running

1. Open new terminal for Frontend:
```cmd
cd Frontend
npm install
npm run dev
```

2. Access frontend at: http://localhost:5173

---

## Need Help?

Check if backend is running:
```cmd
curl http://localhost:8000/
```

Should return: `{"message": "Live Data RAG with Actions API"}`

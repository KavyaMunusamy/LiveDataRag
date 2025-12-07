# Windows Setup Guide for LiveDataRAG

## Quick Fix for Your Current Issues

### Step 1: Install Missing Dependencies

Since you're using Python 3.13 and having compiler issues, let's install dependencies properly:

```cmd
cd Backend
venv\Scripts\activate
install_dependencies.bat
```

Or manually install the critical missing package:
```cmd
pip install pydantic-settings==2.1.0
```

### Step 2: Create .env File

The `.env` file has been created at `Backend/.env`. 

**IMPORTANT**: Edit this file and replace the placeholder values:
- `your_openai_api_key_here` → Your actual OpenAI API key
- `your_pinecone_api_key_here` → Your actual Pinecone API key
- `your_pinecone_environment` → Your Pinecone environment (e.g., "us-west1-gcp")

### Step 3: Start Required Services

You need PostgreSQL and Redis. Use Docker:

```cmd
docker run -d --name postgres-liverag -p 5432:5432 -e POSTGRES_DB=live_rag -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine

docker run -d --name redis-liverag -p 6379:6379 redis:7-alpine
```

### Step 4: Start Backend

```cmd
cd Backend
venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

---

## Alternative: Use Docker (Recommended)

If you have Docker Desktop installed, this is much easier:

### Step 1: Fix docker-compose.yml Path

The docker-compose.yml is in the Backend folder, so:

```cmd
cd Backend
docker-compose up --build
```

This will start everything automatically!

---

## Troubleshooting

### Issue: "No module named 'pydantic_settings'"
**Solution:**
```cmd
pip install pydantic-settings==2.1.0
```

### Issue: Numpy/Pandas build errors on Python 3.13
**Solution:** Use pre-built wheels:
```cmd
pip install --only-binary :all: numpy pandas
```

Or downgrade to Python 3.11:
```cmd
# Download Python 3.11 from python.org
# Create new venv with Python 3.11
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "docker-compose: no configuration file provided"
**Solution:** You need to be in the Backend directory:
```cmd
cd Backend
docker-compose up --build
```

### Issue: Can't set environment variables
**Windows doesn't use `VARIABLE=value` syntax in CMD.**

Instead, edit the `.env` file directly (already created for you).

---

## Recommended Setup Path

**Option A: Docker (Easiest)**
1. Install Docker Desktop for Windows
2. Edit `Backend/.env` with your API keys
3. Run: `cd Backend && docker-compose up --build`
4. Access: http://localhost:8000

**Option B: Local Development**
1. Use Python 3.11 (not 3.13) - download from python.org
2. Create venv: `py -3.11 -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`
5. Edit `Backend/.env` with your API keys
6. Start services: Docker containers for PostgreSQL and Redis
7. Run: `uvicorn src.main:app --reload --port 8000`

---

## What You Need to Get Started

### Required API Keys:

1. **OpenAI API Key**
   - Sign up: https://platform.openai.com/
   - Get API key from: https://platform.openai.com/api-keys
   - Add to `Backend/.env`

2. **Pinecone API Key**
   - Sign up: https://www.pinecone.io/
   - Create a new index:
     - Name: `live-data-rag`
     - Dimensions: `384`
     - Metric: `cosine`
   - Get API key and environment from dashboard
   - Add to `Backend/.env`

### Optional (can skip for now):
- News API key
- Alpha Vantage key
- Slack webhook

---

## Next Steps After Setup

1. Verify backend is running: http://localhost:8000/docs
2. Set up frontend (separate terminal):
   ```cmd
   cd Frontend
   npm install
   npm run dev
   ```
3. Access frontend: http://localhost:5173

---

## Quick Commands Reference

```cmd
# Activate virtual environment
cd Backend
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn src.main:app --reload --port 8000

# Run with Docker
cd Backend
docker-compose up --build

# Stop Docker
docker-compose down

# View logs
docker-compose logs -f backend
```

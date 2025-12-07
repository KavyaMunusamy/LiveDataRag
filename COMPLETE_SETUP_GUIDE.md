# Complete Setup Guide - LiveDataRAG

## 🚀 Quick Start (Step by Step)

### Prerequisites
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Docker Desktop installed and running

---

## 📋 Step-by-Step Instructions

### **Step 1: Configure API Keys**

Edit `Backend/.env` and add your API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=live-data-rag

# Database (already configured for Docker)
DATABASE_URL=postgresql://postgres:password@localhost:5432/live_rag
REDIS_URL=redis://localhost:6379
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Pinecone: https://www.pinecone.io/ (create index with 384 dimensions)

---

### **Step 2: Start Backend Services**

Open **Terminal 1** (for backend):

```cmd
cd Backend
docker-compose -f docker-compose.simple.yml up -d
```

This starts PostgreSQL and Redis in Docker.

**Verify services are running:**
```cmd
docker ps
```

You should see:
- `backend-db-1` (PostgreSQL)
- `backend-redis-1` (Redis)

---

### **Step 3: Start Backend Server**

In the same terminal (Terminal 1):

```cmd
cd Backend
venv\Scripts\activate
python -m uvicorn src.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**Verify backend is running:**
Open browser: http://localhost:8000/docs

---

### **Step 4: Start Frontend**

Open **Terminal 2** (for frontend):

```cmd
cd Frontend
npm run dev
```

**Expected output:**
```
VITE v5.4.21  ready in 731 ms
➜  Local:   http://localhost:3000/
```

**Verify frontend is running:**
Open browser: http://localhost:3000

---

## ✅ Verification Checklist

After starting everything, verify:

1. **Backend API**: http://localhost:8000/docs ✓
2. **Frontend**: http://localhost:3000 ✓
3. **PostgreSQL**: Running on port 5432 ✓
4. **Redis**: Running on port 6379 ✓

---

## 🛑 Stopping Everything

### Stop Frontend:
Press `Ctrl+C` in Terminal 2

### Stop Backend:
Press `Ctrl+C` in Terminal 1

### Stop Docker Services:
```cmd
cd Backend
docker-compose -f docker-compose.simple.yml down
```

---

## 🔄 Restart Instructions

### Restart Backend:
```cmd
cd Backend
venv\Scripts\activate
python -m uvicorn src.main:app --reload --port 8000
```

### Restart Frontend:
```cmd
cd Frontend
npm run dev
```

### Restart Docker Services:
```cmd
cd Backend
docker-compose -f docker-compose.simple.yml up -d
```

---

## 📝 Helper Scripts

### Backend:
- `Backend/start_services.bat` - Start PostgreSQL + Redis
- `Backend/run_backend.bat` - Start backend server
- `Backend/quick_fix.bat` - Fix missing dependencies

### Frontend:
- `Frontend/START.bat` - Start frontend dev server
- `Frontend/CHECK_STATUS.bat` - Check frontend status
- `Frontend/install_missing_deps.bat` - Install missing packages

---

## 🐛 Troubleshooting

### Backend Issues:

**Error: "No module named 'pydantic_settings'"**
```cmd
cd Backend
venv\Scripts\pip.exe install pydantic-settings==2.1.0
```

**Error: "Connection refused" (PostgreSQL/Redis)**
```cmd
# Make sure Docker Desktop is running
docker ps

# If no containers, start them:
cd Backend
docker-compose -f docker-compose.simple.yml up -d
```

**Error: "OPENAI_API_KEY not found"**
- Edit `Backend/.env` and add your API keys

---

### Frontend Issues:

**Error: "Cannot GET /"**
- Make sure dev server is running: `npm run dev`
- Check terminal for error messages

**Error: "Module not found"**
```cmd
cd Frontend
npm install --legacy-peer-deps
```

**Port 3000 already in use:**
```cmd
# Kill the process using port 3000
netstat -ano | findstr :3000
# Then kill the PID shown
taskkill /PID <PID> /F
```

---

## 🎯 What Each Component Does

### Backend (Port 8000):
- FastAPI REST API
- Real-time data processing
- Action execution engine
- RAG (Retrieval-Augmented Generation)
- WebSocket for live updates

### Frontend (Port 3000):
- React dashboard
- Query interface
- System monitoring
- Action management
- Real-time updates

### PostgreSQL (Port 5432):
- Stores action history
- User data
- System logs

### Redis (Port 6379):
- Caching
- Real-time data streams
- Pub/sub messaging

---

## 📊 System Architecture

```
┌─────────────────┐
│   Frontend      │  Port 3000
│   (React)       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Backend       │  Port 8000
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌────────┐
│ PostgreSQL│ │ Redis  │
│ Port 5432│ │Port 6379│
└────────┘ └────────┘
```

---

## 🔑 Important URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

---

## 💡 Tips

1. **Always start Docker services first** before backend
2. **Keep terminals open** while services are running
3. **Check terminal output** for error messages
4. **Use Ctrl+C** to stop services gracefully
5. **Backend must be running** for full frontend functionality

---

## 🆘 Still Having Issues?

1. Check `Backend/.env` has valid API keys
2. Verify Docker Desktop is running
3. Check all ports are available (3000, 8000, 5432, 6379)
4. Look at terminal output for specific errors
5. Try the "nuclear option" - restart everything:
   ```cmd
   # Stop all
   Ctrl+C in both terminals
   docker-compose -f Backend/docker-compose.simple.yml down
   
   # Start fresh
   Follow steps 2-4 again
   ```

---

## ✨ Success!

When everything is working:
- ✅ Frontend shows dashboard at http://localhost:3000
- ✅ Backend API docs at http://localhost:8000/docs
- ✅ No errors in terminals
- ✅ Docker containers running

You're ready to use Live Data RAG! 🎉

# How to Upload to GitHub

## Step 1: Initialize Git Repository

Open terminal in the project root directory:

```bash
cd C:\Users\Kavya\OneDrive\Desktop\LiveDataRAG
git init
```

## Step 2: Add Remote Repository

```bash
git remote add origin https://github.com/KavyaMunusamy/LiveDataRag.git
```

## Step 3: Stage All Files

```bash
git add .
```

This will add all files EXCEPT those in `.gitignore` (like `.env`, `node_modules`, `venv`, etc.)

## Step 4: Commit Files

```bash
git commit -m "Initial commit: LiveDataRAG - Real-time data processing with autonomous actions"
```

## Step 5: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

If you get an authentication error, you'll need to:
1. Generate a Personal Access Token on GitHub
2. Use it as your password when pushing

---

## Alternative: Using GitHub Desktop

1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Open GitHub Desktop
3. Click "Add" → "Add Existing Repository"
4. Browse to: `C:\Users\Kavya\OneDrive\Desktop\LiveDataRAG`
5. Click "Publish repository"
6. Uncheck "Keep this code private" if you want it public
7. Click "Publish Repository"

---

## ⚠️ IMPORTANT: Before Uploading

### 1. Verify .gitignore is Working

Check that sensitive files won't be uploaded:

```bash
git status
```

You should NOT see:
- `.env` files
- `node_modules/` folder
- `venv/` folder
- `__pycache__/` folders

If you see these, they will be uploaded! Stop and fix `.gitignore`.

### 2. Remove Sensitive Data from .env

The `.env` file is already in `.gitignore`, but double-check:

```bash
# This should return nothing (file is ignored)
git status | findstr ".env"
```

### 3. Create .env.example

Create a template without real API keys:

```bash
# Backend/.env.example
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=live-data-rag

DATABASE_URL=postgresql://postgres:password@localhost:5432/live_rag
REDIS_URL=redis://localhost:6379

NEWS_API_KEY=your_newsapi_key_optional
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_optional
```

---

## Complete Command Sequence

```bash
# Navigate to project
cd C:\Users\Kavya\OneDrive\Desktop\LiveDataRAG

# Initialize git
git init

# Add remote
git remote add origin https://github.com/KavyaMunusamy/LiveDataRag.git

# Check what will be committed (verify no sensitive files)
git status

# Add all files
git add .

# Commit
git commit -m "Initial commit: LiveDataRAG system"

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## If Repository Already Exists on GitHub

If you already created the repo on GitHub and it has files:

```bash
# Pull first
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

---

## Verify Upload

1. Go to: https://github.com/KavyaMunusamy/LiveDataRag
2. Check that files are there
3. Verify `.env` is NOT visible (should be ignored)
4. Check README.md displays correctly

---

## Update Repository Later

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

---

## Common Issues

### Issue: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/KavyaMunusamy/LiveDataRag.git
```

### Issue: Authentication failed
- Use Personal Access Token instead of password
- Generate at: GitHub → Settings → Developer settings → Personal access tokens

### Issue: Large files rejected
- Check `.gitignore` is working
- Remove large files: `git rm --cached <file>`

---

## Files That WILL Be Uploaded

✅ Source code (`.py`, `.jsx`, `.js`)
✅ Configuration files (`vite.config.js`, `package.json`)
✅ Documentation (`.md` files)
✅ Docker configs (`docker-compose.yml`)
✅ `.env.example` (template without real keys)

## Files That WON'T Be Uploaded (Ignored)

❌ `.env` (contains API keys)
❌ `node_modules/` (too large, can be reinstalled)
❌ `venv/` (Python virtual environment)
❌ `__pycache__/` (Python cache)
❌ `.vite/` (Vite cache)
❌ Build outputs

---

## After Upload

Add these badges to your README:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)
![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

---

Good luck with your upload! 🚀

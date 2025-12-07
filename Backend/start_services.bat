@echo off
echo Starting Required Services...
echo.

echo Checking Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Starting PostgreSQL...
docker run -d --name postgres-liverag -p 5432:5432 -e POSTGRES_DB=live_rag -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine

echo Starting Redis...
docker run -d --name redis-liverag -p 6379:6379 redis:7-alpine

echo.
echo Services started!
echo PostgreSQL: localhost:5432
echo Redis: localhost:6379
echo.
echo Now you can start the backend:
echo   venv\Scripts\activate
echo   uvicorn src.main:app --reload --port 8000
echo.
pause

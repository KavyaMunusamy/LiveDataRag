@echo off
echo Starting LiveDataRAG Services...
echo.

echo Checking Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Starting PostgreSQL and Redis...
docker-compose -f docker-compose.simple.yml up -d

echo.
echo Services started!
echo PostgreSQL: localhost:5432
echo Redis: localhost:6379
echo.
echo Now starting Backend...
call venv\Scripts\activate.bat
uvicorn src.main:app --reload --port 8000

pause

@echo off
echo Starting LiveDataRAG Backend...
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please edit Backend\.env and add your API keys.
    pause
    exit /b 1
)

REM Activate virtual environment and start server
call venv\Scripts\activate.bat
uvicorn src.main:app --reload --port 8000

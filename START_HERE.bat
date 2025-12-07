@echo off
echo ========================================
echo   LiveDataRAG - Quick Start
echo ========================================
echo.

echo What would you like to do?
echo.
echo 1. Start everything with Docker (Easiest)
echo 2. Start services only (PostgreSQL + Redis)
echo 3. Start backend only (services must be running)
echo 4. Check if Docker is running
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    cd Backend
    call start_all.bat
) else if "%choice%"=="2" (
    cd Backend
    call start_services.bat
) else if "%choice%"=="3" (
    cd Backend
    call venv\Scripts\activate.bat
    uvicorn src.main:app --reload --port 8000
) else if "%choice%"=="4" (
    docker ps
    echo.
    echo If you see containers listed above, Docker is running.
    echo If you see an error, please start Docker Desktop.
    pause
) else (
    exit
)

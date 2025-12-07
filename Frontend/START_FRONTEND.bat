@echo off
echo ========================================
echo   Starting LiveDataRAG Frontend
echo ========================================
echo.

echo Step 1: Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js is installed
echo.

echo Step 2: Checking dependencies...
if not exist node_modules (
    echo Installing dependencies...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✓ Dependencies are installed
echo.

echo Step 3: Starting development server...
echo.
echo Frontend will be available at:
echo   ➜ Local:   http://localhost:3000/
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause

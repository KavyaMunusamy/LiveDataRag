@echo off
cd /d "%~dp0"
echo ========================================
echo   Frontend Setup and Run
echo ========================================
echo.

echo Current directory: %CD%
echo.

echo Checking if Node.js is installed...
where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

echo NPM version:
npm --version
echo.

if not exist node_modules (
    echo Installing dependencies (this may take a few minutes)...
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo.
npm run dev

pause

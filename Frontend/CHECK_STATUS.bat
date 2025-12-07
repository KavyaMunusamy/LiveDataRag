@echo off
echo ========================================
echo   Frontend Status Check
echo ========================================
echo.

echo [1/6] Checking Node.js...
node --version
if errorlevel 1 (
    echo ❌ Node.js NOT installed
) else (
    echo ✅ Node.js installed
)
echo.

echo [2/6] Checking npm...
npm --version
if errorlevel 1 (
    echo ❌ npm NOT installed
) else (
    echo ✅ npm installed
)
echo.

echo [3/6] Checking dependencies...
if exist node_modules (
    echo ✅ node_modules folder exists
) else (
    echo ❌ node_modules NOT found - Run: npm install --legacy-peer-deps
)
echo.

echo [4/6] Checking key files...
if exist src\index.js (
    echo ✅ src\index.js exists
) else (
    echo ❌ src\index.js NOT found
)

if exist src\App.jsx (
    echo ✅ src\App.jsx exists
) else (
    echo ❌ src\App.jsx NOT found
)

if exist public\index.html (
    echo ✅ public\index.html exists
) else (
    echo ❌ public\index.html NOT found
)

if exist vite.config.js (
    echo ✅ vite.config.js exists
) else (
    echo ❌ vite.config.js NOT found
)
echo.

echo [5/6] Checking if port 3000 is in use...
netstat -ano | findstr :3000 >nul
if errorlevel 1 (
    echo ✅ Port 3000 is available
) else (
    echo ⚠️  Port 3000 is already in use
    echo    Kill the process or the dev server is already running
)
echo.

echo [6/6] Testing if dev server is accessible...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Dev server is NOT running
    echo    Start it with: npm run dev
) else (
    echo ✅ Dev server is running!
    echo    Access at: http://localhost:3000
)
echo.

echo ========================================
echo   Status Check Complete
echo ========================================
echo.
echo To start the frontend:
echo   npm run dev
echo.
echo To install dependencies:
echo   npm install --legacy-peer-deps
echo.

pause

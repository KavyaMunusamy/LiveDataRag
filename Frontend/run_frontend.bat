@echo off
echo Starting Frontend Development Server...
echo.

if not exist node_modules (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting Vite dev server...
call npm run dev

pause

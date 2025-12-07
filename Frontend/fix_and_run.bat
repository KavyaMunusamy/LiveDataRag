@echo off
echo Fixing Frontend Issues...
echo.

echo Installing missing dependencies...
call npm install @mui/icons-material notistack

echo.
echo Starting development server...
call npm run dev

pause

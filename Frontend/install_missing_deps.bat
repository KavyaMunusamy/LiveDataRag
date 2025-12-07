@echo off
echo Installing missing frontend dependencies...
echo.

echo Installing MUI Icons (compatible with MUI v5)...
call npm install @mui/icons-material@5.14.18 --legacy-peer-deps

echo Installing Notistack (notifications)...
call npm install notistack@3.0.1 --legacy-peer-deps

echo Installing Framer Motion (animations)...
call npm install framer-motion@10.16.0 --legacy-peer-deps

echo Installing React Syntax Highlighter (code display)...
call npm install react-syntax-highlighter@15.5.0 --legacy-peer-deps

echo Installing React Circular Progressbar (charts)...
call npm install react-circular-progressbar@2.1.0 --legacy-peer-deps

echo.
echo All dependencies installed!
echo You can now run: npm run dev
echo.
pause

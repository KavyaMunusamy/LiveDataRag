@echo off
echo Fixing missing dependencies...
echo.

venv\Scripts\pip.exe install pydantic-settings==2.1.0
venv\Scripts\pip.exe install --only-binary :all: numpy pandas

echo.
echo Done! Now you can run:
echo venv\Scripts\activate
echo uvicorn src.main:app --reload --port 8000
echo.
pause

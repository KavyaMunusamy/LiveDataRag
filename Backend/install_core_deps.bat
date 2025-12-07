@echo off
echo Installing core backend dependencies...
echo.

echo Installing FastAPI and Uvicorn...
pip install fastapi uvicorn[standard]

echo Installing database packages...
pip install sqlalchemy redis

echo Installing OpenAI and Pinecone...
pip install openai pinecone-client

echo Installing utilities...
pip install python-dotenv pydantic pydantic-settings

echo Installing web packages...
pip install aiohttp beautifulsoup4 requests

echo Installing numpy and pandas (pre-built)...
pip install --only-binary :all: numpy pandas

echo.
echo Core dependencies installed!
echo You can now start the backend with:
echo   python -m uvicorn src.main:app --reload --port 8000
echo.
pause

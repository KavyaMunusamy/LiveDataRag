@echo off
echo Installing LiveDataRAG Backend Dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install packages one by one to handle errors better
echo Installing core dependencies...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install python-dotenv==1.0.0

echo Installing database dependencies...
pip install pinecone-client==2.2.4
pip install sqlalchemy==2.0.23
pip install asyncpg==0.29.0
pip install redis==5.0.1

echo Installing AI/LLM dependencies...
pip install openai==1.3.0
pip install anthropic==0.7.7
pip install sentence-transformers==2.2.2
pip install langchain==0.0.340
pip install langchain-openai==0.0.1

echo Installing data processing (this may take a while)...
pip install pandas
pip install numpy
pip install aiohttp==3.9.1
pip install beautifulsoup4==4.12.2

echo Installing monitoring dependencies...
pip install prometheus-client==0.19.0
pip install structlog==23.2.0
pip install sentry-sdk==1.38.0

echo Installing utilities...
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install celery==5.3.4
pip install websockets==12.0
pip install python-socketio==5.10.0

echo.
echo Installation complete!
echo.
pause

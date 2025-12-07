<<<<<<< HEAD
# LiveDataRAG - Real-Time Data Processing with Autonomous Actions

A production-ready system that combines **Real-time Data Processing**, **RAG (Retrieval-Augmented Generation)**, and **Autonomous Action Execution** to create an intelligent data analysis and automation platform.

## 🌟 Features

- **Real-Time Data Streams**: Financial data, news feeds, social media, IoT sensors
- **AI-Powered Analysis**: Uses OpenAI/Anthropic for intelligent query processing
- **Autonomous Actions**: Automated alerts, API calls, database updates, workflow triggers
- **Vector Search**: Time-aware retrieval with Pinecone
- **Safety Layer**: Multi-level safety checks, rate limiting, duplicate detection
- **WebSocket Support**: Real-time updates to frontend
- **Modern UI**: React dashboard with Material-UI
- **Monitoring**: Prometheus metrics, structured logging

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  React + Vite + Material-UI
│   Port 3000     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Backend       │  FastAPI + Python
│   Port 8000     │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌────────┐
│PostgreSQL│ │ Redis  │
│Port 5432│ │Port 6379│
└────────┘ └────────┘
```

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker Desktop** (for PostgreSQL and Redis)
- **API Keys**:
  - OpenAI API key ([Get here](https://platform.openai.com/api-keys))
  - Pinecone API key ([Get here](https://www.pinecone.io/))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/KavyaMunusamy/LiveDataRag.git
cd LiveDataRag
```

### 2. Configure API Keys

Create `Backend/.env` file:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=live-data-rag

# Database (configured for Docker)
DATABASE_URL=postgresql://postgres:password@localhost:5432/live_rag
REDIS_URL=redis://localhost:6379

# Optional
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

### 3. Start Backend

**Terminal 1:**

```bash
# Start Docker services (PostgreSQL + Redis)
cd Backend
docker-compose -f docker-compose.simple.yml up -d

# Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Start backend server
python -m uvicorn src.main:app --reload --port 8000
```

**Verify**: http://localhost:8000/docs

### 4. Start Frontend

**Terminal 2:**

```bash
cd Frontend
npm install --legacy-peer-deps
npm run dev
```

**Verify**: http://localhost:3000

## 📁 Project Structure

```
LiveDataRAG/
├── Backend/
│   ├── src/
│   │   ├── action_engine/      # Action execution system
│   │   ├── data_pipeline/      # Data connectors & processing
│   │   ├── rag_engine/         # RAG implementation
│   │   ├── monitoring/         # Metrics & logging
│   │   ├── config/             # Configuration
│   │   └── main.py             # FastAPI application
│   ├── requirements.txt
│   └── docker-compose.simple.yml
├── Frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API & WebSocket services
│   │   ├── contexts/           # React contexts
│   │   └── App.jsx             # Main app component
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🔧 Configuration

### Pinecone Setup

1. Create account at [Pinecone](https://www.pinecone.io/)
2. Create index:
   - Name: `live-data-rag`
   - Dimensions: `384`
   - Metric: `cosine`
3. Copy API key and environment to `.env`

### Optional Services

- **News API**: Get key from [NewsAPI](https://newsapi.org/)
- **Financial Data**: Get key from [Alpha Vantage](https://www.alphavantage.co/)
- **Slack Notifications**: Configure webhook URL
- **Email Alerts**: Configure SMTP settings

## 🎯 Usage

### Query Interface

1. Open http://localhost:3000
2. Enter natural language queries like:
   - "Monitor TSLA stock and alert me if it drops 5%"
   - "What are the latest AI developments?"
   - "Analyze sentiment about our product"

### Create Automation Rules

1. Go to Rules Manager
2. Define conditions (keywords, thresholds, patterns)
3. Set actions (alerts, API calls, workflows)
4. Enable the rule

### Monitor System

- **Dashboard**: Real-time metrics and system health
- **Action Log**: History of executed actions
- **Data Streams**: Live data flow visualization

## 🛠️ Development

### Backend Development

```bash
cd Backend
venv\Scripts\activate
python -m uvicorn src.main:app --reload --port 8000
```

### Frontend Development

```bash
cd Frontend
npm run dev
```

### Run Tests

```bash
# Backend
cd Backend
pytest

# Frontend
cd Frontend
npm test
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Deployment

```bash
cd Backend
docker-compose up --build
```

This starts all services (backend, frontend, PostgreSQL, Redis, Prometheus, Grafana).

## 🔒 Security

- API keys stored in `.env` (never committed)
- Multi-layer safety checks for actions
- Rate limiting on API endpoints
- Input validation with Pydantic
- CORS configuration for frontend

## 📝 Environment Variables

See `Backend/.env.example` for all available configuration options.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI for the backend framework
- React and Material-UI for the frontend
- OpenAI for LLM capabilities
- Pinecone for vector search
- All open-source contributors

## 📧 Contact

Kavya Munusamy - [@KavyaMunusamy](https://github.com/KavyaMunusamy)

Project Link: [https://github.com/KavyaMunusamy/LiveDataRag](https://github.com/KavyaMunusamy/LiveDataRag)

---

## 🚨 Important Notes

- **Never commit `.env` files** - they contain sensitive API keys
- **Backend must be running** for full frontend functionality
- **Docker Desktop required** for PostgreSQL and Redis
- **API keys required** for OpenAI and Pinecone

## 🐛 Troubleshooting

See `COMPLETE_SETUP_GUIDE.md` for detailed troubleshooting steps.

### Common Issues

**Backend won't start:**
- Check if PostgreSQL and Redis are running: `docker ps`
- Verify API keys in `.env`
- Install missing dependencies: `pip install -r requirements.txt`

**Frontend shows 404:**
- Ensure dev server is running: `npm run dev`
- Check terminal for build errors
- Clear cache: `rm -rf node_modules/.vite && npm run dev`

**Database connection errors:**
- Start Docker services: `docker-compose -f docker-compose.simple.yml up -d`
- Check Docker Desktop is running

---

Made with ❤️ by Kavya Munusamy
=======
# LiveDataRag
>>>>>>> 3122e617802a47247d109f5e8307f2b1ed151f0b

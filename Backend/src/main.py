from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, List
import json

from .config.settings import settings
from .data_pipeline.connectors.financial import FinancialDataConnector
from .data_pipeline.storage import TimeAwareVectorStore
from .rag_engine.retriever import TimeAwareRetriever
from .action_engine.decision_maker import ActionDecisionEngine
from .action_engine.registry import ActionRegistry
from .monitoring.logger import get_logger

logger = get_logger(__name__)

# Global instances
vector_store = None
retriever = None
decision_engine = None
action_registry = None
financial_connector = None

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup/shutdown"""
    # Startup
    logger.info("Initializing Live Data RAG System...")
    
    global vector_store, retriever, decision_engine, action_registry, financial_connector
    
    # Initialize components
    vector_store = TimeAwareVectorStore()
    vector_store.initialize()
    
    retriever = TimeAwareRetriever(vector_store)
    decision_engine = ActionDecisionEngine()
    action_registry = ActionRegistry()
    financial_connector = FinancialDataConnector()
    
    # Start data ingestion task
    asyncio.create_task(data_ingestion_task())
    
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Live Data RAG System...")
    
    if financial_connector:
        await financial_connector.close()
    
    logger.info("Shutdown complete")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "subscribe_stream":
                # Handle stream subscription
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscription_confirmation",
                        "stream_id": message["streamId"],
                        "status": "subscribed"
                    }),
                    websocket
                )
                
            elif message["type"] == "query":
                # Process real-time query
                response = await process_query(message["query"])
                await manager.send_personal_message(
                    json.dumps({
                        "type": "query_response",
                        "query_id": message.get("queryId"),
                        "response": response
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Live Data RAG with Actions API", "status": "operational"}

@app.get("/api/v1/system/status")
async def system_status():
    """Get system status"""
    return {
        "status": "active",
        "components": {
            "vector_store": "connected",
            "retriever": "ready",
            "decision_engine": "active",
            "action_registry": "ready"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/query")
async def process_query_endpoint(query: Dict):
    """Process a query and potentially trigger actions"""
    try:
        result = await process_query(query["query"], query.get("context", {}))
        return result
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/actions/history")
async def get_action_history(limit: int = 20):
    """Get action history"""
    if action_registry:
        return action_registry.action_history[-limit:]
    return []

@app.post("/api/v1/actions/confirm/{action_id}")
async def confirm_action(action_id: str, confirm: bool):
    """Confirm or reject a pending action"""
    # Implementation for action confirmation
    return {"status": "confirmed" if confirm else "rejected", "action_id": action_id}

@app.get("/api/v1/data/streams")
async def get_data_streams():
    """Get active data streams"""
    # Return mock data for now
    return [
        {"id": "financial", "name": "Financial Data", "status": "active", "data_points": 1500},
        {"id": "news", "name": "News Feeds", "status": "active", "data_points": 3200},
        {"id": "social", "name": "Social Media", "status": "inactive", "data_points": 0},
    ]

# Background tasks
async def data_ingestion_task():
    """Continuous data ingestion task"""
    while True:
        try:
            # Fetch financial data
            if financial_connector:
                quotes = await financial_connector.fetch_realtime_quotes()
                
                for quote in quotes:
                    if quote:
                        # Store in vector DB
                        await vector_store.store_data(quote)
                        
                        # Broadcast to WebSocket clients
                        await manager.broadcast(
                            json.dumps({
                                "type": "data_update",
                                "data_type": "financial_quote",
                                "data": quote
                            })
                        )
            
            # Sleep before next ingestion
            await asyncio.sleep(60)  # Every minute
            
        except Exception as e:
            logger.error(f"Data ingestion error: {e}")
            await asyncio.sleep(10)

async def process_query(query: str, context: Dict = None) -> Dict:
    """Process a query through the full pipeline"""
    # 1. Retrieve relevant data
    retrieval_result = await retriever.retrieve(
        query=query,
        time_range="last_6_hours",
        include_raw=False
    )
    
    # 2. Decide if action is needed
    user_rules = []  # Would come from user profile/database
    decision = await decision_engine.evaluate_for_action(
        query=query,
        context=retrieval_result["context"],
        user_rules=user_rules,
        historical_actions=action_registry.action_history[-10:] if action_registry else []
    )
    
    # 3. Execute action if needed
    action_result = None
    if decision["action_required"] and action_registry:
        action_result = await action_registry.execute_action(
            action_type=decision["action_type"],
            parameters=decision.get("action_parameters", {}),
            context={
                "query": query,
                "retrieval_result": retrieval_result,
                "decision": decision
            },
            require_confirmation=decision.get("requires_confirmation", False)
        )
        
        # Broadcast action execution
        if action_result:
            await manager.broadcast(
                json.dumps({
                    "type": "action_executed",
                    "action": action_result
                })
            )
    
    # 4. Generate response
    response_text = generate_response(
        query=query,
        context=retrieval_result["context"],
        decision=decision,
        action_result=action_result
    )
    
    return {
        "query": query,
        "response": response_text,
        "retrieval_metadata": retrieval_result["metadata"],
        "decision": decision,
        "action_result": action_result,
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_response(query: str, context: str, decision: Dict, action_result: Dict = None) -> str:
    """Generate human-readable response"""
    
    if action_result and action_result.get("status") == "executed":
        return f"Based on the current data: {context}\n\nI've executed the following action: {decision['action_type']}. {action_result.get('result', 'Action completed successfully.')}"
    
    elif decision["action_required"] and decision.get("requires_confirmation"):
        return f"Analysis suggests taking action: {decision['action_type']}. Reason: {decision.get('reason', 'Conditions met')}. Please confirm if you want to proceed."
    
    else:
        return f"Based on the latest information: {context}\n\nNo immediate action required. The situation is being monitored and I'll alert you if conditions change."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
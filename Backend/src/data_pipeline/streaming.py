import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from datetime import datetime, timedelta
import redis.asyncio as redis
from ...config.settings import settings
from ...monitoring.logger import get_logger
from .connectors.financial import FinancialDataConnector
from .connectors.news import NewsDataConnector
from .connectors.custom import CustomDataConnector
from .processor import DataProcessor
from .storage import TimeAwareVectorStore

logger = get_logger(__name__)

class DataStreamManager:
    """Manager for real-time data streams"""
    
    def __init__(self):
        self.redis_client = None
        self.streams = {}
        self.subscribers = {}
        self.processor = None
        self.vector_store = None
        self.is_running = False
        
        # Initialize connectors
        self.financial_connector = FinancialDataConnector()
        self.news_connector = NewsDataConnector()
        self.custom_connector = CustomDataConnector()
        
        # Statistics
        self.stats = {
            "total_messages": 0,
            "active_streams": 0,
            "subscribers": 0,
            "errors": 0,
            "last_update": datetime.utcnow().isoformat()
        }
    
    async def initialize(self, processor: DataProcessor, vector_store: TimeAwareVectorStore):
        """Initialize stream manager"""
        self.processor = processor
        self.vector_store = vector_store
        
        # Initialize Redis
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Initialize connectors
        await self.financial_connector.connect()
        await self.news_connector.initialize()
        await self.custom_connector.initialize()
        
        logger.info("Data stream manager initialized")
    
    async def start_stream(self, stream_type: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Start a new data stream"""
        stream_id = f"{stream_type}_{datetime.utcnow().timestamp()}"
        
        if stream_type == "financial":
            stream_task = asyncio.create_task(self._run_financial_stream(stream_id, config))
        elif stream_type == "news":
            stream_task = asyncio.create_task(self._run_news_stream(stream_id, config))
        elif stream_type == "custom":
            stream_id = config.get("source_id", stream_id)
            stream_task = asyncio.create_task(self._run_custom_stream(stream_id, config))
        else:
            raise ValueError(f"Unknown stream type: {stream_type}")
        
        self.streams[stream_id] = {
            "type": stream_type,
            "task": stream_task,
            "config": config or {},
            "started_at": datetime.utcnow().isoformat(),
            "status": "running",
            "message_count": 0,
            "error_count": 0
        }
        
        self.stats["active_streams"] = len(self.streams)
        logger.info(f"Started {stream_type} stream: {stream_id}")
        
        return stream_id
    
    async def _run_financial_stream(self, stream_id: str, config: Dict[str, Any]):
        """Run financial data stream"""
        symbols = config.get("symbols", ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"])
        interval = config.get("interval", 60)  # seconds
        
        while self.is_running and stream_id in self.streams:
            try:
                # Fetch financial data
                quotes = await self.financial_connector.fetch_realtime_quotes()
                
                for quote in quotes:
                    if quote:
                        # Process and store
                        processed = await self.processor.process(quote)
                        await self._handle_stream_data(stream_id, processed)
                
                # Update stream stats
                self.streams[stream_id]["message_count"] += len(quotes)
                
            except Exception as e:
                self.streams[stream_id]["error_count"] += 1
                self.stats["errors"] += 1
                logger.error(f"Error in financial stream {stream_id}: {e}")
            
            # Wait for next interval
            await asyncio.sleep(interval)
    
    async def _run_news_stream(self, stream_id: str, config: Dict[str, Any]):
        """Run news data stream"""
        interval = config.get("interval", 300)  # 5 minutes
        keywords = config.get("keywords", [])
        
        while self.is_running and stream_id in self.streams:
            try:
                # Fetch news
                if keywords:
                    articles = await self.news_connector.search_news(keywords, limit=20)
                else:
                    articles = await self.news_connector.fetch_news(limit=20)
                
                for article in articles:
                    # Process and store
                    processed = await self.processor.process(article)
                    await self._handle_stream_data(stream_id, processed)
                
                # Update stream stats
                self.streams[stream_id]["message_count"] += len(articles)
                
            except Exception as e:
                self.streams[stream_id]["error_count"] += 1
                self.stats["errors"] += 1
                logger.error(f"Error in news stream {stream_id}: {e}")
            
            # Wait for next interval
            await asyncio.sleep(interval)
    
    async def _run_custom_stream(self, stream_id: str, config: Dict[str, Any]):
        """Run custom data stream"""
        source_id = config.get("source_id")
        if not source_id:
            raise ValueError("source_id required for custom stream")
        
        try:
            async for data in self.custom_connector.stream_data(source_id):
                if not self.is_running or stream_id not in self.streams:
                    break
                
                try:
                    # Process and store
                    processed = await self.processor.process(data)
                    await self._handle_stream_data(stream_id, processed)
                    
                    # Update stream stats
                    self.streams[stream_id]["message_count"] += 1
                    
                except Exception as e:
                    self.streams[stream_id]["error_count"] += 1
                    self.stats["errors"] += 1
                    logger.error(f"Error processing custom stream data {stream_id}: {e}")
                    
        except Exception as e:
            self.streams[stream_id]["error_count"] += 1
            self.stats["errors"] += 1
            logger.error(f"Error in custom stream {stream_id}: {e}")
    
    async def _handle_stream_data(self, stream_id: str, data: Dict[str, Any]):
        """Handle stream data: store, publish, and notify"""
        try:
            # Store in vector database
            if self.vector_store and "error" not in data:
                await self.vector_store.store_data(data)
            
            # Publish to Redis for real-time subscribers
            await self._publish_to_redis(stream_id, data)
            
            # Update statistics
            self.stats["total_messages"] += 1
            self.stats["last_update"] = datetime.utcnow().isoformat()
            
            # Log periodically
            if self.stats["total_messages"] % 100 == 0:
                logger.info(f"Processed {self.stats['total_messages']} total messages")
            
        except Exception as e:
            logger.error(f"Error handling stream data: {e}")
    
    async def _publish_to_redis(self, stream_id: str, data: Dict[str, Any]):
        """Publish data to Redis channels"""
        if not self.redis_client:
            return
        
        try:
            # Create message
            message = {
                "stream_id": stream_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "data_update"
            }
            
            # Publish to stream-specific channel
            await self.redis_client.publish(
                f"stream:{stream_id}",
                json.dumps(message)
            )
            
            # Publish to general data channel
            await self.redis_client.publish(
                "data:updates",
                json.dumps(message)
            )
            
            # Store in Redis stream for persistence
            await self.redis_client.xadd(
                f"stream:data:{stream_id}",
                {"data": json.dumps(message)},
                maxlen=1000  # Keep last 1000 messages
            )
            
        except Exception as e:
            logger.error(f"Redis publish error: {e}")
    
    async def subscribe(self, stream_id: str, callback: Callable):
        """Subscribe to a data stream"""
        if stream_id not in self.subscribers:
            self.subscribers[stream_id] = []
        
        self.subscribers[stream_id].append(callback)
        self.stats["subscribers"] = sum(len(callbacks) for callbacks in self.subscribers.values())
        
        logger.info(f"New subscriber for stream {stream_id}")
        
        # Return unsubscribe function
        def unsubscribe():
            if stream_id in self.subscribers and callback in self.subscribers[stream_id]:
                self.subscribers[stream_id].remove(callback)
                self.stats["subscribers"] = sum(len(callbacks) for callbacks in self.subscribers.values())
                logger.info(f"Unsubscribed from stream {stream_id}")
        
        return unsubscribe
    
    async def get_stream_history(self, stream_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data from a stream"""
        if not self.redis_client:
            return []
        
        try:
            # Get from Redis stream
            messages = await self.redis_client.xrevrange(
                f"stream:data:{stream_id}",
                count=limit
            )
            
            history = []
            for msg_id, msg_data in messages:
                data = json.loads(msg_data["data"])
                history.append(data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting stream history: {e}")
            return []
    
    async def stop_stream(self, stream_id: str):
        """Stop a data stream"""
        if stream_id in self.streams:
            stream_info = self.streams[stream_id]
            stream_info["status"] = "stopping"
            
            # Cancel the stream task
            stream_info["task"].cancel()
            try:
                await stream_info["task"]
            except asyncio.CancelledError:
                pass
            
            # Update status
            stream_info["status"] = "stopped"
            stream_info["stopped_at"] = datetime.utcnow().isoformat()
            
            self.stats["active_streams"] = len([s for s in self.streams.values() if s["status"] == "running"])
            logger.info(f"Stopped stream: {stream_id}")
            
            return True
        
        return False
    
    async def start_all_streams(self, configs: Dict[str, Dict[str, Any]] = None):
        """Start all configured streams"""
        if not configs:
            configs = {
                "financial": {"symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"], "interval": 60},
                "news": {"interval": 300}
            }
        
        self.is_running = True
        
        for stream_type, config in configs.items():
            try:
                await self.start_stream(stream_type, config)
            except Exception as e:
                logger.error(f"Failed to start {stream_type} stream: {e}")
        
        logger.info(f"Started {len(self.streams)} data streams")
    
    async def stop_all_streams(self):
        """Stop all data streams"""
        self.is_running = False
        
        for stream_id in list(self.streams.keys()):
            await self.stop_stream(stream_id)
        
        logger.info("All data streams stopped")
    
    def list_streams(self) -> List[Dict[str, Any]]:
        """List all active streams"""
        return [
            {
                "stream_id": stream_id,
                "type": info["type"],
                "status": info["status"],
                "started_at": info["started_at"],
                "message_count": info["message_count"],
                "error_count": info["error_count"],
                "config": info["config"]
            }
            for stream_id, info in self.streams.items()
        ]
    
    def get_stream_stats(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific stream"""
        if stream_id not in self.streams:
            return None
        
        info = self.streams[stream_id]
        
        # Calculate uptime
        started = datetime.fromisoformat(info["started_at"])
        uptime_seconds = (datetime.utcnow() - started).total_seconds()
        
        # Calculate message rate
        if uptime_seconds > 0:
            message_rate = info["message_count"] / uptime_seconds
        else:
            message_rate = 0
        
        return {
            "stream_id": stream_id,
            "type": info["type"],
            "status": info["status"],
            "uptime_seconds": uptime_seconds,
            "message_count": info["message_count"],
            "error_count": info["error_count"],
            "message_rate_per_second": message_rate,
            "error_rate": info["error_count"] / max(info["message_count"], 1),
            "config": info["config"]
        }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        # Calculate additional stats
        total_messages = sum(info["message_count"] for info in self.streams.values())
        total_errors = sum(info["error_count"] for info in self.streams.values())
        
        return {
            **self.stats,
            "total_messages": total_messages,
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_messages, 1),
            "stream_count": len(self.streams),
            "running_streams": len([s for s in self.streams.values() if s["status"] == "running"]),
            "uptime_seconds": (
                datetime.utcnow() - datetime.fromisoformat(self.stats.get("started_at", datetime.utcnow().isoformat()))
            ).total_seconds()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        # Stop all streams
        await self.stop_all_streams()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Close connectors
        await self.financial_connector.close()
        await self.news_connector.close()
        await self.custom_connector.close()
        
        logger.info("Data stream manager cleaned up")
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import aiohttp
from aiohttp import web
from ...config.settings import settings
from ...monitoring.logger import get_logger

logger = get_logger(__name__)

class WebhookConnector:
    """Webhook connector for receiving real-time data"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.webhooks = {}
        self.data_handlers = []
        
        # Setup routes
        self.app.router.add_post('/webhook/{webhook_id}', self.handle_webhook)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_post('/register', self.handle_register)
    
    async def start(self):
        """Start webhook server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        logger.info(f"Webhook server started on {self.host}:{self.port}")
    
    async def stop(self):
        """Stop webhook server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.cleanup()
        
        logger.info("Webhook server stopped")
    
    async def handle_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming webhook data"""
        webhook_id = request.match_info.get('webhook_id')
        client_ip = request.remote
        
        try:
            # Parse request data
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = await request.text()
                try:
                    data = json.loads(data)
                except:
                    data = {"raw_text": data}
            
            # Add metadata
            enriched_data = {
                "webhook_id": webhook_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "headers": dict(request.headers),
                "data_type": "webhook_data"
            }
            
            # Validate webhook if it's registered
            if webhook_id in self.webhooks:
                webhook_config = self.webhooks[webhook_id]
                
                # Verify secret if configured
                secret = webhook_config.get("secret")
                if secret:
                    provided_secret = request.headers.get('X-Webhook-Secret')
                    if provided_secret != secret:
                        return web.Response(
                            status=401,
                            text="Invalid webhook secret"
                        )
            
            # Process data
            await self._process_webhook_data(enriched_data)
            
            logger.info(f"Webhook received from {client_ip} for {webhook_id}")
            
            return web.Response(
                status=200,
                text="Webhook received successfully"
            )
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return web.Response(
                status=500,
                text=f"Internal server error: {str(e)}"
            )
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.Response(
            status=200,
            text=json.dumps({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "active_webhooks": len(self.webhooks),
                "data_handlers": len(self.data_handlers)
            })
        )
    
    async def handle_register(self, request: web.Request) -> web.Response:
        """Register a new webhook"""
        try:
            data = await request.json()
            
            webhook_id = data.get('webhook_id')
            if not webhook_id:
                return web.Response(
                    status=400,
                    text="webhook_id is required"
                )
            
            # Store webhook configuration
            self.webhooks[webhook_id] = {
                "secret": data.get('secret'),
                "description": data.get('description'),
                "registered_at": datetime.utcnow().isoformat(),
                "callback_url": data.get('callback_url')
            }
            
            logger.info(f"Webhook registered: {webhook_id}")
            
            return web.Response(
                status=200,
                text=json.dumps({
                    "success": True,
                    "webhook_id": webhook_id,
                    "endpoint": f"http://{self.host}:{self.port}/webhook/{webhook_id}",
                    "registered_at": self.webhooks[webhook_id]["registered_at"]
                })
            )
            
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            return web.Response(
                status=500,
                text=f"Internal server error: {str(e)}"
            )
    
    async def _process_webhook_data(self, data: Dict[str, Any]):
        """Process incoming webhook data"""
        # Call registered data handlers
        for handler in self.data_handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.error(f"Error in data handler: {e}")
    
    def register_data_handler(self, handler: Callable):
        """Register a data handler for incoming webhook data"""
        self.data_handlers.append(handler)
        logger.info(f"Data handler registered: {handler.__name__}")
    
    def unregister_data_handler(self, handler: Callable):
        """Unregister a data handler"""
        if handler in self.data_handlers:
            self.data_handlers.remove(handler)
            logger.info(f"Data handler unregistered: {handler.__name__}")
    
    async def send_webhook(self, url: str, data: Dict[str, Any], 
                          headers: Optional[Dict[str, str]] = None,
                          secret: Optional[str] = None) -> Dict[str, Any]:
        """Send data to an external webhook"""
        try:
            if headers is None:
                headers = {}
            
            headers['Content-Type'] = 'application/json'
            
            if secret:
                headers['X-Webhook-Secret'] = secret
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    
                    result = {
                        "status_code": response.status,
                        "success": 200 <= response.status < 300,
                        "response": response_text,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    if response.status != 200:
                        logger.warning(f"Webhook to {url} returned status {response.status}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error sending webhook to {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all registered webhooks"""
        return [
            {
                "webhook_id": webhook_id,
                "registered_at": config["registered_at"],
                "description": config.get("description"),
                "has_secret": bool(config.get("secret"))
            }
            for webhook_id, config in self.webhooks.items()
        ]
    
    async def test_webhook(self, webhook_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a webhook endpoint"""
        if webhook_id not in self.webhooks:
            return {
                "success": False,
                "error": f"Webhook {webhook_id} not found"
            }
        
        webhook_config = self.webhooks[webhook_id]
        endpoint = f"http://{self.host}:{self.port}/webhook/{webhook_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if webhook_config.get("secret"):
                    headers['X-Webhook-Secret'] = webhook_config["secret"]
                
                async with session.post(endpoint, json=test_data, headers=headers) as response:
                    response_text = await response.text()
                    
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "response": response_text,
                        "endpoint": endpoint,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        # Cleanup old webhook registrations (older than 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        to_remove = []
        for webhook_id, config in self.webhooks.items():
            registered_at = datetime.fromisoformat(config["registered_at"])
            if registered_at < cutoff:
                to_remove.append(webhook_id)
        
        for webhook_id in to_remove:
            del self.webhooks[webhook_id]
            logger.info(f"Cleaned up old webhook: {webhook_id}")


class WebhookManager:
    """Manager for webhook connectors"""
    
    def __init__(self):
        self.connectors = {}
    
    async def create_connector(self, name: str, host: str = "0.0.0.0", port: int = 8080) -> WebhookConnector:
        """Create a new webhook connector"""
        if name in self.connectors:
            raise ValueError(f"Connector {name} already exists")
        
        connector = WebhookConnector(host, port)
        await connector.start()
        
        self.connectors[name] = connector
        logger.info(f"Webhook connector created: {name}")
        
        return connector
    
    async def get_connector(self, name: str) -> Optional[WebhookConnector]:
        """Get a webhook connector by name"""
        return self.connectors.get(name)
    
    async def stop_connector(self, name: str):
        """Stop a webhook connector"""
        connector = self.connectors.get(name)
        if connector:
            await connector.stop()
            del self.connectors[name]
            logger.info(f"Webhook connector stopped: {name}")
    
    async def stop_all(self):
        """Stop all webhook connectors"""
        for name in list(self.connectors.keys()):
            await self.stop_connector(name)
    
    def list_connectors(self) -> List[Dict[str, Any]]:
        """List all webhook connectors"""
        return [
            {
                "name": name,
                "host": connector.host,
                "port": connector.port,
                "webhook_count": len(connector.webhooks)
            }
            for name, connector in self.connectors.items()
        ]
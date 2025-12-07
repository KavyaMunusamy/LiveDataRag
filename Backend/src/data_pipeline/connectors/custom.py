import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import aiohttp
from ...config.settings import settings
from ...monitoring.logger import get_logger
from .base import BaseConnector

logger = get_logger(__name__)

class CustomDataConnector(BaseConnector):
    """Custom data connector for user-defined data sources"""
    
    def __init__(self):
        super().__init__()
        self.custom_sources = {}
        self.session = None
    
    async def initialize(self):
        """Initialize custom connectors"""
        self.session = aiohttp.ClientSession()
        
        # Load custom sources from configuration/database
        await self._load_custom_sources()
        
        logger.info(f"Custom connector initialized with {len(self.custom_sources)} sources")
    
    async def _load_custom_sources(self):
        """Load custom data source configurations"""
        # This would load from database or configuration file
        # For now, use example sources
        self.custom_sources = {
            "weather_api": {
                "type": "api",
                "endpoint": "https://api.openweathermap.org/data/2.5/weather",
                "method": "GET",
                "params": {
                    "q": "London,UK",
                    "appid": settings.WEATHER_API_KEY,
                    "units": "metric"
                },
                "interval": 300,  # 5 minutes
                "parser": self._parse_weather_data,
                "enabled": True
            },
            "crypto_prices": {
                "type": "api",
                "endpoint": "https://api.coingecko.com/api/v3/simple/price",
                "method": "GET",
                "params": {
                    "ids": "bitcoin,ethereum",
                    "vs_currencies": "usd",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true"
                },
                "interval": 60,  # 1 minute
                "parser": self._parse_crypto_data,
                "enabled": True
            }
        }
    
    async def fetch_data(self, source_id: str) -> Dict[str, Any]:
        """Fetch data from a custom source"""
        if source_id not in self.custom_sources:
            raise ValueError(f"Unknown custom source: {source_id}")
        
        source_config = self.custom_sources[source_id]
        
        if not source_config.get("enabled", True):
            return {"status": "disabled", "source_id": source_id}
        
        try:
            if source_config["type"] == "api":
                data = await self._fetch_api_data(source_config)
            elif source_config["type"] == "webhook":
                data = await self._fetch_webhook_data(source_config)
            elif source_config["type"] == "database":
                data = await self._fetch_database_data(source_config)
            else:
                raise ValueError(f"Unsupported source type: {source_config['type']}")
            
            # Parse data using custom parser
            parser = source_config.get("parser")
            if parser and callable(parser):
                parsed_data = parser(data, source_config)
            else:
                parsed_data = data
            
            # Add metadata
            parsed_data.update({
                "source_id": source_id,
                "data_type": "custom_data",
                "timestamp": datetime.utcnow().isoformat(),
                "source_type": source_config["type"]
            })
            
            logger.info(f"Custom data fetched from {source_id}: {len(str(parsed_data))} bytes")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to fetch custom data from {source_id}: {e}")
            return {
                "source_id": source_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "error"
            }
    
    async def _fetch_api_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        endpoint = config["endpoint"]
        method = config.get("method", "GET")
        params = config.get("params", {})
        headers = config.get("headers", {})
        
        # Add authentication if provided
        auth = config.get("auth")
        if auth:
            if auth["type"] == "bearer":
                headers["Authorization"] = f"Bearer {auth['token']}"
            elif auth["type"] == "basic":
                import base64
                auth_str = f"{auth['username']}:{auth['password']}"
                headers["Authorization"] = f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        
        async with self.session.request(method, endpoint, params=params, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"API returned status {response.status}")
            
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return await response.json()
            else:
                return {"text": await response.text()}
    
    async def _fetch_webhook_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data via webhook"""
        # Webhooks typically push data, so this might listen for incoming data
        # For now, return empty
        return {"message": "Webhook data would be received asynchronously"}
    
    async def _fetch_database_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from database"""
        from ...database import SessionLocal
        import pandas as pd
        
        db = SessionLocal()
        try:
            query = config.get("query")
            if not query:
                raise ValueError("Database query required")
            
            # Execute query
            result = db.execute(query)
            
            # Convert to list of dicts
            rows = [dict(row._mapping) for row in result]
            
            return {
                "rows": rows,
                "count": len(rows)
            }
        finally:
            db.close()
    
    def _parse_weather_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse weather data"""
        if "error" in data:
            return data
        
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        
        return {
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "description": weather.get("description"),
            "location": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "cloudiness": data.get("clouds", {}).get("all")
        }
    
    def _parse_crypto_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse cryptocurrency data"""
        result = {}
        
        for coin, info in data.items():
            result[coin] = {
                "price_usd": info.get("usd"),
                "market_cap": info.get("usd_market_cap"),
                "volume_24h": info.get("usd_24h_vol"),
                "change_24h": info.get("usd_24h_change")
            }
        
        return result
    
    async def stream_data(self, source_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream data from custom source"""
        config = self.custom_sources.get(source_id)
        if not config:
            raise ValueError(f"Unknown source: {source_id}")
        
        interval = config.get("interval", 60)
        
        while True:
            try:
                data = await self.fetch_data(source_id)
                yield data
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in data stream for {source_id}: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def add_custom_source(self, source_config: Dict[str, Any]) -> str:
        """Add a new custom data source"""
        source_id = f"custom_{len(self.custom_sources) + 1}"
        
        # Validate configuration
        if not self._validate_source_config(source_config):
            raise ValueError("Invalid source configuration")
        
        self.custom_sources[source_id] = source_config
        
        # Persist to database (simplified)
        await self._save_custom_source(source_id, source_config)
        
        logger.info(f"Custom source added: {source_id}")
        return source_id
    
    def _validate_source_config(self, config: Dict[str, Any]) -> bool:
        """Validate custom source configuration"""
        required_fields = ["type"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Type-specific validation
        source_type = config["type"]
        
        if source_type == "api":
            return "endpoint" in config
        elif source_type == "database":
            return "query" in config
        elif source_type == "webhook":
            return "endpoint" in config
        
        return True
    
    async def _save_custom_source(self, source_id: str, config: Dict[str, Any]):
        """Save custom source to database"""
        # This would save to a database table
        # For now, just log
        logger.info(f"Custom source saved: {source_id}")
    
    async def remove_custom_source(self, source_id: str) -> bool:
        """Remove a custom data source"""
        if source_id in self.custom_sources:
            del self.custom_sources[source_id]
            logger.info(f"Custom source removed: {source_id}")
            return True
        return False
    
    def list_custom_sources(self) -> List[Dict[str, Any]]:
        """List all custom data sources"""
        return [
            {
                "id": source_id,
                "type": config["type"],
                "enabled": config.get("enabled", True),
                "interval": config.get("interval"),
                "description": config.get("description", "")
            }
            for source_id, config in self.custom_sources.items()
        ]
    
    async def test_connection(self, source_id: str) -> Dict[str, Any]:
        """Test connection to custom source"""
        try:
            data = await self.fetch_data(source_id)
            
            if "error" in data:
                return {
                    "success": False,
                    "source_id": source_id,
                    "error": data["error"]
                }
            
            return {
                "success": True,
                "source_id": source_id,
                "data_sample": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "source_id": source_id,
                "error": str(e)
            }
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()
            self.session = None
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ...config.settings import settings
from ...monitoring.logger import get_logger
from .storage import TimeAwareVectorStore

logger = get_logger(__name__)

class DataProcessor:
    """Data processor for cleaning, transforming, and enriching data"""
    
    def __init__(self, vector_store: Optional[TimeAwareVectorStore] = None):
        self.vector_store = vector_store
        self.processors = self._register_processors()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _register_processors(self) -> Dict[str, Callable]:
        """Register data processors by data type"""
        return {
            "financial_quote": self._process_financial_data,
            "news_article": self._process_news_data,
            "social_media": self._process_social_data,
            "sensor_data": self._process_sensor_data,
            "custom_data": self._process_custom_data,
            "webhook_data": self._process_webhook_data
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data based on its type"""
        data_type = data.get("data_type", "unknown")
        
        # Get appropriate processor
        processor = self.processors.get(data_type, self._process_generic_data)
        
        try:
            # Process the data
            processed_data = processor(data)
            
            # Add processing metadata
            processed_data.update({
                "processed_at": datetime.utcnow().isoformat(),
                "processing_version": "1.0",
                "original_data_type": data_type
            })
            
            # Cache the result
            self._cache_data(data, processed_data)
            
            logger.info(f"Processed {data_type} data: {len(str(processed_data))} bytes")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process {data_type} data: {e}")
            
            # Return error information
            return {
                "error": str(e),
                "data_type": data_type,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "processing_failed"
            }
    
    def _process_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process financial data"""
        result = {
            "symbol": data.get("symbol", "").upper(),
            "price": float(data.get("price", 0)),
            "change": float(data.get("change", 0)),
            "change_percent": data.get("change_percent", "0%"),
            "volume": int(data.get("volume", 0)),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "source": data.get("source", "unknown"),
            "market_cap": data.get("market_cap"),
            "pe_ratio": data.get("pe_ratio"),
            "dividend_yield": data.get("dividend_yield")
        }
        
        # Calculate additional metrics
        result["price_change_direction"] = "up" if result["change"] > 0 else "down" if result["change"] < 0 else "unchanged"
        
        # Parse percentage
        try:
            percent_str = result["change_percent"].replace("%", "").replace("+", "")
            result["change_percent_value"] = float(percent_str)
        except:
            result["change_percent_value"] = 0.0
        
        # Add volatility indicator
        result["volatility"] = self._calculate_volatility(data)
        
        # Add text for embedding
        result["text_content"] = (
            f"{result['symbol']} trading at ${result['price']:.2f} "
            f"({result['change_percent']}), volume {result['volume']:,}"
        )
        
        return result
    
    def _process_news_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process news article data"""
        result = {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "content": data.get("content", ""),
            "url": data.get("url", ""),
            "image_url": data.get("image_url", ""),
            "published": data.get("published", datetime.utcnow().isoformat()),
            "source_name": data.get("source_name", data.get("source", "unknown")),
            "author": data.get("author", ""),
            "sentiment_score": float(data.get("sentiment_score", 0)),
            "keywords": data.get("keywords", []),
            "category": data.get("category", "general")
        }
        
        # Clean and normalize text
        result["clean_title"] = self._clean_text(result["title"])
        result["clean_description"] = self._clean_text(result["description"])
        result["clean_content"] = self._clean_text(result["content"])[:1000]  # Limit content
        
        # Extract entities
        result["entities"] = self._extract_entities(
            result["clean_title"] + " " + result["clean_description"]
        )
        
        # Calculate urgency score
        result["urgency_score"] = self._calculate_news_urgency(result)
        
        # Add text for embedding
        result["text_content"] = (
            f"{result['title']} - {result['description']}"
        )
        
        return result
    
    def _process_social_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process social media data"""
        result = {
            "platform": data.get("platform", "unknown"),
            "author": data.get("author", ""),
            "content": data.get("content", ""),
            "url": data.get("url", ""),
            "published": data.get("published", datetime.utcnow().isoformat()),
            "likes": int(data.get("likes", 0)),
            "shares": int(data.get("shares", 0)),
            "comments": int(data.get("comments", 0)),
            "sentiment_score": float(data.get("sentiment_score", 0)),
            "hashtags": data.get("hashtags", []),
            "mentions": data.get("mentions", [])
        }
        
        # Clean content
        result["clean_content"] = self._clean_text(result["content"])
        
        # Calculate engagement score
        result["engagement_score"] = self._calculate_engagement_score(result)
        
        # Extract entities and topics
        result["entities"] = self._extract_entities(result["clean_content"])
        
        # Add text for embedding
        result["text_content"] = result["clean_content"]
        
        return result
    
    def _process_sensor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sensor/IoT data"""
        result = {
            "sensor_id": data.get("sensor_id", ""),
            "sensor_type": data.get("sensor_type", "unknown"),
            "value": float(data.get("value", 0)),
            "unit": data.get("unit", ""),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "location": data.get("location", {}),
            "battery_level": data.get("battery_level"),
            "signal_strength": data.get("signal_strength")
        }
        
        # Add derived metrics
        result["status"] = self._determine_sensor_status(result)
        result["anomaly_score"] = self._detect_anomaly(result)
        
        # Add text for embedding
        result["text_content"] = (
            f"Sensor {result['sensor_id']} reading {result['value']} {result['unit']} "
            f"at {result['timestamp']}"
        )
        
        return result
    
    def _process_custom_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process custom data"""
        # Start with original data
        result = dict(data)
        
        # Ensure required fields
        result.setdefault("timestamp", datetime.utcnow().isoformat())
        result.setdefault("source_id", "custom")
        
        # Clean text fields if present
        for field in ["title", "description", "content", "message"]:
            if field in result:
                result[f"clean_{field}"] = self._clean_text(str(result[field]))
        
        # Create embedding text
        text_parts = []
        for field in ["title", "description", "content", "message", "summary"]:
            if field in result:
                text_parts.append(str(result[field]))
        
        result["text_content"] = " ".join(text_parts)[:1000]
        
        return result
    
    def _process_webhook_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook data"""
        result = {
            "webhook_id": data.get("webhook_id", ""),
            "data": data.get("data", {}),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "client_ip": data.get("client_ip", ""),
            "headers": data.get("headers", {}),
            "raw_data": data.get("raw_text")
        }
        
        # Try to extract structured data
        webhook_data = result["data"]
        if isinstance(webhook_data, dict):
            # Copy relevant fields
            for key in ["event", "type", "message", "value", "status"]:
                if key in webhook_data:
                    result[key] = webhook_data[key]
        
        # Create text for embedding
        result["text_content"] = json.dumps(result, ensure_ascii=False)[:1000]
        
        return result
    
    def _process_generic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic/unknown data type"""
        result = dict(data)
        
        # Ensure timestamp
        result.setdefault("timestamp", datetime.utcnow().isoformat())
        
        # Create text for embedding
        text_parts = []
        for key, value in result.items():
            if isinstance(value, (str, int, float, bool)):
                text_parts.append(f"{key}: {value}")
        
        result["text_content"] = " ".join(text_parts)[:1000]
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove special characters but keep basic punctuation
        import re
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
        return text.strip()
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified version)"""
        # In production, use NER model like spaCy
        # This is a simplified version using keyword matching
        
        if not text:
            return []
        
        # Common entity patterns
        patterns = {
            "company": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(Inc|Corp|Corporation|Ltd|LLC)\b',
            "stock_symbol": r'\b[A-Z]{1,5}\b',
            "currency": r'\$[\d,]+(?:\.\d+)?|\d+\s*(?:dollars|USD)',
            "percentage": r'\d+\.?\d*%',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
        }
        
        entities = []
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend([f"{entity_type}:{match}" for match in matches])
        
        return entities
    
    def _calculate_volatility(self, data: Dict[str, Any]) -> float:
        """Calculate volatility score for financial data"""
        # Simplified volatility calculation
        # In production, use historical data
        price = float(data.get("price", 0))
        volume = int(data.get("volume", 0))
        
        if price == 0 or volume == 0:
            return 0.0
        
        # Simple heuristic
        volume_ratio = min(volume / 1000000, 10.0)  # Scale volume
        volatility = volume_ratio * 0.1
        
        return min(volatility, 1.0)
    
    def _calculate_news_urgency(self, news: Dict[str, Any]) -> float:
        """Calculate urgency score for news"""
        score = 0.0
        
        # Check for urgency keywords
        urgency_keywords = [
            "breaking", "urgent", "alert", "crisis", "emergency",
            "immediate", "critical", "warning", "danger"
        ]
        
        text = (news.get("title", "") + " " + news.get("description", "")).lower()
        for keyword in urgency_keywords:
            if keyword in text:
                score += 0.2
        
        # Check sentiment (absolute value)
        sentiment = abs(news.get("sentiment_score", 0))
        score += sentiment * 0.3
        
        # Check recency
        try:
            published = datetime.fromisoformat(news.get("published", "").replace('Z', '+00:00'))
            age_hours = (datetime.utcnow() - published).total_seconds() / 3600
            recency_score = max(0, 1 - (age_hours / 24))  # Decay over 24 hours
            score += recency_score * 0.5
        except:
            pass
        
        return min(score, 1.0)
    
    def _calculate_engagement_score(self, social: Dict[str, Any]) -> float:
        """Calculate engagement score for social media"""
        likes = social.get("likes", 0)
        shares = social.get("shares", 0)
        comments = social.get("comments", 0)
        
        # Weighted engagement formula
        engagement = (
            (likes * 0.3) +
            (shares * 0.5) +
            (comments * 0.2)
        )
        
        # Normalize using log scale
        if engagement > 0:
            engagement = np.log10(engagement + 1)
        
        return min(engagement / 5.0, 1.0)  # Scale to 0-1
    
    def _determine_sensor_status(self, sensor: Dict[str, Any]) -> str:
        """Determine sensor status based on values"""
        value = sensor.get("value", 0)
        sensor_type = sensor.get("sensor_type", "").lower()
        
        # Simple threshold-based status
        if sensor_type == "temperature":
            if value > 40:
                return "critical"
            elif value > 30:
                return "warning"
            elif value < 0:
                return "critical"
            elif value < 10:
                return "warning"
        
        elif sensor_type == "humidity":
            if value > 80:
                return "warning"
            elif value < 20:
                return "warning"
        
        elif sensor_type == "pressure":
            if value > 1100 or value < 900:
                return "warning"
        
        return "normal"
    
    def _detect_anomaly(self, sensor: Dict[str, Any]) -> float:
        """Detect anomaly in sensor data"""
        # Simplified anomaly detection
        # In production, use statistical methods or ML
        
        value = sensor.get("value", 0)
        sensor_type = sensor.get("sensor_type", "")
        
        # Typical ranges for common sensors
        typical_ranges = {
            "temperature": (10, 30),
            "humidity": (30, 70),
            "pressure": (950, 1050)
        }
        
        if sensor_type in typical_ranges:
            min_val, max_val = typical_ranges[sensor_type]
            
            if value < min_val:
                deviation = (min_val - value) / min_val
            elif value > max_val:
                deviation = (value - max_val) / max_val
            else:
                deviation = 0
            
            return min(deviation, 1.0)
        
        return 0.0
    
    def _cache_data(self, original: Dict[str, Any], processed: Dict[str, Any]):
        """Cache processed data"""
        cache_key = hash(json.dumps(original, sort_keys=True))
        self.cache[cache_key] = {
            "data": processed,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Clean old cache entries
        self._clean_cache()
    
    def _clean_cache(self):
        """Clean old cache entries"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.cache_ttl)
        
        to_remove = []
        for key, entry in self.cache.items():
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time < cutoff:
                to_remove.append(key)
        
        for key in to_remove:
            del self.cache[key]
    
    async def batch_process(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple data items in batch"""
        results = []
        
        for data in data_list:
            processed = await self.process(data)
            results.append(processed)
        
        return results
    
    async def store_processed_data(self, data: Dict[str, Any]):
        """Store processed data in vector store"""
        if not self.vector_store:
            logger.warning("Vector store not available for storage")
            return
        
        try:
            # Store in vector database
            doc_id = await self.vector_store.store_data(data)
            
            logger.info(f"Processed data stored with ID: {doc_id}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to store processed data: {e}")
            raise
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "processors_registered": len(self.processors),
            "cache_size": len(self.cache),
            "cache_ttl_seconds": self.cache_ttl,
            "data_types": list(self.processors.keys())
        }
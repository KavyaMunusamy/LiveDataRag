from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from ..data_pipeline.storage import TimeAwareVectorStore
from ..config.settings import settings

class TimeAwareRetriever:
    """Advanced retriever with temporal awareness"""
    
    def __init__(self, vector_store: TimeAwareVectorStore):
        self.vector_store = vector_store
        self.cache = {}  # Simple cache for frequent queries
        
    async def retrieve(
        self,
        query: str,
        context_type: str = "auto",
        time_range: str = "last_24_hours",
        filters: Optional[Dict] = None,
        include_raw: bool = False
    ) -> Dict[str, Any]:
        """Retrieve relevant information with time context"""
        
        # Determine optimal time range based on query
        inferred_range = self._infer_time_range_from_query(query)
        time_range = inferred_range or time_range
        
        # Determine context type if auto
        if context_type == "auto":
            context_type = self._detect_context_type(query)
        
        # Build filters
        search_filters = filters or {}
        if context_type != "all":
            search_filters["data_type"] = context_type
        
        # Perform vector search
        vector_results = self.vector_store.search_with_time_filter(
            query=query,
            time_range=time_range,
            filters=search_filters,
            top_k=15
        )
        
        # Enhance with temporal relationships
        enhanced_results = self._add_temporal_context(vector_results)
        
        # Format for LLM consumption
        context_text = self._format_context(enhanced_results)
        
        # Calculate freshness metrics
        freshness = self._calculate_freshness_metrics(enhanced_results)
        
        return {
            "query": query,
            "context": context_text,
            "raw_results": enhanced_results if include_raw else None,
            "metadata": {
                "result_count": len(enhanced_results),
                "time_range_used": time_range,
                "context_type": context_type,
                "freshness_score": freshness["score"],
                "oldest_data": freshness["oldest"],
                "newest_data": freshness["newest"]
            }
        }
    
    def _infer_time_range_from_query(self, query: str) -> Optional[str]:
        """Infer time range from query text"""
        query_lower = query.lower()
        
        time_keywords = {
            "last hour": "last_hour",
            "last 6 hours": "last_6_hours",
            "today": "last_24_hours",
            "this week": "last_week",
            "this month": "last_month",
            "recent": "last_6_hours",
            "latest": "last_hour",
            "just now": "last_hour",
            "yesterday": "last_24_hours",
        }
        
        for keyword, time_range in time_keywords.items():
            if keyword in query_lower:
                return time_range
        
        # Check for explicit time mentions
        if "hour" in query_lower and "24" not in query_lower:
            return "last_hour"
        elif "day" in query_lower:
            return "last_24_hours"
        elif "week" in query_lower:
            return "last_week"
        
        return None
    
    def _detect_context_type(self, query: str) -> str:
        """Detect what type of data is being asked for"""
        query_lower = query.lower()
        
        financial_terms = ["stock", "price", "market", "trade", "invest", "share", "dollar", "currency"]
        news_terms = ["news", "article", "report", "announce", "update", "headline"]
        social_terms = ["tweet", "post", "social", "comment", "mention", "reddit"]
        
        financial_match = sum(1 for term in financial_terms if term in query_lower)
        news_match = sum(1 for term in news_terms if term in query_lower)
        social_match = sum(1 for term in social_terms if term in query_lower)
        
        if financial_match > news_match and financial_match > social_match:
            return "financial"
        elif news_match > financial_match and news_match > social_match:
            return "news"
        elif social_match > financial_match and social_match > news_match:
            return "social"
        else:
            return "all"
    
    def _add_temporal_context(self, results: List[Dict]) -> List[Dict]:
        """Add temporal relationships between results"""
        if not results:
            return results
        
        # Sort by timestamp
        sorted_results = sorted(
            results,
            key=lambda x: x["metadata"].get("timestamp", ""),
            reverse=True
        )
        
        # Add temporal markers
        for i, result in enumerate(sorted_results):
            metadata = result["metadata"]
            
            # Add recency label
            if "timestamp" in metadata:
                try:
                    doc_time = datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
                    hours_ago = (datetime.utcnow() - doc_time).total_seconds() / 3600
                    
                    if hours_ago < 1:
                        metadata["recency"] = "just now"
                    elif hours_ago < 6:
                        metadata["recency"] = "recent"
                    elif hours_ago < 24:
                        metadata["recency"] = "today"
                    else:
                        metadata["recency"] = f"{int(hours_ago/24)} days ago"
                except:
                    metadata["recency"] = "unknown"
            
            # Add sequence marker if multiple results
            if len(sorted_results) > 1:
                metadata["sequence"] = f"{i+1}/{len(sorted_results)}"
        
        return sorted_results
    
    def _format_context(self, results: List[Dict]) -> str:
        """Format results into LLM-consumable context"""
        if not results:
            return "No relevant data found in the specified time range."
        
        context_parts = ["RELEVANT DATA CONTEXT:"]
        
        for i, result in enumerate(results[:10]):  # Limit to top 10
            metadata = result["metadata"]
            
            # Format based on data type
            if metadata.get("data_type") == "financial_quote":
                context_parts.append(
                    f"[{metadata.get('recency', '')}] {metadata.get('symbol')}: "
                    f"${metadata.get('price')} ({metadata.get('change_percent')}) "
                    f"Volume: {metadata.get('volume'):,}"
                )
            
            elif metadata.get("data_type") == "news_sentiment":
                context_parts.append(
                    f"[{metadata.get('recency', '')}] NEWS for {metadata.get('symbol')}: "
                    f"Sentiment: {metadata.get('avg_sentiment', 0):.2f} "
                    f"({metadata.get('article_count', 0)} articles)"
                )
            
            elif "text_content" in metadata:
                context_parts.append(
                    f"[{metadata.get('recency', '')}] {metadata.get('text_content', '')[:200]}..."
                )
        
        # Add temporal summary
        context_parts.append(f"\nTEMPORAL SUMMARY: Data spans from most recent to oldest.")
        
        return "\n".join(context_parts)
    
    def _calculate_freshness_metrics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate freshness metrics for retrieved data"""
        if not results:
            return {"score": 0, "oldest": None, "newest": None}
        
        timestamps = []
        for result in results:
            metadata = result["metadata"]
            if "timestamp" in metadata:
                try:
                    ts = datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
                    timestamps.append(ts)
                except:
                    continue
        
        if not timestamps:
            return {"score": 0, "oldest": None, "newest": None}
        
        oldest = min(timestamps)
        newest = max(timestamps)
        time_span = (newest - oldest).total_seconds() / 3600
        
        # Freshness score: 1.0 = all within last hour, 0.0 = all older than 24h
        avg_age_hours = sum([(datetime.utcnow() - ts).total_seconds() / 3600 for ts in timestamps]) / len(timestamps)
        freshness_score = max(0, 1 - (avg_age_hours / 24))
        
        return {
            "score": round(freshness_score, 2),
            "oldest": oldest.isoformat(),
            "newest": newest.isoformat(),
            "time_span_hours": round(time_span, 1)
        }
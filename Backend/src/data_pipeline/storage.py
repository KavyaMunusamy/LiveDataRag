import pinecone
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from ..config.settings import settings

class TimeAwareVectorStore:
    """Vector store with time-based metadata filtering"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        
    def initialize(self):
        """Initialize Pinecone index"""
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Create index if it doesn't exist
        if settings.PINECONE_INDEX not in pinecone.list_indexes():
            pinecone.create_index(
                name=settings.PINECONE_INDEX,
                dimension=384,  # all-MiniLM-L6-v2 dimension
                metric="cosine",
                metadata_config={
                    "indexed": ["timestamp", "data_type", "source", "symbol"]
                }
            )
        
        self.index = pinecone.Index(settings.PINECONE_INDEX)
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        return self.embedding_model.encode(text).tolist()
    
    async def store_data(self, data: Dict[str, Any]) -> str:
        """Store data with timestamp metadata"""
        # Prepare text for embedding
        text_content = self._prepare_text_for_embedding(data)
        embedding = self.create_embedding(text_content)
        
        # Create unique ID with timestamp
        doc_id = f"{data.get('data_type', 'unknown')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Prepare metadata with timestamp
        metadata = {
            **data,
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "text_content": text_content[:1000]  # Store truncated text
        }
        
        # Store in vector DB
        self.index.upsert(vectors=[(doc_id, embedding, metadata)])
        return doc_id
    
    def _prepare_text_for_embedding(self, data: Dict[str, Any]) -> str:
        """Prepare data for embedding creation"""
        parts = []
        
        if data.get("data_type") == "financial_quote":
            parts.append(f"Stock {data.get('symbol')} trading at ${data.get('price')}")
            parts.append(f"Change: {data.get('change_percent')}")
            parts.append(f"Volume: {data.get('volume')}")
            
        elif data.get("data_type") == "news_article":
            parts.append(data.get("title", ""))
            parts.append(data.get("description", ""))
            parts.append(f"Sentiment: {data.get('sentiment_score', 0)}")
            
        elif data.get("data_type") == "social_media":
            parts.append(data.get("content", ""))
            parts.append(f"Author: {data.get('author', '')}")
            parts.append(f"Engagement: {data.get('engagement', 0)}")
        
        return " ".join(parts)
    
    def search_with_time_filter(
        self, 
        query: str, 
        time_range: str = "last_24_hours",
        filters: Optional[Dict] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search with time-based filtering"""
        # Create query embedding
        query_embedding = self.create_embedding(query)
        
        # Parse time range
        time_filter = self._parse_time_range(time_range)
        
        # Combine filters
        combined_filters = {}
        if time_filter:
            combined_filters.update(time_filter)
        if filters:
            combined_filters.update(filters)
        
        # Perform search
        results = self.index.query(
            vector=query_embedding,
            filter=combined_filters if combined_filters else None,
            top_k=top_k,
            include_metadata=True
        )
        
        # Process and rank results with time decay
        processed = self._apply_time_decay_ranking(results.matches)
        return processed
    
    def _parse_time_range(self, time_range: str) -> Dict[str, Any]:
        """Parse time range string to filter"""
        now = datetime.utcnow()
        
        if time_range == "last_hour":
            start_time = now - timedelta(hours=1)
        elif time_range == "last_6_hours":
            start_time = now - timedelta(hours=6)
        elif time_range == "last_24_hours":
            start_time = now - timedelta(days=1)
        elif time_range == "last_week":
            start_time = now - timedelta(weeks=1)
        elif time_range == "last_month":
            start_time = now - timedelta(days=30)
        else:
            # Default to 24 hours
            start_time = now - timedelta(days=1)
        
        return {
            "timestamp": {"$gte": start_time.isoformat()}
        }
    
    def _apply_time_decay_ranking(self, matches: List) -> List[Dict[str, Any]]:
        """Apply time decay to search results"""
        ranked_results = []
        
        for match in matches:
            score = match.score
            metadata = match.metadata
            
            # Apply time decay if timestamp exists
            if "timestamp" in metadata:
                try:
                    doc_time = datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
                    hours_old = (datetime.utcnow() - doc_time).total_seconds() / 3600
                    
                    # Exponential decay: e^(-0.1 * hours_old)
                    time_decay = np.exp(-0.1 * hours_old)
                    adjusted_score = score * (0.3 + 0.7 * time_decay)  # 30% base + 70% time adjusted
                except:
                    adjusted_score = score
            else:
                adjusted_score = score
            
            ranked_results.append({
                "id": match.id,
                "score": adjusted_score,
                "metadata": metadata,
                "original_score": score
            })
        
        # Sort by adjusted score
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results
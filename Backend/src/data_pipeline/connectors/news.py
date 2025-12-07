import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import feedparser
from ...config.settings import settings
from ...monitoring.logger import get_logger
from .base import BaseConnector

logger = get_logger(__name__)

class NewsDataConnector(BaseConnector):
    """News data connector for fetching and processing news articles"""
    
    def __init__(self):
        super().__init__()
        self.session = None
        self.news_sources = self._load_news_sources()
        self.last_fetch_time = {}
    
    async def initialize(self):
        """Initialize news connector"""
        self.session = aiohttp.ClientSession()
        logger.info("News connector initialized")
    
    def _load_news_sources(self) -> Dict[str, Dict[str, Any]]:
        """Load news source configurations"""
        return {
            "newsapi": {
                "type": "api",
                "endpoint": "https://newsapi.org/v2/everything",
                "api_key": settings.NEWS_API_KEY,
                "enabled": bool(settings.NEWS_API_KEY)
            },
            "rss": {
                "type": "rss",
                "feeds": [
                    "http://feeds.bbci.co.uk/news/rss.xml",
                    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
                    "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
                ],
                "enabled": True
            },
            "reddit": {
                "type": "api",
                "endpoint": "https://www.reddit.com/r/news/hot.json",
                "enabled": True,
                "limit": 25
            }
        }
    
    async def fetch_news(self, query: Optional[str] = None, 
                        sources: List[str] = None,
                        from_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch news articles"""
        if not from_date:
            from_date = datetime.utcnow() - timedelta(hours=24)
        
        if not sources:
            sources = list(self.news_sources.keys())
        
        all_articles = []
        
        for source in sources:
            if source not in self.news_sources:
                logger.warning(f"Unknown news source: {source}")
                continue
            
            source_config = self.news_sources[source]
            if not source_config.get("enabled", True):
                continue
            
            try:
                if source_config["type"] == "api":
                    articles = await self._fetch_api_news(source, query, from_date)
                elif source_config["type"] == "rss":
                    articles = await self._fetch_rss_news(source_config)
                elif source_config["type"] == "reddit":
                    articles = await self._fetch_reddit_news(source_config)
                else:
                    continue
                
                # Filter by date and add source info
                filtered_articles = []
                for article in articles:
                    article_date = self._parse_article_date(article.get("published"))
                    if article_date and article_date >= from_date:
                        article["source"] = source
                        article["data_type"] = "news_article"
                        filtered_articles.append(article)
                
                all_articles.extend(filtered_articles)
                logger.info(f"Fetched {len(filtered_articles)} articles from {source}")
                
            except Exception as e:
                logger.error(f"Failed to fetch news from {source}: {e}")
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: self._parse_article_date(x.get("published")) or datetime.min, reverse=True)
        
        return all_articles[:100]  # Limit to 100 articles
    
    async def _fetch_api_news(self, source: str, query: Optional[str], from_date: datetime) -> List[Dict[str, Any]]:
        """Fetch news from API sources"""
        if source == "newsapi":
            return await self._fetch_newsapi(query, from_date)
        
        return []
    
    async def _fetch_newsapi(self, query: Optional[str], from_date: datetime) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI"""
        if not settings.NEWS_API_KEY:
            return []
        
        params = {
            "apiKey": settings.NEWS_API_KEY,
            "from": from_date.strftime("%Y-%m-%d"),
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 50
        }
        
        if query:
            params["q"] = query
        
        try:
            async with self.session.get(
                "https://newsapi.org/v2/everything",
                params=params
            ) as response:
                if response.status != 200:
                    logger.error(f"NewsAPI returned status {response.status}")
                    return []
                
                data = await response.json()
                
                if data.get("status") != "ok":
                    return []
                
                articles = data.get("articles", [])
                
                return [
                    {
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "url": article.get("url", ""),
                        "image_url": article.get("urlToImage", ""),
                        "published": article.get("publishedAt", ""),
                        "source_name": article.get("source", {}).get("name", ""),
                        "author": article.get("author", ""),
                        "sentiment_score": self._analyze_sentiment(
                            article.get("title", "") + " " + article.get("description", "")
                        )
                    }
                    for article in articles
                ]
                
        except Exception as e:
            logger.error(f"NewsAPI fetch error: {e}")
            return []
    
    async def _fetch_rss_news(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch news from RSS feeds"""
        articles = []
        
        for feed_url in config.get("feeds", []):
            try:
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Limit to 20 per feed
                    content = ""
                    if hasattr(entry, 'content'):
                        content = entry.content[0].value if entry.content else ""
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    article = {
                        "title": entry.get("title", ""),
                        "description": entry.get("description", ""),
                        "content": content,
                        "url": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source_name": feed.feed.get("title", feed_url),
                        "author": entry.get("author", ""),
                        "sentiment_score": self._analyze_sentiment(
                            entry.get("title", "") + " " + entry.get("description", "")
                        )
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Failed to parse RSS feed {feed_url}: {e}")
                continue
        
        return articles
    
    async def _fetch_reddit_news(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch news from Reddit"""
        try:
            headers = {
                "User-Agent": "LiveDataRAG/1.0"
            }
            
            async with self.session.get(
                config["endpoint"],
                headers=headers,
                params={"limit": config.get("limit", 25)}
            ) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                
                articles = []
                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})
                    
                    article = {
                        "title": post_data.get("title", ""),
                        "description": post_data.get("selftext", "")[:500],  # Truncate
                        "content": post_data.get("selftext", ""),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "published": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                        "source_name": "Reddit",
                        "author": post_data.get("author", ""),
                        "upvotes": post_data.get("ups", 0),
                        "comments": post_data.get("num_comments", 0),
                        "sentiment_score": self._analyze_sentiment(post_data.get("title", ""))
                    }
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.error(f"Reddit fetch error: {e}")
            return []
    
    def _parse_article_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse article date string"""
        if not date_str:
            return None
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common date formats
                formats = [
                    "%a, %d %b %Y %H:%M:%S %Z",
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S"
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
            except:
                pass
        
        return None
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (simple implementation)"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = [
            'good', 'great', 'excellent', 'positive', 'success', 'win', 
            'profit', 'growth', 'up', 'rise', 'bullish', 'optimistic'
        ]
        
        negative_words = [
            'bad', 'poor', 'negative', 'failure', 'loss', 'down',
            'decline', 'fall', 'bearish', 'pessimistic', 'risk', 'warning'
        ]
        
        words = text_lower.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        # Sentiment score from -1 (very negative) to 1 (very positive)
        sentiment = (positive_count - negative_count) / total_words
        
        # Normalize to range -1 to 1
        return max(-1.0, min(1.0, sentiment))
    
    async def search_news(self, keywords: List[str], 
                         time_range: str = "24h",
                         limit: int = 20) -> List[Dict[str, Any]]:
        """Search news by keywords"""
        time_map = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        from_date = datetime.utcnow() - time_map.get(time_range, timedelta(hours=24))
        
        # Fetch news
        all_articles = await self.fetch_news(None, None, from_date)
        
        # Filter by keywords
        filtered_articles = []
        for article in all_articles:
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".lower()
            
            # Check if any keyword is in the text
            matches = sum(1 for keyword in keywords if keyword.lower() in text)
            
            if matches > 0:
                article["keyword_matches"] = matches
                article["matched_keywords"] = [
                    keyword for keyword in keywords 
                    if keyword.lower() in text
                ]
                filtered_articles.append(article)
        
        # Sort by number of keyword matches
        filtered_articles.sort(key=lambda x: x.get("keyword_matches", 0), reverse=True)
        
        return filtered_articles[:limit]
    
    async def get_trending_topics(self, hours: int = 24, top_n: int = 10) -> List[Dict[str, Any]]:
        """Extract trending topics from recent news"""
        from collections import Counter
        import re
        
        # Get recent news
        from_date = datetime.utcnow() - timedelta(hours=hours)
        articles = await self.fetch_news(None, None, from_date)
        
        # Extract words from titles
        all_words = []
        for article in articles:
            title = article.get("title", "")
            # Remove special characters and split
            words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
            all_words.extend(words)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'with', 'that', 'this', 'have', 'from', 'their', 'what'}
        filtered_words = [word for word in all_words if word not in stop_words]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get top N trending words
        trending = [
            {"word": word, "count": count}
            for word, count in word_counts.most_common(top_n)
        ]
        
        return trending
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()
            self.session = None
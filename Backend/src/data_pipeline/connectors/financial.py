import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from ...config.settings import settings

class FinancialDataConnector:
    """Real-time financial data connector"""
    
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
        self.symbols = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"]
        self.session = None
        
    async def connect(self):
        """Establish connection pool"""
        self.session = aiohttp.ClientSession()
        
    async def fetch_realtime_quotes(self) -> List[Dict[str, Any]]:
        """Fetch real-time stock quotes"""
        if not self.session:
            await self.connect()
            
        tasks = []
        for symbol in self.symbols:
            task = self._fetch_symbol_data(symbol)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict)]
    
    async def _fetch_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data for a single symbol"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": settings.FINANCIAL_API_KEY
        }
        
        try:
            async with self.session.get(self.base_url, params=params) as response:
                data = await response.json()
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    processed = {
                        "symbol": symbol,
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent", "0%"),
                        "volume": int(quote.get("06. volume", 0)),
                        "timestamp": datetime.utcnow().isoformat(),
                        "data_type": "financial_quote",
                        "source": "alpha_vantage"
                    }
                    return processed
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return {}
    
    async def fetch_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Fetch news sentiment for a symbol"""
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "apikey": settings.FINANCIAL_API_KEY,
            "limit": 10
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            data = await response.json()
            
            # Process news articles
            if "feed" in data:
                articles = data["feed"][:5]  # Take top 5
                sentiments = [
                    float(article.get("overall_sentiment_score", 0))
                    for article in articles
                ]
                
                return {
                    "symbol": symbol,
                    "avg_sentiment": sum(sentiments) / len(sentiments) if sentiments else 0,
                    "article_count": len(articles),
                    "articles": articles,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data_type": "news_sentiment"
                }
        return {}
    
    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()
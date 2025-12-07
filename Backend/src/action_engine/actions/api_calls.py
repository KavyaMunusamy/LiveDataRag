import aiohttp
import requests
from typing import Dict, Any, Optional
import json
from datetime import datetime
from ...config.settings import settings
from ...monitoring.logger import get_logger
import asyncio

logger = get_logger(__name__)

class APIActionSystem:
    """System for making external API calls as actions"""
    
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.rate_limits = {}
        
    async def execute_api_call(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call with given parameters"""
        endpoint = parameters.get('endpoint')
        method = parameters.get('method', 'GET').upper()
        payload = parameters.get('payload', {})
        headers = parameters.get('headers', {})
        retry_count = parameters.get('retry_count', 3)
        retry_delay = parameters.get('retry_delay', 1)
        
        if not endpoint:
            raise ValueError("API endpoint is required")
        
        # Add default headers
        default_headers = {
            'User-Agent': 'LiveDataRAG/1.0',
            'Content-Type': 'application/json',
            'X-Request-ID': f"rag_{datetime.utcnow().timestamp()}_{hash(str(context)) % 10000:04d}"
        }
        headers = {**default_headers, **headers}
        
        # Check rate limits
        self._check_rate_limit(endpoint)
        
        try:
            # Execute with retries
            for attempt in range(retry_count):
                try:
                    result = await self._make_request(
                        endpoint, method, payload, headers, context
                    )
                    
                    logger.info(f"API call successful: {endpoint}")
                    return {
                        "status": "success",
                        "response": result,
                        "attempts": attempt + 1,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == retry_count - 1:
                        raise
                    
                    logger.warning(f"API call failed (attempt {attempt + 1}/{retry_count}): {e}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    
        except Exception as e:
            logger.error(f"API call failed after {retry_count} attempts: {e}")
            raise
    
    async def _make_request(self, endpoint: str, method: str, payload: Dict, 
                           headers: Dict, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make the actual HTTP request"""
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        
        # Prepare request
        request_params = {
            'url': endpoint,
            'headers': headers,
            'timeout': self.timeout
        }
        
        if method in ['POST', 'PUT', 'PATCH']:
            request_params['json'] = payload
        elif method == 'GET' and payload:
            # Convert payload to query parameters for GET requests
            import urllib.parse
            query_string = urllib.parse.urlencode(payload)
            request_params['url'] = f"{endpoint}?{query_string}"
        
        try:
            async with self.session.request(method, **request_params) as response:
                # Read response
                response_text = await response.text()
                
                # Try to parse as JSON
                try:
                    response_data = await response.json()
                except:
                    response_data = response_text
                
                # Log the request
                self._log_api_call(endpoint, method, response.status, context)
                
                # Check for error status
                if response.status >= 400:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"API returned error {response.status}: {response_text[:200]}",
                        headers=response.headers
                    )
                
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "size": len(response_text)
                }
                
        except asyncio.TimeoutError:
            logger.error(f"API call timeout: {endpoint}")
            raise
        except Exception as e:
            logger.error(f"API call error: {e}")
            raise
    
    def _check_rate_limit(self, endpoint: str):
        """Check and enforce rate limits"""
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # Parse domain from endpoint
        from urllib.parse import urlparse
        domain = urlparse(endpoint).netloc
        
        now = datetime.utcnow()
        minute_key = f"{domain}_{now.strftime('%Y%m%d%H%M')}"
        
        if minute_key not in self.rate_limits:
            self.rate_limits[minute_key] = {
                'count': 0,
                'reset_time': now + timedelta(minutes=1)
            }
        
        # Clean old entries
        to_delete = []
        for key, data in self.rate_limits.items():
            if data['reset_time'] < now:
                to_delete.append(key)
        
        for key in to_delete:
            del self.rate_limits[key]
        
        # Check limit (e.g., 60 requests per minute per domain)
        current = self.rate_limits[minute_key]
        if current['count'] >= 60:
            raise Exception(f"Rate limit exceeded for {domain}")
        
        current['count'] += 1
    
    def _log_api_call(self, endpoint: str, method: str, status: int, context: Dict[str, Any]):
        """Log API call for monitoring"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "context_hash": hash(str(context)) % 10000,
            "action_type": "api_call"
        }
        
        logger.info(f"API_CALL: {json.dumps(log_entry)}")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def validate_endpoint(self, endpoint: str) -> bool:
        """Validate endpoint URL"""
        from urllib.parse import urlparse
        
        try:
            result = urlparse(endpoint)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API call statistics"""
        return {
            "total_calls": sum(data['count'] for data in self.rate_limits.values()),
            "active_limits": len(self.rate_limits),
            "rate_limits": self.rate_limits
        }
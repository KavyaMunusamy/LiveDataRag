import uuid
import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
import re
import hashlib
from functools import wraps
import inspect

def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{unique_id}"


def format_timestamp(timestamp: Any, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return timestamp
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format_str)
    
    return str(timestamp)


def validate_email(email: str) -> bool:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage"""
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def normalize_text(text: str, max_length: Optional[int] = None) -> str:
    """Normalize text: trim, remove extra spaces, optional truncation"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text.strip()


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""


def rate_limit(calls_per_second: float = 1.0):
    """Rate limit decorator"""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = 1.0 / calls_per_second - elapsed
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        
        return wrapper
    
    return decorator


async def async_retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Async retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        return wrapper
    
    return decorator


def format_bytes(size: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def time_it(func):
    """Timing decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    
    return wrapper


def async_time_it(func):
    """Async timing decorator"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    
    return wrapper


def create_hash(data: Any, algorithm: str = 'sha256') -> str:
    """Create hash of data"""
    data_str = json.dumps(data, sort_keys=True) if isinstance(data, (dict, list)) else str(data)
    
    if algorithm == 'md5':
        return hashlib.md5(data_str.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(data_str.encode()).hexdigest()
    else:  # sha256
        return hashlib.sha256(data_str.encode()).hexdigest()


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
    """Mask sensitive data in dictionary"""
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
    
    masked = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            if isinstance(value, str) and len(value) > 4:
                masked[key] = value[:2] + '***' + value[-2:]
            else:
                masked[key] = '***'
        else:
            masked[key] = value
    
    return masked


def get_size_of_object(obj: Any) -> int:
    """Get approximate size of object in bytes"""
    try:
        return len(json.dumps(obj))
    except:
        return len(str(obj))


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Deep update dictionary"""
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            base_dict[key] = deep_update(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict


def get_function_signature(func: Callable) -> str:
    """Get function signature as string"""
    sig = inspect.signature(func)
    params = []
    
    for param in sig.parameters.values():
        param_str = str(param)
        params.append(param_str)
    
    return f"{func.__name__}({', '.join(params)})"


class Timer:
    """Context manager for timing code blocks"""
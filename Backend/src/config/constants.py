"""
Application constants for Live Data RAG with Actions system.
"""

from enum import Enum

class Constants:
    """Application constants"""
    
    # Application
    APP_NAME = "Live Data RAG with Actions"
    APP_VERSION = "1.0.0"
    API_PREFIX = "/api/v1"
    
    # Data types
    DATA_TYPES = {
        "FINANCIAL_QUOTE": "financial_quote",
        "NEWS_ARTICLE": "news_article",
        "SOCIAL_MEDIA": "social_media",
        "SENSOR_DATA": "sensor_data",
        "API_DATA": "api_data",
        "CUSTOM_DATA": "custom_data"
    }
    
    # Action types
    ACTION_TYPES = {
        "ALERT": "alert",
        "API_CALL": "api_call",
        "DATA_UPDATE": "data_update",
        "WORKFLOW_TRIGGER": "workflow_trigger"
    }
    
    # Action statuses
    ACTION_STATUS = {
        "PENDING": "pending",
        "EXECUTED": "executed",
        "FAILED": "failed",
        "BLOCKED": "blocked",
        "REQUIRES_CONFIRMATION": "requires_confirmation"
    }
    
    # Safety levels
    SAFETY_LEVELS = {
        "LOW": "low",      # Maximum automation
        "MEDIUM": "medium", # Balanced
        "HIGH": "high"      # Conservative
    }
    
    # Time ranges for retrieval
    TIME_RANGES = {
        "LAST_HOUR": "last_hour",
        "LAST_6_HOURS": "last_6_hours",
        "LAST_24_HOURS": "last_24_hours",
        "LAST_WEEK": "last_week",
        "LAST_MONTH": "last_month"
    }
    
    # Vector database constants
    VECTOR_DIMENSION = 384  # all-MiniLM-L6-v2
    VECTOR_METRIC = "cosine"
    VECTOR_INDEX_NAME = "live-rag-index"
    
    # LLM models
    LLM_MODELS = {
        "GPT_4_TURBO": "gpt-4-turbo-preview",
        "GPT_3_5_TURBO": "gpt-3.5-turbo",
        "CLAUDE_3_OPUS": "claude-3-opus-20240229",
        "CLAUDE_3_SONNET": "claude-3-sonnet-20240229"
    }
    
    # Embedding models
    EMBEDDING_MODELS = {
        "OPENAI_ADA": "text-embedding-ada-002",
        "OPENAI_3_SMALL": "text-embedding-3-small",
        "OPENAI_3_LARGE": "text-embedding-3-large",
        "SENTENCE_TRANSFORMERS": "all-MiniLM-L6-v2"
    }
    
    # Data source types
    DATA_SOURCES = {
        "FINANCIAL": "financial",
        "NEWS": "news",
        "SOCIAL": "social",
        "SENSOR": "sensor",
        "API": "api",
        "CUSTOM": "custom"
    }
    
    # Rule condition types
    RULE_CONDITIONS = {
        "KEYWORD": "keyword",
        "THRESHOLD": "threshold",
        "PATTERN": "pattern",
        "COMPOSITE": "composite"
    }
    
    # Notification channels
    NOTIFICATION_CHANNELS = {
        "EMAIL": "email",
        "SLACK": "slack",
        "SMS": "sms",
        "IN_APP": "in_app",
        "WEBHOOK": "webhook"
    }
    
    # Alert priorities
    ALERT_PRIORITIES = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low"
    }
    
    # System status
    SYSTEM_STATUS = {
        "ACTIVE": "active",
        "PAUSED": "paused",
        "MAINTENANCE": "maintenance",
        "ERROR": "error"
    }
    
    # Component health
    COMPONENT_HEALTH = {
        "HEALTHY": "healthy",
        "WARNING": "warning",
        "ERROR": "error",
        "OFFLINE": "offline"
    }
    
    # Rate limits
    RATE_LIMITS = {
        "QUERIES_PER_MINUTE": 60,
        "ACTIONS_PER_MINUTE": 100,
        "API_CALLS_PER_MINUTE": 30,
        "DATA_POINTS_PER_MINUTE": 1000
    }
    
    # Safety limits
    SAFETY_LIMITS = {
        "MAX_TRANSACTION_AMOUNT": 10000,
        "MAX_RETRY_ATTEMPTS": 3,
        "MAX_WORKFLOW_DURATION": 300,  # 5 minutes
        "MAX_DATA_ROWS": 1000
    }
    
    # Cache TTLs (in seconds)
    CACHE_TTL = {
        "SHORT": 60,           # 1 minute
        "MEDIUM": 300,         # 5 minutes
        "LONG": 3600,          # 1 hour
        "VERY_LONG": 86400     # 1 day
    }
    
    # HTTP status codes
    HTTP_STATUS = {
        "OK": 200,
        "CREATED": 201,
        "BAD_REQUEST": 400,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "INTERNAL_ERROR": 500,
        "SERVICE_UNAVAILABLE": 503
    }


class ErrorCodes(Enum):
    """Error codes for the application"""
    
    # General errors
    UNKNOWN_ERROR = "ERR_0001"
    VALIDATION_ERROR = "ERR_0002"
    CONFIGURATION_ERROR = "ERR_0003"
    
    # Data errors
    DATA_VALIDATION_ERROR = "ERR_0101"
    DATA_NOT_FOUND = "ERR_0102"
    DATA_PROCESSING_ERROR = "ERR_0103"
    
    # Action errors
    ACTION_VALIDATION_ERROR = "ERR_0201"
    ACTION_EXECUTION_ERROR = "ERR_0202"
    ACTION_SAFETY_BLOCKED = "ERR_0203"
    
    # LLM errors
    LLM_API_ERROR = "ERR_0301"
    LLM_RATE_LIMIT = "ERR_0302"
    LLM_CONTEXT_TOO_LONG = "ERR_0303"
    
    # Vector DB errors
    VECTOR_DB_ERROR = "ERR_0401"
    VECTOR_DB_CONNECTION_ERROR = "ERR_0402"
    
    # Authentication errors
    AUTHENTICATION_ERROR = "ERR_0501"
    AUTHORIZATION_ERROR = "ERR_0502"
    TOKEN_EXPIRED = "ERR_0503"
    
    # Rate limit errors
    RATE_LIMIT_EXCEEDED = "ERR_0601"
    
    # External API errors
    EXTERNAL_API_ERROR = "ERR_0701"
    EXTERNAL_API_TIMEOUT = "ERR_0702"


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
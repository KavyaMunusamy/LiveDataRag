import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from ...config.settings import settings

def setup_logging():
    """Setup logging configuration"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(formatter)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Set levels for specific loggers
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get logger with given name"""
    return logging.getLogger(name)


class StructuredLogger:
    """Structured logger for application events"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set logging context"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear logging context"""
        self.context.clear()
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        extra = {**self.context, **kwargs}
        self.logger.info(message, extra={'extra': extra})
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        extra = {**self.context, **kwargs}
        self.logger.warning(message, extra={'extra': extra})
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        extra = {**self.context, **kwargs}
        self.logger.error(message, extra={'extra': extra})
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        extra = {**self.context, **kwargs}
        self.logger.critical(message, extra={'extra': extra})
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        extra = {**self.context, **kwargs}
        self.logger.debug(message, extra={'extra': extra})
    
    def exception(self, message: str, exc_info: Exception, **kwargs):
        """Log exception with context"""
        extra = {**self.context, **kwargs}
        self.logger.exception(message, exc_info=exc_info, extra={'extra': extra})


# Initialize logging on module import
setup_logging()
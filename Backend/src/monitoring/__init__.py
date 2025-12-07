"""
Monitoring module for Live Data RAG with Actions system.

This module provides logging, metrics, and dashboard functionality.
"""

from .logger import get_logger, setup_logging
from .metrics import MetricsCollector
from .dashboard import DashboardService

__all__ = [
    'get_logger',
    'setup_logging',
    'MetricsCollector',
    'DashboardService'
]

__version__ = '1.0.0'
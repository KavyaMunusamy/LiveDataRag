"""
Data Pipeline module for Live Data RAG with Actions system.

This module handles real-time data ingestion, processing, and storage.
"""

from .connectors.financial import FinancialDataConnector
from .connectors.news import NewsDataConnector
from .connectors.custom import CustomDataConnector
from .connectors.webhook import WebhookConnector, WebhookManager
from .processor import DataProcessor
from .streaming import DataStreamManager
from .storage import TimeAwareVectorStore

__all__ = [
    'FinancialDataConnector',
    'NewsDataConnector',
    'CustomDataConnector',
    'WebhookConnector',
    'WebhookManager',
    'DataProcessor',
    'DataStreamManager',
    'TimeAwareVectorStore'
]

__version__ = '1.0.0'
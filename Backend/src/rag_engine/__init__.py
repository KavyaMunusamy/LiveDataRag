"""
RAG Engine module for Live Data RAG with Actions system.

This module handles retrieval-augmented generation with time-aware capabilities.
"""

from .retriever import TimeAwareRetriever
from .generator import ResponseGenerator
from .temporal import TemporalContextManager

__all__ = [
    'TimeAwareRetriever',
    'ResponseGenerator',
    'TemporalContextManager'
]

__version__ = '1.0.0'
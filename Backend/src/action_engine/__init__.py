"""
Action Engine module for Live Data RAG with Actions system.

This module handles autonomous action execution based on real-time data analysis.
"""

from .decision_maker import ActionDecisionEngine
from .registry import ActionRegistry
from .safety_layer import SafetyLayer
from .actions.alerts import AlertSystem
from .actions.api_calls import APIActionSystem
from .actions.database import DatabaseActionSystem
from .actions.workflow import WorkflowActionSystem

__all__ = [
    'ActionDecisionEngine',
    'ActionRegistry',
    'SafetyLayer',
    'AlertSystem',
    'APIActionSystem',
    'DatabaseActionSystem',
    'WorkflowActionSystem'
]

__version__ = '1.0.0'
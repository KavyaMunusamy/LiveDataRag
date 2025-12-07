from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from .actions.alerts import AlertSystem
from .actions.api_calls import APIActionSystem
from .actions.database import DatabaseActionSystem
from .actions.workflow import WorkflowActionSystem
from ..config.settings import settings
from ..monitoring.logger import get_logger

logger = get_logger(__name__)

class ActionRegistry:
    """Registry for all available actions with safety controls"""
    
    def __init__(self):
        self.alert_system = AlertSystem()
        self.api_system = APIActionSystem()
        self.db_system = DatabaseActionSystem()
        self.workflow_system = WorkflowActionSystem()
        
        self.action_history = []
        self.rate_limits = {}
        self.safety_rules = self._load_safety_rules()
        
    async def execute_action(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
        require_confirmation: bool = False
    ) -> Dict[str, Any]:
        """Execute an action with safety checks"""
        
        # Generate action ID
        action_id = f"act_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(parameters)) % 10000:04d}"
        
        # Safety checks
        safety_check = await self._run_safety_checks(action_type, parameters, context)
        if not safety_check["allowed"]:
            return {
                "action_id": action_id,
                "status": "blocked",
                "reason": safety_check["reason"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Check rate limits
        if not self._check_rate_limit(action_type):
            return {
                "action_id": action_id,
                "status": "rate_limited",
                "reason": "Rate limit exceeded for this action type",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Require confirmation for sensitive actions
        if require_confirmation or action_type in settings.REQUIRED_CONFIRMATION_FOR:
            return {
                "action_id": action_id,
                "status": "requires_confirmation",
                "action_type": action_type,
                "parameters": parameters,
                "confirmation_prompt": f"Confirm {action_type} action?",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Execute the action
        try:
            result = await self._execute_safe(action_type, parameters, context)
            
            # Record in history
            self._record_action({
                "action_id": action_id,
                "type": action_type,
                "parameters": parameters,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "context_hash": hash(str(context))
            })
            
            return {
                "action_id": action_id,
                "status": "executed",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            
            return {
                "action_id": action_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_safe(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """Execute action within try-catch and timeout"""
        
        timeout_seconds = 30  # Maximum execution time
        
        try:
            if action_type == "alert":
                return await asyncio.wait_for(
                    self.alert_system.send_alert(parameters, context),
                    timeout=timeout_seconds
                )
            
            elif action_type == "api_call":
                return await asyncio.wait_for(
                    self.api_system.execute_api_call(parameters, context),
                    timeout=timeout_seconds
                )
            
            elif action_type == "data_update":
                return await asyncio.wait_for(
                    self.db_system.update_data(parameters, context),
                    timeout=timeout_seconds
                )
            
            elif action_type == "workflow_trigger":
                return await asyncio.wait_for(
                    self.workflow_system.trigger_workflow(parameters, context),
                    timeout=timeout_seconds
                )
            
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except asyncio.TimeoutError:
            raise Exception(f"Action timed out after {timeout_seconds} seconds")
    
    async def _run_safety_checks(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run all safety checks for an action"""
        
        checks = [
            self._check_parameter_safety,
            self._check_context_relevance,
            self._check_financial_limits,
            self._check_time_constraints,
            self._check_historical_patterns
        ]
        
        for check in checks:
            result = await check(action_type, parameters, context)
            if not result["allowed"]:
                return result
        
        return {"allowed": True, "reason": "All checks passed"}
    
    async def _check_parameter_safety(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if parameters are safe"""
        
        # Block dangerous API endpoints
        if action_type == "api_call":
            endpoint = parameters.get("endpoint", "")
            blocked_patterns = [
                "delete", "shutdown", "format", "rm -rf",
                "drop database", "format c:", "sudo"
            ]
            
            if any(pattern in endpoint.lower() for pattern in blocked_patterns):
                return {
                    "allowed": False,
                    "reason": "Endpoint contains potentially dangerous operations"
                }
        
        # Validate financial transaction limits
        if action_type in ["api_call", "data_update"]:
            if "amount" in parameters:
                amount = float(parameters["amount"])
                if amount > 10000:  # Example limit
                    return {
                        "allowed": False,
                        "reason": f"Amount ${amount} exceeds safety limit"
                    }
        
        return {"allowed": True, "reason": "Parameters safe"}
    
    def _check_rate_limit(self, action_type: str) -> bool:
        """Check if action is within rate limits"""
        now = datetime.utcnow()
        hour_key = f"{action_type}_{now.strftime('%Y%m%d%H')}"
        
        if hour_key not in self.rate_limits:
            self.rate_limits[hour_key] = {
                "count": 0,
                "reset_time": now + timedelta(hours=1)
            }
        
        # Clean old entries
        to_delete = []
        for key, data in self.rate_limits.items():
            if data["reset_time"] < now:
                to_delete.append(key)
        
        for key in to_delete:
            del self.rate_limits[key]
        
        # Check limit
        current = self.rate_limits[hour_key]
        
        # Different limits per action type
        limits = {
            "alert": 100,
            "api_call": 50,
            "data_update": 200,
            "workflow_trigger": 30
        }
        
        limit = limits.get(action_type, 50)
        
        if current["count"] >= limit:
            return False
        
        current["count"] += 1
        return True
    
    def _record_action(self, action_record: Dict[str, Any]):
        """Record action in history"""
        self.action_history.append(action_record)
        
        # Keep only last 1000 actions
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]
    
    def _load_safety_rules(self) -> List[Dict[str, Any]]:
        """Load safety rules from configuration"""
        return [
            {
                "name": "no_duplicate_actions",
                "description": "Prevent duplicate actions within short timeframe",
                "condition": lambda hist, curr: self._check_duplicates(hist, curr),
                "block_message": "Similar action was recently executed"
            },
            {
                "name": "business_hours_only",
                "description": "Some actions only allowed during business hours",
                "condition": lambda hist, curr: self._check_business_hours(curr),
                "block_message": "Action only allowed during business hours (9AM-5PM)"
            }
        ]
    
    def _check_duplicates(
        self,
        history: List[Dict[str, Any]],
        current_action: Dict[str, Any]
    ) -> bool:
        """Check for duplicate actions in recent history"""
        recent_window = timedelta(minutes=5)
        cutoff = datetime.utcnow() - recent_window
        
        for action in reversed(history[-20:]):  # Check last 20 actions
            action_time = datetime.fromisoformat(action["timestamp"].replace('Z', '+00:00'))
            
            if action_time < cutoff:
                continue
            
            # Check if same type and similar parameters
            if (action["type"] == current_action["type"] and 
                action["context_hash"] == current_action["context_hash"]):
                return False  # Duplicate found
        
        return True  # No duplicate
    
    def _check_business_hours(self, action: Dict[str, Any]) -> bool:
        """Check if action is allowed during current time"""
        # Example: Only allow certain actions during business hours
        restricted_actions = ["data_update", "workflow_trigger"]
        
        if action["type"] not in restricted_actions:
            return True
        
        now = datetime.utcnow()
        hour = now.hour
        
        # Business hours: 9 AM to 5 PM UTC
        return 9 <= hour < 17
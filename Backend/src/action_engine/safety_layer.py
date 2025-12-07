import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from ...config.settings import settings
from ...monitoring.logger import get_logger
from ...database import SessionLocal
from ...models.action_log import ActionLog

logger = get_logger(__name__)

class SafetyLayer:
    """Safety layer for validating and controlling autonomous actions"""
    
    def __init__(self):
        self.blocked_patterns = self._load_blocked_patterns()
        self.safety_rules = self._load_safety_rules()
        self.action_history = []
        self.max_history_size = 1000
        
    async def validate_action(self, action_type: str, parameters: Dict[str, Any], 
                             context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate an action before execution"""
        
        validation_results = []
        
        # 1. Check for blocked patterns
        blocked_check = self._check_blocked_patterns(action_type, parameters)
        validation_results.append(blocked_check)
        
        # 2. Check safety rules
        safety_check = await self._check_safety_rules(action_type, parameters, context)
        validation_results.append(safety_check)
        
        # 3. Check rate limits
        rate_limit_check = await self._check_rate_limits(action_type, context)
        validation_results.append(rate_limit_check)
        
        # 4. Check for duplicate actions
        duplicate_check = await self._check_duplicate_actions(action_type, parameters, context)
        validation_results.append(duplicate_check)
        
        # 5. Check time-based restrictions
        time_check = self._check_time_restrictions(action_type, parameters)
        validation_results.append(time_check)
        
        # 6. Check financial limits (if applicable)
        financial_check = await self._check_financial_limits(parameters, context)
        validation_results.append(financial_check)
        
        # Combine all validation results
        all_passed = all(r[0] for r in validation_results)
        
        if all_passed:
            return True, "All safety checks passed", {
                "checks": [r[2] for r in validation_results],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            failed_checks = [r[1] for r in validation_results if not r[0]]
            return False, f"Safety checks failed: {', '.join(failed_checks)}", {
                "failed_checks": failed_checks,
                "details": [r[2] for r in validation_results if not r[0]]
            }
    
    def _check_blocked_patterns(self, action_type: str, parameters: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check for blocked patterns in action parameters"""
        details = {"blocked_patterns_found": []}
        
        # Convert parameters to string for pattern matching
        param_str = json.dumps(parameters).lower()
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, param_str, re.IGNORECASE):
                details["blocked_patterns_found"].append(pattern)
        
        if details["blocked_patterns_found"]:
            return False, "Blocked patterns detected", details
        
        # Check action-specific blocked patterns
        if action_type == "api_call":
            endpoint = parameters.get("endpoint", "").lower()
            dangerous_endpoints = [
                "delete", "drop", "truncate", "format", "shutdown",
                "sudo", "rm -rf", "chmod 777", "format c:"
            ]
            
            for dangerous in dangerous_endpoints:
                if dangerous in endpoint:
                    details["dangerous_endpoint"] = dangerous
                    return False, "Dangerous API endpoint", details
        
        return True, "No blocked patterns", details
    
    async def _check_safety_rules(self, action_type: str, parameters: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check against configured safety rules"""
        details = {"rules_checked": [], "violations": []}
        
        for rule in self.safety_rules:
            details["rules_checked"].append(rule["name"])
            
            try:
                # Evaluate rule condition
                if await self._evaluate_rule(rule, action_type, parameters, context):
                    details["violations"].append({
                        "rule": rule["name"],
                        "description": rule["description"]
                    })
            except Exception as e:
                logger.error(f"Error evaluating safety rule {rule['name']}: {e}")
                # On error, be safe and fail the check
                details["violations"].append({
                    "rule": rule["name"],
                    "error": str(e)
                })
        
        if details["violations"]:
            return False, f"Safety rules violated: {len(details['violations'])}", details
        
        return True, "All safety rules passed", details
    
    async def _evaluate_rule(self, rule: Dict[str, Any], action_type: str, 
                            parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a single safety rule"""
        rule_type = rule.get("type", "condition")
        
        if rule_type == "condition":
            # Evaluate Python condition
            condition = rule.get("condition", "")
            if condition:
                try:
                    # Create safe evaluation context
                    eval_context = {
                        "action_type": action_type,
                        "parameters": parameters,
                        "context": context,
                        "timestamp": datetime.utcnow(),
                        "settings": settings
                    }
                    
                    # IMPORTANT: In production, use a safe expression evaluator
                    # For demo purposes, we'll use simple string matching
                    return self._simple_condition_eval(condition, eval_context)
                except:
                    return True  # On error, be safe and block
        elif rule_type == "regex":
            # Regex pattern matching
            pattern = rule.get("pattern", "")
            if pattern:
                param_str = json.dumps(parameters)
                return bool(re.search(pattern, param_str))
        
        return False
    
    def _simple_condition_eval(self, condition: str, context: Dict[str, Any]) -> bool:
        """Simple condition evaluation (replace with proper evaluator in production)"""
        # This is a simplified version - in production use a safe expression evaluator
        condition_lower = condition.lower()
        
        # Check for common conditions
        if "amount" in condition_lower and "parameters.get('amount')" in condition_lower:
            # Extract amount value
            amount = context["parameters"].get("amount", 0)
            if ">" in condition_lower:
                threshold = float(condition_lower.split(">")[1].strip())
                return amount > threshold
            elif "<" in condition_lower:
                threshold = float(condition_lower.split("<")[1].strip())
                return amount < threshold
        
        return False
    
    async def _check_rate_limits(self, action_type: str, context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check rate limits for actions"""
        details = {
            "action_type": action_type,
            "rate_limits": self._get_rate_limits(action_type)
        }
        
        # Get recent actions of this type
        recent_actions = await self._get_recent_actions(action_type, minutes=1)
        details["recent_count"] = len(recent_actions)
        
        # Check limits
        limits = self._get_rate_limits(action_type)
        if len(recent_actions) >= limits.get("per_minute", 60):
            details["limit_exceeded"] = "per_minute"
            return False, "Rate limit exceeded (per minute)", details
        
        if len(recent_actions) >= limits.get("per_hour", 1000):
            details["limit_exceeded"] = "per_hour"
            return False, "Rate limit exceeded (per hour)", details
        
        return True, "Rate limits OK", details
    
    async def _check_duplicate_actions(self, action_type: str, parameters: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check for duplicate/recently executed similar actions"""
        details = {"duplicate_check": "passed"}
        
        # Get recent similar actions
        recent_actions = await self._get_recent_actions(action_type, minutes=5)
        
        for action in recent_actions:
            # Compare parameters
            if self._are_parameters_similar(parameters, action.get("parameters", {})):
                details["duplicate_of"] = action.get("action_id")
                details["similarity_score"] = self._calculate_similarity(parameters, action.get("parameters", {}))
                return False, "Duplicate action detected", details
        
        return True, "No duplicates found", details
    
    def _check_time_restrictions(self, action_type: str, parameters: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check time-based restrictions for actions"""
        details = {"time_check": "passed"}
        now = datetime.utcnow()
        
        # Check if action is only allowed during business hours
        restricted_actions = ["data_update", "workflow_trigger", "api_call"]
        if action_type in restricted_actions:
            hour = now.hour
            if hour < 9 or hour >= 17:  # 9 AM to 5 PM UTC
                details["business_hours"] = False
                return False, "Action only allowed during business hours", details
        
        # Check for maintenance window
        maintenance_window = self._get_maintenance_window()
        if maintenance_window["active"]:
            details["maintenance_window"] = True
            return False, "Action blocked during maintenance window", details
        
        return True, "Time restrictions passed", details
    
    async def _check_financial_limits(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check financial transaction limits"""
        details = {"financial_check": "passed"}
        
        # Check for financial parameters
        amount = parameters.get("amount") or parameters.get("value") or parameters.get("price")
        if amount is not None:
            amount = float(amount)
            details["amount"] = amount
            
            # Check against user limits
            user_limit = context.get("user_limits", {}).get("max_transaction", 10000)
            if amount > user_limit:
                details["exceeds_user_limit"] = True
                return False, f"Amount ${amount} exceeds user limit ${user_limit}", details
            
            # Check against system limits
            system_limit = settings.MAX_TRANSACTION_AMOUNT or 50000
            if amount > system_limit:
                details["exceeds_system_limit"] = True
                return False, f"Amount ${amount} exceeds system limit ${system_limit}", details
            
            # Check for suspicious patterns
            if amount % 1000 == 0 and amount > 5000:
                details["suspicious_amount"] = True
                # Don't fail, just flag for review
        
        return True, "Financial limits passed", details
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load blocked patterns from configuration"""
        return [
            r"delete\s+from",
            r"drop\s+table",
            r"truncate\s+table",
            r"rm\s+-rf",
            r"format\s+c:",
            r"chmod\s+777",
            r"sudo\s+",
            r"shutdown",
            r"reboot",
            r"kill\s+process",
            r"injection",
            r"\.\./",  # Path traversal
            r"<script>",  # XSS
            r"union\s+select",  # SQL injection
        ]
    
    def _load_safety_rules(self) -> List[Dict[str, Any]]:
        """Load safety rules from configuration"""
        return [
            {
                "name": "max_amount_per_transaction",
                "description": "Limit transaction amounts",
                "type": "condition",
                "condition": "parameters.get('amount', 0) > 10000"
            },
            {
                "name": "no_sensitive_data_exposure",
                "description": "Prevent exposure of sensitive data",
                "type": "regex",
                "pattern": r"(password|token|secret|key)\s*[:=]\s*['\"].+?['\"]"
            },
            {
                "name": "no_destructive_api_calls",
                "description": "Block destructive API calls",
                "type": "condition",
                "condition": "action_type == 'api_call' and 'delete' in parameters.get('endpoint', '').lower()"
            }
        ]
    
    def _get_rate_limits(self, action_type: str) -> Dict[str, int]:
        """Get rate limits for an action type"""
        limits = {
            "alert": {"per_minute": 100, "per_hour": 1000},
            "api_call": {"per_minute": 60, "per_hour": 500},
            "data_update": {"per_minute": 200, "per_hour": 5000},
            "workflow_trigger": {"per_minute": 30, "per_hour": 300}
        }
        return limits.get(action_type, {"per_minute": 50, "per_hour": 1000})
    
    async def _get_recent_actions(self, action_type: str, minutes: int) -> List[Dict[str, Any]]:
        """Get recent actions from database"""
        try:
            db = SessionLocal()
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            
            # Query database for recent actions
            # This is simplified - implement actual query based on your schema
            actions = db.query(ActionLog).filter(
                ActionLog.action_type == action_type,
                ActionLog.timestamp >= cutoff
            ).order_by(ActionLog.timestamp.desc()).limit(100).all()
            
            return [action.to_dict() for action in actions]
        except Exception as e:
            logger.error(f"Error getting recent actions: {e}")
            return []
        finally:
            db.close()
    
    def _are_parameters_similar(self, params1: Dict[str, Any], params2: Dict[str, Any], threshold: float = 0.8) -> bool:
        """Check if two parameter sets are similar"""
        if not params1 or not params2:
            return False
        
        # Simple similarity check - compare JSON strings
        import hashlib
        
        hash1 = hashlib.md5(json.dumps(params1, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.md5(json.dumps(params2, sort_keys=True).encode()).hexdigest()
        
        return hash1 == hash2
    
    def _calculate_similarity(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> float:
        """Calculate similarity score between two parameter sets"""
        if params1 == params2:
            return 1.0
        
        # Simple implementation
        common_keys = set(params1.keys()) & set(params2.keys())
        if not common_keys:
            return 0.0
        
        similar = 0
        for key in common_keys:
            if params1[key] == params2[key]:
                similar += 1
        
        return similar / max(len(params1), len(params2))
    
    def _get_maintenance_window(self) -> Dict[str, Any]:
        """Get maintenance window configuration"""
        # This would come from configuration/database
        return {
            "active": False,
            "start": "02:00",
            "end": "04:00",
            "timezone": "UTC"
        }
    
    async def log_action_validation(self, action_id: str, validation_result: Tuple[bool, str, Dict[str, Any]]):
        """Log action validation result"""
        self.action_history.append({
            "action_id": action_id,
            "timestamp": datetime.utcnow().isoformat(),
            "validation_result": validation_result
        })
        
        # Keep history size limited
        if len(self.action_history) > self.max_history_size:
            self.action_history = self.action_history[-self.max_history_size:]
    
    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety layer statistics"""
        total_validations = len(self.action_history)
        passed = sum(1 for item in self.action_history if item["validation_result"][0])
        
        return {
            "total_validations": total_validations,
            "passed": passed,
            "blocked": total_validations - passed,
            "success_rate": (passed / total_validations * 100) if total_validations > 0 else 0,
            "recent_validations": self.action_history[-10:] if self.action_history else []
        }
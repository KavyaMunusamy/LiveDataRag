from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import openai
from ..config.settings import settings

class ActionDecisionEngine:
    """Decides whether and what actions to take based on context"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.action_templates = self._load_action_templates()
    
    async def evaluate_for_action(
        self,
        query: str,
        context: str,
        user_rules: List[Dict],
        historical_actions: List[Dict] = None
    ) -> Dict[str, Any]:
        """Evaluate if action should be taken"""
        
        # First, check against user-defined rules
        rule_based_decision = self._check_user_rules(query, context, user_rules)
        
        if rule_based_decision["action_required"]:
            return {
                **rule_based_decision,
                "decision_source": "user_rule",
                "confidence": 1.0
            }
        
        # If no rule matches, use LLM for intelligent decision
        llm_decision = await self._llm_decision_making(query, context, historical_actions)
        
        return {
            **llm_decision,
            "decision_source": "llm_analysis"
        }
    
    def _check_user_rules(
        self,
        query: str,
        context: str,
        user_rules: List[Dict]
    ) -> Dict[str, Any]:
        """Check if any user-defined rule matches"""
        for rule in user_rules:
            if self._rule_matches(rule, query, context):
                return {
                    "action_required": True,
                    "action_type": rule["action_type"],
                    "action_parameters": rule.get("parameters", {}),
                    "matching_rule": rule["name"],
                    "rule_condition": rule["condition"]
                }
        
        return {
            "action_required": False,
            "action_type": None,
            "matching_rule": None
        }
    
    def _rule_matches(self, rule: Dict, query: str, context: str) -> bool:
        """Check if a rule matches the current situation"""
        condition_type = rule["condition"]["type"]
        
        if condition_type == "keyword":
            keywords = rule["condition"]["keywords"]
            text_to_check = f"{query} {context}".lower()
            return any(keyword.lower() in text_to_check for keyword in keywords)
        
        elif condition_type == "threshold":
            # For numeric conditions (e.g., price > 100)
            try:
                value = self._extract_numeric_value(context, rule["condition"]["field"])
                threshold = float(rule["condition"]["threshold"])
                operator = rule["condition"]["operator"]
                
                if operator == "greater_than":
                    return value > threshold
                elif operator == "less_than":
                    return value < threshold
                elif operator == "equals":
                    return abs(value - threshold) < 0.01
            except:
                return False
        
        elif condition_type == "pattern":
            # Regex pattern matching
            import re
            pattern = rule["condition"]["pattern"]
            return bool(re.search(pattern, f"{query} {context}", re.IGNORECASE))
        
        return False
    
    async def _llm_decision_making(
        self,
        query: str,
        context: str,
        historical_actions: List[Dict] = None
    ) -> Dict[str, Any]:
        """Use LLM to decide if action is needed"""
        
        prompt = self._build_decision_prompt(query, context, historical_actions)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            decision = json.loads(response.choices[0].message.content)
            
            # Validate and add metadata
            decision["timestamp"] = datetime.utcnow().isoformat()
            decision["llm_model"] = settings.LLM_MODEL
            
            return decision
            
        except Exception as e:
            print(f"LLM decision error: {e}")
            return {
                "action_required": False,
                "action_type": None,
                "reason": "Decision engine error",
                "confidence": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_decision_prompt(
        self,
        query: str,
        context: str,
        historical_actions: List[Dict]
    ) -> str:
        """Build prompt for LLM decision making"""
        
        history_text = ""
        if historical_actions:
            recent_actions = historical_actions[-5:]  # Last 5 actions
            history_text = "RECENT ACTIONS:\n"
            for action in recent_actions:
                history_text += f"- {action['type']}: {action.get('result', 'executed')}\n"
        
        prompt = f"""
        Analyze this situation and decide if autonomous action should be taken.
        
        USER QUERY: {query}
        
        REAL-TIME CONTEXT: {context}
        
        {history_text}
        
        DECISION CRITERIA:
        1. URGENCY: Is this time-sensitive? Would delay cause negative impact?
        2. CONFIDENCE: Do we have clear, recent data to make a decision?
        3. IMPACT: What's the potential benefit vs risk?
        4. PRECEDENT: Have similar situations required action before?
        5. SAFETY: Any potential for harm or negative consequences?
        
        POSSIBLE ACTION TYPES (only suggest if clearly appropriate):
        - "alert": Send notification (email, SMS, Slack)
        - "data_update": Update database or record
        - "api_call": Call external API
        - "workflow_trigger": Start another process
        - "none": No action needed
        
        Return JSON with this structure:
        {{
            "action_required": boolean,
            "action_type": string (from above list),
            "action_parameters": {{...}}, // if action_required is true
            "reason": string, // explanation of decision
            "confidence": float 0-1, // confidence in decision
            "urgency_score": float 1-10, // how urgent
            "expected_impact": string // "high", "medium", "low"
        }}
        
        BE CONSERVATIVE: Only recommend action if confident and justified.
        """
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """System prompt for action decision LLM"""
        return """You are an autonomous action decision engine. 
        Your goal is to determine when automated actions should be taken based on real-time data.
        
        GUIDELINES:
        1. Safety first: Never suggest actions that could cause harm, financial loss, or privacy violations
        2. Clear justification: Every decision must have a clear, logical reason
        3. Consider timing: Some actions are only valid at certain times
        4. Respect limits: Don't suggest actions that exceed system capabilities
        
        You have access to real-time data and historical context. Make decisions that balance
        responsiveness with caution."""
    
    def _load_action_templates(self) -> Dict[str, Any]:
        """Load predefined action templates"""
        return {
            "alert": {
                "description": "Send notification to user",
                "parameters": {
                    "channel": ["email", "sms", "slack", "in_app"],
                    "message": "string",
                    "priority": ["low", "medium", "high", "critical"]
                },
                "safety_level": "high"
            },
            "data_update": {
                "description": "Update database record",
                "parameters": {
                    "database": "string",
                    "collection": "string",
                    "query": "dict",
                    "update": "dict"
                },
                "safety_level": "medium",
                "requires_validation": True
            },
            "api_call": {
                "description": "Call external API",
                "parameters": {
                    "endpoint": "string",
                    "method": ["GET", "POST", "PUT", "DELETE"],
                    "payload": "dict",
                    "headers": "dict"
                },
                "safety_level": "low",
                "requires_confirmation": True
            }
        }
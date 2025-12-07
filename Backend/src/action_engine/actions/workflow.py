import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
from ...config.settings import settings
from ...monitoring.logger import get_logger
from ..registry import ActionRegistry

logger = get_logger(__name__)

class WorkflowActionSystem:
    """System for triggering and managing workflows"""
    
    def __init__(self, action_registry: Optional[ActionRegistry] = None):
        self.action_registry = action_registry
        self.active_workflows = {}
        self.workflow_templates = self._load_workflow_templates()
    
    async def trigger_workflow(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a workflow"""
        workflow_id = parameters.get('workflow_id')
        workflow_template = parameters.get('template')
        
        if not workflow_id and not workflow_template:
            raise ValueError("Either workflow_id or template is required")
        
        # Generate workflow ID
        workflow_id = workflow_id or f"workflow_{uuid.uuid4().hex[:8]}"
        
        # Get workflow definition
        if workflow_template:
            workflow_def = self._get_template(workflow_template)
        else:
            workflow_def = parameters.get('definition', {})
        
        if not workflow_def:
            raise ValueError("Workflow definition is required")
        
        # Start workflow execution
        workflow_task = asyncio.create_task(
            self._execute_workflow(workflow_id, workflow_def, context, parameters)
        )
        
        # Store workflow info
        self.active_workflows[workflow_id] = {
            "task": workflow_task,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "definition": workflow_def,
            "context": context
        }
        
        logger.info(f"Workflow '{workflow_id}' started")
        
        return {
            "status": "started",
            "workflow_id": workflow_id,
            "task_id": id(workflow_task),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_workflow(self, workflow_id: str, definition: Dict[str, Any], 
                               context: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps"""
        steps = definition.get('steps', [])
        max_retries = definition.get('max_retries', 3)
        timeout = definition.get('timeout', 300)  # 5 minutes default
        parallel = definition.get('parallel', False)
        
        results = []
        errors = []
        
        try:
            # Set timeout for entire workflow
            await asyncio.wait_for(
                self._execute_steps(steps, context, parallel, max_retries, results, errors),
                timeout=timeout
            )
            
            # Update workflow status
            self.active_workflows[workflow_id].update({
                "status": "completed" if not errors else "completed_with_errors",
                "completed_at": datetime.utcnow().isoformat(),
                "results": results,
                "errors": errors
            })
            
            logger.info(f"Workflow '{workflow_id}' completed")
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "step_count": len(steps),
                "successful_steps": len([r for r in results if r.get('status') == 'success']),
                "failed_steps": len(errors),
                "results": results,
                "errors": errors,
                "duration": self._calculate_duration(workflow_id)
            }
            
        except asyncio.TimeoutError:
            self.active_workflows[workflow_id].update({
                "status": "timeout",
                "completed_at": datetime.utcnow().isoformat()
            })
            
            logger.error(f"Workflow '{workflow_id}' timed out after {timeout} seconds")
            
            raise Exception(f"Workflow timed out after {timeout} seconds")
            
        except Exception as e:
            self.active_workflows[workflow_id].update({
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error": str(e)
            })
            
            logger.error(f"Workflow '{workflow_id}' failed: {e}")
            
            raise
    
    async def _execute_steps(self, steps: List[Dict], context: Dict[str, Any], 
                            parallel: bool, max_retries: int, 
                            results: List, errors: List):
        """Execute workflow steps sequentially or in parallel"""
        if parallel:
            # Execute steps in parallel
            tasks = []
            for step in steps:
                task = asyncio.create_task(
                    self._execute_step_with_retry(step, context, max_retries)
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(step_results):
                if isinstance(result, Exception):
                    errors.append({
                        "step": steps[i].get('name', f'step_{i}'),
                        "error": str(result)
                    })
                else:
                    results.append(result)
        else:
            # Execute steps sequentially
            for i, step in enumerate(steps):
                try:
                    result = await self._execute_step_with_retry(step, context, max_retries)
                    results.append(result)
                    
                    # Update context with step result for next steps
                    if result.get('output'):
                        context[f"step_{i}_result"] = result['output']
                        
                except Exception as e:
                    errors.append({
                        "step": step.get('name', f'step_{i}'),
                        "error": str(e)
                    })
                    
                    # Check if workflow should continue on error
                    if not step.get('continue_on_error', False):
                        raise
    
    async def _execute_step_with_retry(self, step: Dict[str, Any], context: Dict[str, Any], 
                                      max_retries: int) -> Dict[str, Any]:
        """Execute a single step with retry logic"""
        step_type = step.get('type', 'action')
        step_name = step.get('name', 'unnamed_step')
        step_params = step.get('parameters', {})
        
        # Merge context into parameters
        step_params = self._merge_context(step_params, context)
        
        for attempt in range(max_retries):
            try:
                if step_type == 'action':
                    result = await self._execute_action_step(step_name, step_params, context)
                elif step_type == 'delay':
                    result = await self._execute_delay_step(step_params)
                elif step_type == 'condition':
                    result = await self._execute_condition_step(step_params, context)
                elif step_type == 'webhook':
                    result = await self._execute_webhook_step(step_params)
                else:
                    raise ValueError(f"Unknown step type: {step_type}")
                
                logger.info(f"Step '{step_name}' completed successfully")
                return {
                    "step": step_name,
                    "type": step_type,
                    "status": "success",
                    "attempts": attempt + 1,
                    "output": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Step '{step_name}' failed after {max_retries} attempts: {e}")
                    raise
                
                logger.warning(f"Step '{step_name}' failed (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _execute_action_step(self, action_name: str, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action step"""
        if not self.action_registry:
            raise ValueError("Action registry not available")
        
        return await self.action_registry.execute_action(
            action_type=action_name,
            parameters=parameters,
            context=context,
            require_confirmation=False
        )
    
    async def _execute_delay_step(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a delay step"""
        delay_seconds = parameters.get('seconds', 0)
        await asyncio.sleep(delay_seconds)
        
        return {
            "delayed_seconds": delay_seconds,
            "message": f"Delayed for {delay_seconds} seconds"
        }
    
    async def _execute_condition_step(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a condition step"""
        condition = parameters.get('condition')
        if_true = parameters.get('if_true')
        if_false = parameters.get('if_false')
        
        # Evaluate condition
        condition_result = self._evaluate_condition(condition, context)
        
        # Return appropriate result
        if condition_result:
            return {
                "condition": condition,
                "result": True,
                "branch": "if_true",
                "output": if_true
            }
        else:
            return {
                "condition": condition,
                "result": False,
                "branch": "if_false",
                "output": if_false
            }
    
    async def _execute_webhook_step(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a webhook step"""
        import aiohttp
        
        url = parameters.get('url')
        method = parameters.get('method', 'POST')
        payload = parameters.get('payload', {})
        headers = parameters.get('headers', {})
        
        if not url:
            raise ValueError("Webhook URL is required")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=payload, headers=headers) as response:
                response_text = await response.text()
                
                return {
                    "status_code": response.status,
                    "response": response_text,
                    "url": url,
                    "method": method
                }
    
    def _evaluate_condition(self, condition: Any, context: Dict[str, Any]) -> bool:
        """Evaluate a condition"""
        if isinstance(condition, bool):
            return condition
        
        if isinstance(condition, str):
            # Simple expression evaluation
            try:
                # Replace context variables
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        condition = condition.replace(f"{{{{{key}}}}}", str(value))
                
                # Safe evaluation (consider using a proper expression evaluator)
                # For now, just check if it's a comparison
                if '==' in condition:
                    left, right = condition.split('==', 1)
                    return left.strip() == right.strip()
                elif '!=' in condition:
                    left, right = condition.split('!=', 1)
                    return left.strip() != right.strip()
                elif '>' in condition:
                    left, right = condition.split('>', 1)
                    return float(left.strip()) > float(right.strip())
                elif '<' in condition:
                    left, right = condition.split('<', 1)
                    return float(left.strip()) < float(right.strip())
                
                # If it's just a string, check if it's truthy
                return condition.lower() in ['true', 'yes', '1', 'on']
                
            except:
                return False
        
        return bool(condition)
    
    def _merge_context(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Merge context variables into parameters"""
        import copy
        
        params = copy.deepcopy(parameters)
        
        def replace_variables(obj):
            if isinstance(obj, dict):
                return {k: replace_variables(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_variables(item) for item in obj]
            elif isinstance(obj, str):
                # Replace {{variable}} patterns
                for key, value in context.items():
                    if isinstance(value, (str, int, float)):
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in obj:
                            obj = obj.replace(placeholder, str(value))
                return obj
            else:
                return obj
        
        return replace_variables(params)
    
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load predefined workflow templates"""
        return {
            "data_pipeline": {
                "name": "Data Processing Pipeline",
                "description": "Process data through multiple stages",
                "steps": [
                    {
                        "name": "fetch_data",
                        "type": "action",
                        "action_type": "api_call",
                        "parameters": {
                            "endpoint": "{{data_source}}",
                            "method": "GET"
                        }
                    },
                    {
                        "name": "process_data",
                        "type": "action",
                        "action_type": "data_update",
                        "parameters": {
                            "table": "processed_data",
                            "operation": "insert",
                            "data": {
                                "raw_data": "{{step_0_result.output.data}}",
                                "processed_at": "{{timestamp}}"
                            }
                        }
                    },
                    {
                        "name": "send_notification",
                        "type": "action",
                        "action_type": "alert",
                        "parameters": {
                            "channel": "slack",
                            "message": "Data processing completed successfully"
                        }
                    }
                ]
            },
            "monitoring_alert": {
                "name": "Monitoring Alert Workflow",
                "description": "Handle monitoring alerts with escalation",
                "steps": [
                    {
                        "name": "initial_alert",
                        "type": "action",
                        "action_type": "alert",
                        "parameters": {
                            "channel": "slack",
                            "message": "Monitoring alert triggered: {{alert_message}}",
                            "priority": "high"
                        }
                    },
                    {
                        "name": "check_status",
                        "type": "delay",
                        "parameters": {
                            "seconds": 300  # 5 minutes
                        }
                    },
                    {
                        "name": "escalate_if_needed",
                        "type": "condition",
                        "parameters": {
                            "condition": "{{still_alerting}}",
                            "if_true": {
                                "type": "action",
                                "action_type": "alert",
                                "parameters": {
                                    "channel": "email",
                                    "message": "ALERT ESCALATION: Issue not resolved",
                                    "priority": "critical"
                                }
                            },
                            "if_false": {
                                "type": "action",
                                "action_type": "alert",
                                "parameters": {
                                    "channel": "slack",
                                    "message": "Alert resolved",
                                    "priority": "low"
                                }
                            }
                        }
                    }
                ]
            }
        }
    
    def _get_template(self, template_name: str) -> Dict[str, Any]:
        """Get workflow template by name"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        return self.workflow_templates[template_name]
    
    def _calculate_duration(self, workflow_id: str) -> float:
        """Calculate workflow duration in seconds"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return 0
        
        started = datetime.fromisoformat(workflow['started_at'])
        completed = datetime.fromisoformat(workflow.get('completed_at', datetime.utcnow().isoformat()))
        
        return (completed - started).total_seconds()
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow"""
        workflow = self.active_workflows.get(workflow_id)
        
        if not workflow:
            return {"status": "not_found"}
        
        # Check if task is done
        task = workflow['task']
        if task.done():
            try:
                result = task.result()
                return {
                    "status": workflow['status'],
                    "result": result,
                    "started_at": workflow['started_at'],
                    "completed_at": workflow.get('completed_at'),
                    "definition": workflow['definition']
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e),
                    "started_at": workflow['started_at'],
                    "completed_at": workflow.get('completed_at')
                }
        else:
            return {
                "status": "running",
                "started_at": workflow['started_at'],
                "elapsed_seconds": self._calculate_duration(workflow_id)
            }
    
    async def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a running workflow"""
        workflow = self.active_workflows.get(workflow_id)
        
        if not workflow:
            return {"status": "not_found"}
        
        task = workflow['task']
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        workflow['status'] = 'cancelled'
        workflow['completed_at'] = datetime.utcnow().isoformat()
        
        return {
            "status": "cancelled",
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows"""
        return [
            {
                "workflow_id": wf_id,
                "status": info['status'],
                "started_at": info['started_at'],
                "elapsed_seconds": self._calculate_duration(wf_id)
            }
            for wf_id, info in self.active_workflows.items()
        ]
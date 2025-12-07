import openai
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from ...config.settings import settings
from ...monitoring.logger import get_logger
from ...monitoring.metrics import metrics_collector

logger = get_logger(__name__)

class ResponseGenerator:
    """Response generator for RAG system using LLMs"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Response templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load response templates"""
        return {
            "analysis": """Based on the latest information available:

{context}

Analysis: {analysis}

Recommendation: {recommendation}

Confidence: {confidence}/10
Urgency: {urgency}/10
Expected Impact: {impact}""",
            
            "alert": """🚨 ALERT: {title}

{message}

Context: {context}

Action Recommended: {action}
Priority: {priority}
Timestamp: {timestamp}""",
            
            "summary": """📊 SUMMARY

Key Points:
{key_points}

Trends Identified:
{trends}

Next Steps:
{next_steps}

Generated: {timestamp}"""
        }
    
    async def generate_response(self, 
                               query: str, 
                               context: str, 
                               metadata: Dict[str, Any],
                               response_type: str = "analysis") -> Dict[str, Any]:
        """Generate response using LLM"""
        start_time = datetime.utcnow()
        
        try:
            # Prepare prompt
            prompt = self._build_prompt(query, context, metadata, response_type)
            
            # Call LLM
            response = await self._call_llm(prompt, response_type)
            
            # Process response
            processed_response = self._process_response(
                response, query, context, metadata, response_type
            )
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics_collector.record_query(
                query_type=response_type,
                status="success",
                duration=duration
            )
            
            logger.info(f"Response generated in {duration:.2f}s")
            
            return processed_response
            
        except Exception as e:
            # Record error
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics_collector.record_query(
                query_type=response_type,
                status="error",
                duration=duration
            )
            metrics_collector.record_error(
                error_type="llm_error",
                component="response_generator",
                message=str(e)
            )
            
            logger.error(f"Failed to generate response: {e}")
            
            # Return error response
            return {
                "query": query,
                "response": f"Error generating response: {str(e)}",
                "type": response_type,
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata
            }
    
    def _build_prompt(self, 
                     query: str, 
                     context: str, 
                     metadata: Dict[str, Any],
                     response_type: str) -> str:
        """Build prompt for LLM"""
        
        system_prompt = self._get_system_prompt(response_type)
        
        user_prompt = f"""Query: {query}

Relevant Data Context:
{context}

Additional Metadata:
- Data Freshness: {metadata.get('freshness_score', 0)}/1.0
- Time Range: {metadata.get('time_range_used', 'unknown')}
- Data Sources: {metadata.get('context_type', 'multiple')}
- Result Count: {metadata.get('result_count', 0)}
- Oldest Data: {metadata.get('oldest_data', 'unknown')}
- Newest Data: {metadata.get('newest_data', 'unknown')}

Please provide a {response_type} based on this information."""
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _get_system_prompt(self, response_type: str) -> str:
        """Get system prompt based on response type"""
        prompts = {
            "analysis": """You are a financial and data analysis assistant. 
            Analyze the provided data and provide insights, recommendations, and risk assessments.
            Be concise, accurate, and data-driven.
            Include confidence levels and urgency where applicable.""",
            
            "alert": """You are an alert generation system.
            Create clear, actionable alerts based on the data.
            Include severity levels, recommended actions, and context.
            Be urgent but accurate.""",
            
            "summary": """You are a summarization system.
            Create comprehensive summaries of data and trends.
            Highlight key points, patterns, and implications.
            Be thorough but concise.""",
            
            "explanation": """You are an explanation system.
            Explain complex data and concepts in simple terms.
            Provide context, implications, and next steps.
            Be educational and informative."""
        }
        
        return prompts.get(response_type, prompts["analysis"])
    
    async def _call_llm(self, prompt: str, response_type: str) -> str:
        """Call LLM API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(response_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30
            )
            
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _process_response(self, 
                         response: str, 
                         query: str, 
                         context: str, 
                         metadata: Dict[str, Any],
                         response_type: str) -> Dict[str, Any]:
        """Process LLM response"""
        # Extract structured information if possible
        structured_data = self._extract_structured_data(response, response_type)
        
        # Calculate confidence based on metadata
        confidence = self._calculate_confidence(metadata, structured_data)
        
        # Determine urgency
        urgency = self._determine_urgency(query, response, metadata)
        
        # Create final response
        result = {
            "query": query,
            "response": response,
            "type": response_type,
            "structured_data": structured_data,
            "confidence": confidence,
            "urgency": urgency,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                **metadata,
                "model_used": self.model,
                "response_length": len(response)
            }
        }
        
        return result
    
    def _extract_structured_data(self, response: str, response_type: str) -> Dict[str, Any]:
        """Extract structured data from response"""
        try:
            if response_type == "analysis":
                # Try to find key-value pairs
                import re
                
                structured = {}
                
                # Look for confidence
                confidence_match = re.search(r'Confidence[:\s]*(\d+)/10', response)
                if confidence_match:
                    structured["confidence"] = int(confidence_match.group(1))
                
                # Look for urgency
                urgency_match = re.search(r'Urgency[:\s]*(\d+)/10', response)
                if urgency_match:
                    structured["urgency"] = int(urgency_match.group(1))
                
                # Look for impact
                impact_match = re.search(r'Expected Impact[:\s]*(\w+)', response)
                if impact_match:
                    structured["impact"] = impact_match.group(1)
                
                return structured
                
            elif response_type == "alert":
                # Extract alert components
                import re
                
                structured = {}
                
                # Extract priority
                priority_match = re.search(r'Priority[:\s]*(\w+)', response, re.IGNORECASE)
                if priority_match:
                    structured["priority"] = priority_match.group(1).lower()
                
                # Extract action
                action_match = re.search(r'Action Recommended[:\s]*(.+?)(?:\n|$)', response)
                if action_match:
                    structured["recommended_action"] = action_match.group(1).strip()
                
                return structured
                
            else:
                return {}
                
        except Exception as e:
            logger.warning(f"Failed to extract structured data: {e}")
            return {}
    
    def _calculate_confidence(self, metadata: Dict[str, Any], structured_data: Dict[str, Any]) -> float:
        """Calculate confidence score"""
        confidence = 0.5  # Base confidence
        
        # Adjust based on data freshness
        freshness = metadata.get('freshness_score', 0)
        confidence += freshness * 0.3
        
        # Adjust based on result count
        result_count = metadata.get('result_count', 0)
        if result_count > 5:
            confidence += 0.1
        elif result_count == 0:
            confidence -= 0.2
        
        # Adjust based on extracted confidence from response
        if 'confidence' in structured_data:
            response_confidence = structured_data['confidence'] / 10
            confidence = (confidence + response_confidence) / 2
        
        return min(max(confidence, 0), 1)  # Clamp to 0-1
    
    def _determine_urgency(self, query: str, response: str, metadata: Dict[str, Any]) -> float:
        """Determine urgency score"""
        urgency = 0.3  # Base urgency
        
        # Check for urgency keywords in query
        urgency_keywords = [
            'urgent', 'immediate', 'now', 'asap', 'emergency',
            'critical', 'important', 'time-sensitive', 'alert'
        ]
        
        query_lower = query.lower()
        for keyword in urgency_keywords:
            if keyword in query_lower:
                urgency += 0.2
                break
        
        # Check for urgency in response
        response_lower = response.lower()
        for keyword in urgency_keywords:
            if keyword in response_lower:
                urgency += 0.2
                break
        
        # Adjust based on data freshness
        freshness = metadata.get('freshness_score', 0)
        if freshness > 0.8:  # Very fresh data
            urgency += 0.1
        
        # Check for financial terms (often time-sensitive)
        financial_terms = ['stock', 'price', 'market', 'trade', 'buy', 'sell']
        for term in financial_terms:
            if term in query_lower:
                urgency += 0.1
                break
        
        return min(max(urgency, 0), 1)  # Clamp to 0-1
    
    async def generate_multiple_responses(self, 
                                         queries: List[str], 
                                         contexts: List[str],
                                         response_types: List[str]) -> List[Dict[str, Any]]:
        """Generate multiple responses in batch"""
        tasks = []
        
        for query, context, response_type in zip(queries, contexts, response_types):
            # Create metadata for each
            metadata = {
                "batch_index": len(tasks),
                "response_type": response_type
            }
            
            task = self.generate_response(query, context, metadata, response_type)
            tasks.append(task)
        
        # Execute all tasks
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Batch response {i} failed: {response}")
                processed_responses.append({
                    "query": queries[i],
                    "response": f"Error: {str(response)}",
                    "type": response_types[i],
                    "status": "error",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                processed_responses.append(response)
        
        return processed_responses
    
    def format_response(self, 
                       response_data: Dict[str, Any], 
                       format: str = "text") -> str:
        """Format response in different formats"""
        if format == "text":
            return self._format_text_response(response_data)
        elif format == "html":
            return self._format_html_response(response_data)
        elif format == "markdown":
            return self._format_markdown_response(response_data)
        elif format == "json":
            return json.dumps(response_data, indent=2)
        else:
            return str(response_data)
    
    def _format_text_response(self, response_data: Dict[str, Any]) -> str:
        """Format as plain text"""
        response = response_data.get("response", "")
        
        # Add metadata if available
        if "confidence" in response_data:
            response += f"\n\nConfidence: {response_data['confidence']:.0%}"
        
        if "urgency" in response_data:
            response += f"\nUrgency: {response_data['urgency']:.0%}"
        
        response += f"\n\nGenerated at: {response_data.get('timestamp', '')}"
        
        return response
    
    def _format_html_response(self, response_data: Dict[str, Any]) -> str:
        """Format as HTML"""
        response = response_data.get("response", "")
        
        # Convert to HTML
        html = f"""
        <div class="rag-response">
            <div class="response-content">
                {response.replace('\n', '<br>')}
            </div>
            <div class="response-metadata">
                <small>
                    Confidence: <span class="confidence">{response_data.get('confidence', 0):.0%}</span> | 
                    Urgency: <span class="urgency">{response_data.get('urgency', 0):.0%}</span> | 
                    Generated: {response_data.get('timestamp', '')}
                </small>
            </div>
        </div>
        """
        
        return html
    
    def _format_markdown_response(self, response_data: Dict[str, Any]) -> str:
        """Format as Markdown"""
        response = response_data.get("response", "")
        
        md = f"""
{response}

---
**Confidence**: {response_data.get('confidence', 0):.0%}  
**Urgency**: {response_data.get('urgency', 0):.0%}  
**Generated**: {response_data.get('timestamp', '')}
"""
        
        return md
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        stats = metrics_collector.get_stats()
        
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "query_stats": stats.get("queries", {}),
            "error_stats": stats.get("errors", {}),
            "templates_available": list(self.templates.keys())
        }
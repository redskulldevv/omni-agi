from typing import Dict, List, Optional, Union
from datetime import datetime
import random
import json
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    ANALYSIS = "analysis"
    TRADE = "trade"
    ERROR = "error"
    INFO = "info"
    SOCIAL = "social"
    WARNING = "warning"
    SUCCESS = "success"

@dataclass
class ResponseTemplate:
    """Template for agent responses"""
    type: ResponseType
    templates: List[str]
    requires_context: bool = False
    formatting: Optional[Dict[str, str]] = None

class ResponseManager:
    """Manages agent response generation"""
    
    def __init__(self):
        self.templates = self._init_templates()
        self.response_history: List[Dict] = []
        
    def _init_templates(self) -> Dict[ResponseType, ResponseTemplate]:
        """Initialize response templates"""
        return {
            ResponseType.ANALYSIS: ResponseTemplate(
                type=ResponseType.ANALYSIS,
                templates=[
                    "Based on my analysis: {analysis}",
                    "My market analysis indicates: {analysis}",
                    "After examining the data: {analysis}"
                ],
                requires_context=True
            ),
            
            ResponseType.TRADE: ResponseTemplate(
                type=ResponseType.TRADE,
                templates=[
                    "Trade executed: {details}",
                    "Transaction complete: {details}",
                    "Trade summary: {details}"
                ],
                requires_context=True,
                formatting={"details": "json"}
            ),
            
            ResponseType.ERROR: ResponseTemplate(
                type=ResponseType.ERROR,
                templates=[
                    "Error encountered: {error}. Action: {action}",
                    "Issue detected: {error}. Recommended action: {action}",
                    "An error occurred: {error}. Please {action}"
                ],
                requires_context=True
            ),
            
            ResponseType.INFO: ResponseTemplate(
                type=ResponseType.INFO,
                templates=[
                    "Information: {message}",
                    "Note: {message}",
                    "For your information: {message}"
                ],
                requires_context=True
            ),
            
            ResponseType.SOCIAL: ResponseTemplate(
                type=ResponseType.SOCIAL,
                templates=[
                    "Community update: {message}",
                    "Social engagement: {message}",
                    "Community message: {message}"
                ],
                requires_context=True
            ),
            
            ResponseType.WARNING: ResponseTemplate(
                type=ResponseType.WARNING,
                templates=[
                    "⚠️ Warning: {warning}",
                    "⚠️ Caution: {warning}",
                    "⚠️ Important notice: {warning}"
                ],
                requires_context=True
            ),
            
            ResponseType.SUCCESS: ResponseTemplate(
                type=ResponseType.SUCCESS,
                templates=[
                    "✅ Success: {message}",
                    "✅ Completed: {message}",
                    "✅ Operation successful: {message}"
                ],
                requires_context=True
            )
        }
        
    def generate_response(
        self,
        response_type: ResponseType,
        context: Dict,
        emotional_state: Optional[Dict] = None
    ) -> str:
        """Generate appropriate response"""
        try:
            template = self.templates.get(response_type)
            if not template:
                raise ValueError(f"Unknown response type: {response_type}")
                
            if template.requires_context and not context:
                raise ValueError("Context required for this response type")
                
            # Select template
            base_template = random.choice(template.templates)
            
            # Format context if needed
            formatted_context = self._format_context(
                context,
                template.formatting
            )
            
            # Generate response
            response = base_template.format(**formatted_context)
            
            # Add emotional modulation if provided
            if emotional_state:
                response = self._add_emotional_context(
                    response,
                    emotional_state
                )
                
            # Record response
            self._record_response(
                response_type,
                response,
                context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
            
    def _format_context(
        self,
        context: Dict,
        formatting: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Format context values"""
        if not formatting:
            return context
            
        formatted = context.copy()
        for key, format_type in formatting.items():
            if key in formatted:
                if format_type == "json":
                    formatted[key] = json.dumps(
                        formatted[key],
                        indent=2
                    )
                elif format_type == "number":
                    formatted[key] = f"{formatted[key]:,.2f}"
                    
        return formatted
        
    def _add_emotional_context(
        self,
        response: str,
        emotional_state: Dict
    ) -> str:
        """Add emotional context to response"""
        emotion = emotional_state.get("emotion", "neutral")
        intensity = emotional_state.get("intensity", 0.5)
        
        # Emotion-based modifiers
        modifiers = {
            "optimistic": ["Excitingly,", "Positively,", "Encouragingly,"],
            "cautious": ["Carefully,", "Mindfully,", "Considerately,"],
            "confident": ["Confidently,", "Assuredly,", "Certainly,"],
            "concerned": ["Notably,", "Importantly,", "Significantly,"]
        }
        
        # Add modifier based on emotion and intensity
        if intensity > 0.7 and emotion in modifiers:
            modifier = random.choice(modifiers[emotion])
            response = f"{modifier} {response}"
            
        return response
        
    def _record_response(
        self,
        response_type: ResponseType,
        response: str,
        context: Dict
    ):
        """Record generated response"""
        self.response_history.append({
            "type": response_type.value,
            "response": response,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_response_history(
        self,
        response_type: Optional[ResponseType] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get response history with optional filtering"""
        history = self.response_history
        
        if response_type:
            history = [
                r for r in history
                if r["type"] == response_type.value
            ]
            
        if limit:
            history = history[-limit:]
            
        return history
        
    def get_formatted_response(
        self,
        response_type: ResponseType,
        context: Dict,
        format_type: str = "text"
    ) -> Union[str, Dict]:
        """Get formatted response"""
        response = self.generate_response(
            response_type,
            context
        )
        
        if format_type == "json":
            return {
                "type": response_type.value,
                "message": response,
                "timestamp": datetime.now().isoformat()
            }
            
        return response

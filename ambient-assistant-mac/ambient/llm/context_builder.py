from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Builds context for LLM prompts from various sources."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def build_context(self, screen_content: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """
        Build context string from screen content and conversation history.
        
        Args:
            screen_content: Current screen content
            conversation_history: List of previous messages
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add screen content
        if screen_content:
            context_parts.append("Current screen content:")
            context_parts.append(screen_content)
            
        # Add conversation history
        if conversation_history:
            context_parts.append("\nPrevious conversation:")
            for message in conversation_history[-5:]:  # Last 5 messages
                role = message.get("role", "unknown")
                content = message.get("content", "")
                context_parts.append(f"{role}: {content}")
                
        return "\n".join(context_parts) 
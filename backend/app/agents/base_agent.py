"""
Base agent class for all role agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all PPT Master agents
    Follows the original workflow without modification
    """
    
    def __init__(self, llm_client, session_manager, script_executor):
        self.llm = llm_client
        self.session_manager = session_manager
        self.script_executor = script_executor
        self.role_name = self.__class__.__name__
    
    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Get the system prompt for this agent
        Should load from skills/ppt-master/references/
        """
        pass
    
    @abstractmethod
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message and return response
        
        Returns:
            {
                "content": str,  # AI response
                "actions": List[Dict],  # Actions taken (script calls, etc.)
                "context_updates": Dict,  # Updates to session context
                "role_switch": Optional[str],  # Next role if switching
                "stage_switch": Optional[str]  # Next stage if switching
            }
        """
        pass
    
    def build_conversation_context(
        self,
        session_id: str,
        max_messages: int = 20
    ) -> str:
        """Build conversation context from history"""
        messages = self.session_manager.get_conversation_history(
            session_id,
            limit=max_messages
        )
        
        context_parts = []
        for msg in messages:
            # Handle both dict and object formats
            role = msg.get("role") if isinstance(msg, dict) else msg.role
            content = msg.get("content") if isinstance(msg, dict) else msg.content
            role_label = role.upper()
            context_parts.append(f"{role_label}: {content}")
        
        return "\n\n".join(context_parts)
    
    def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        conversation_context: Optional[str] = None
    ) -> str:
        """
        Call LLM with proper prompt structure
        
        Args:
            system_prompt: System instructions for the agent
            user_message: Current user message
            conversation_context: Previous conversation history
        
        Returns:
            LLM response text
        """
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if conversation_context:
            messages.append({
                "role": "system",
                "content": f"Previous conversation:\n{conversation_context}"
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent action"""
        logger.info(f"[{self.role_name}] {action}: {details}")

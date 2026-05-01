"""
LLM client initialization and management
"""
from typing import Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from .config import settings

logger = logging.getLogger(__name__)


def create_llm_client():
    """
    Create LLM client based on configuration
    
    Returns:
        LangChain chat model instance
    """
    provider = settings.LLM_PROVIDER.lower()
    
    try:
        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None,
                temperature=0.7
            )
        
        elif provider == "openai_compatible":
            # 讯飞星火等 OpenAI 兼容 API
            if not settings.OPENAI_COMPATIBLE_API_KEY:
                raise ValueError("OPENAI_COMPATIBLE_API_KEY not configured")
            
            if not settings.OPENAI_COMPATIBLE_BASE_URL:
                raise ValueError("OPENAI_COMPATIBLE_BASE_URL not configured")
            
            return ChatOpenAI(
                api_key=settings.OPENAI_COMPATIBLE_API_KEY,
                model=settings.OPENAI_COMPATIBLE_MODEL or "default",
                base_url=settings.OPENAI_COMPATIBLE_BASE_URL,
                temperature=0.7
            )
        
        elif provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            
            return ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL,
                temperature=0.7
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    except Exception as e:
        logger.error(f"Failed to create LLM client: {e}")
        raise


# Global LLM client instance
_llm_client: Optional[object] = None


def get_llm_client():
    """Get or create global LLM client instance"""
    global _llm_client
    
    if _llm_client is None:
        _llm_client = create_llm_client()
        logger.info(f"LLM client initialized: {settings.LLM_PROVIDER}")
    
    return _llm_client


def reset_llm_client():
    """Reset LLM client (useful for testing or config changes)"""
    global _llm_client
    _llm_client = None

"""
LLM client initialization and management
"""
from typing import Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from .config import settings

logger = logging.getLogger(__name__)


class MockLLMClient:
    """Mock LLM client for when no API key is configured"""
    
    def invoke(self, messages):
        """Mock invoke method"""
        logger.warning("Using mock LLM client - no API key configured")
        
        class MockResponse:
            content = "抱歉，LLM 服务未配置。请在 .env 文件中配置 API Key。\n\n请检查以下配置：\n- LLM_PROVIDER\n- OPENAI_COMPATIBLE_API_KEY\n- OPENAI_COMPATIBLE_BASE_URL\n- OPENAI_COMPATIBLE_MODEL"
        
        return MockResponse()


def create_llm_client():
    """
    Create LLM client based on configuration
    
    Returns:
        LangChain chat model instance or MockLLMClient if configuration is invalid
    """
    provider = settings.LLM_PROVIDER.lower()
    
    try:
        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not configured, using mock client")
                return MockLLMClient()
            
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None,
                temperature=0.7
            )
        
        elif provider == "openai_compatible":
            # 讯飞星火等 OpenAI 兼容 API
            if not settings.OPENAI_COMPATIBLE_API_KEY:
                logger.warning("OPENAI_COMPATIBLE_API_KEY not configured, using mock client")
                return MockLLMClient()
            
            if not settings.OPENAI_COMPATIBLE_BASE_URL:
                logger.warning("OPENAI_COMPATIBLE_BASE_URL not configured, using mock client")
                return MockLLMClient()
            
            return ChatOpenAI(
                api_key=settings.OPENAI_COMPATIBLE_API_KEY,
                model=settings.OPENAI_COMPATIBLE_MODEL or "default",
                base_url=settings.OPENAI_COMPATIBLE_BASE_URL,
                temperature=0.7
            )
        
        elif provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("ANTHROPIC_API_KEY not configured, using mock client")
                return MockLLMClient()
            
            return ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL,
                temperature=0.7
            )
        
        else:
            logger.warning(f"Unsupported LLM provider: {provider}, using mock client")
            return MockLLMClient()
    
    except Exception as e:
        logger.error(f"Failed to create LLM client: {e}, using mock client")
        return MockLLMClient()


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

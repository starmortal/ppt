"""
Startup validation and initialization
"""
import logging
from .config import settings

logger = logging.getLogger(__name__)


def validate_llm_config():
    """
    Validate LLM configuration
    Returns True if valid, False otherwise (with warnings)
    """
    if settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-your-openai-key":
            logger.warning("OpenAI API key not configured. LLM features will be disabled.")
            return False
    elif settings.LLM_PROVIDER == "openai_compatible":
        if not settings.OPENAI_COMPATIBLE_API_KEY:
            logger.warning("OpenAI Compatible API key not configured. LLM features will be disabled.")
            return False
        if not settings.OPENAI_COMPATIBLE_BASE_URL:
            logger.warning("OpenAI Compatible Base URL not configured. LLM features will be disabled.")
            return False
        if not settings.OPENAI_COMPATIBLE_MODEL:
            logger.warning("OpenAI Compatible Model not configured. LLM features will be disabled.")
            return False
    elif settings.LLM_PROVIDER == "anthropic":
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "sk-ant-your-anthropic-key":
            logger.warning("Anthropic API key not configured. LLM features will be disabled.")
            return False
    elif settings.LLM_PROVIDER == "ollama":
        logger.info(f"Using Ollama at {settings.OLLAMA_BASE_URL}")
        return True
    else:
        logger.warning(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
        return False
    
    return True


def validate_image_gen_config():
    """
    Validate image generation configuration
    Returns True if valid, False otherwise (with warnings)
    """
    if settings.IMAGE_GEN_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-your-openai-key":
            logger.warning("OpenAI API key not configured. Image generation will be disabled.")
            return False
    elif settings.IMAGE_GEN_PROVIDER == "stability":
        if not settings.STABILITY_API_KEY or settings.STABILITY_API_KEY == "sk-your-stability-key":
            logger.warning("Stability API key not configured. Image generation will be disabled.")
            return False
    elif settings.IMAGE_GEN_PROVIDER == "local":
        logger.info("Using local image generation")
        return True
    else:
        logger.warning(f"Unknown image generation provider: {settings.IMAGE_GEN_PROVIDER}")
        return False
    
    return True


def startup_checks():
    """
    Run all startup checks
    Returns dict with check results
    """
    results = {
        "llm_available": validate_llm_config(),
        "image_gen_available": validate_image_gen_config(),
    }
    
    # Log summary
    if results["llm_available"]:
        logger.info(f"✓ LLM provider configured: {settings.LLM_PROVIDER}")
    else:
        logger.warning("✗ LLM features disabled (no API key)")
    
    if results["image_gen_available"]:
        logger.info(f"✓ Image generation configured: {settings.IMAGE_GEN_PROVIDER}")
    else:
        logger.warning("✗ Image generation disabled (no API key)")
    
    return results

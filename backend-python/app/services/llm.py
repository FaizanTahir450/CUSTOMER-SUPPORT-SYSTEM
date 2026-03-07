# llm.py
from langchain_openai import ChatOpenAI
from app.config import Config
import logging

logger = logging.getLogger(__name__)

_llm_instance = None
_extraction_llm_instance = None
_classification_llm_instance = None

def get_llm():
    """Get the main LLM for response generation (Gemini 2.0 Flash or configured model)."""
    global _llm_instance
    
    if _llm_instance is None:
        _llm_instance = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=0,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        logger.info(f"Initialized main LLM with model: {Config.MODEL_NAME}")
    
    return _llm_instance

def get_extraction_llm():
    """Get a cheaper LLM for fact extraction (GPT-4o Mini or configured extraction model)."""
    global _extraction_llm_instance

    if _extraction_llm_instance is None:
        _extraction_llm_instance = ChatOpenAI(
            model=Config.EXTRACTION_MODEL,
            temperature=0,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        logger.info(f"Initialized extraction LLM with model: {Config.EXTRACTION_MODEL}")
    return _extraction_llm_instance

def get_classification_llm():
    """Get a cheaper LLM for classification tasks (GPT-4o Mini or configured classification model)."""
    global _classification_llm_instance

    if _classification_llm_instance is None:
        _classification_llm_instance = ChatOpenAI(
            model=Config.CLASSIFICATION_MODEL,
            temperature=0,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        logger.info(f"Initialized classification LLM with model: {Config.CLASSIFICATION_MODEL}")
    return _classification_llm_instance

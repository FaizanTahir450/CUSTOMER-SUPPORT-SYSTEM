# llm.py
from langchain_openai import ChatOpenAI
from config.config import Config

_llm_instance = None
_extraction_llm_instance = None

def get_llm():
    global _llm_instance
    
    if _llm_instance is None:
        _llm_instance = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=0,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
    
    return _llm_instance

def get_extraction_llm():
    global _extraction_llm_instance

    if _extraction_llm_instance is None:
        _extraction_llm_instance = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=0,
            openai_api_key=Config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1"
        )
    return _extraction_llm_instance
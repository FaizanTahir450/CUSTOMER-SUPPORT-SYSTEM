# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "admin")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "customer_support")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY","")
    MODEL_NAME = os.getenv("MODEL_NAME", "google/gemini-2.5-flash")
    
    # PDF Path
    PDF_PATH = os.getenv("PDF_PATH", "docs/Lama1.pdf")
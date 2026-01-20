import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'test_db1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Gemini API Configuration
    GEMINI_API_KEY = 'AIzaSyDVj136W58hHxh_dSuKSUtEXmLlEZ0_PbQ'
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
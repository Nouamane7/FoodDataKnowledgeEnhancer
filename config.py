import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'food_db')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
    POSTGRES_TABLE = os.getenv('POSTGRES_TABLE', 'ingredient') 
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'food_database')
    MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'products')
    
    # Ollama Configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    LLM1_MODEL = os.getenv('LLM1_MODEL', 'llama3.1:8b')  # Primary transformer model
    LLM2_MODEL = os.getenv('LLM2_MODEL', 'mistral:7b')   # Validator/corrector model
    
    # Processing Configuration
    MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '3'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))

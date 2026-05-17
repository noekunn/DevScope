"""
Centralized Configuration — Loads environment variables and provides defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(_env_path)


class Config:
    """Application configuration from environment variables."""
    
    # Neo4j
    NEO4J_URI = os.getenv('NEO4J_URI', '')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')
    
    # watsonx.ai
    WATSONX_API_KEY = os.getenv('WATSONX_API_KEY', '')
    WATSONX_URL = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID', '')
    WATSONX_MODEL_ID = os.getenv('WATSONX_MODEL_ID', 'ibm/granite-3-8b-instruct')
    
    # Analysis defaults
    MAX_FILE_SIZE_KB = int(os.getenv('MAX_FILE_SIZE_KB', '500'))
    MAX_FILES = int(os.getenv('MAX_FILES', '1000'))
    COMPLEXITY_HOTSPOT_THRESHOLD = int(os.getenv('COMPLEXITY_HOTSPOT_THRESHOLD', '10'))
    
    # Dashboard
    DASHBOARD_THEME = os.getenv('DASHBOARD_THEME', 'dark')
    
    @classmethod
    def has_neo4j(cls) -> bool:
        return bool(cls.NEO4J_URI and cls.NEO4J_PASSWORD)
    
    @classmethod
    def has_watsonx(cls) -> bool:
        return bool(cls.WATSONX_API_KEY and cls.WATSONX_PROJECT_ID)
    
    @classmethod
    def as_dict(cls) -> dict:
        return {
            'neo4j_configured': cls.has_neo4j(),
            'watsonx_configured': cls.has_watsonx(),
            'max_files': cls.MAX_FILES,
            'hotspot_threshold': cls.COMPLEXITY_HOTSPOT_THRESHOLD,
        }

# Made with Bob

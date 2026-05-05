import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./investments.db")
DEBUG = os.getenv("DEBUG", "False") == "True"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Chemins
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

print(f"🔧 Configuration chargée | DEBUG: {DEBUG} | DB: {DATABASE_URL}")

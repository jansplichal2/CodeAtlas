# Config loader
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

PROJECT_ROOT = Path(".").resolve()
CHUNK_DIR = PROJECT_ROOT / ".chunks"
DB_PATH = PROJECT_ROOT / ".codeatlas.sqlite"
MAX_TOKENS = 8192

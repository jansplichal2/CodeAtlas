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

EMBED_MODEL = "text-embedding-3-small"
QDRANT_COLLECTION = "codeatlas_chunks"
QDRANT_DIM = 1536  # For text-embedding-3-small

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

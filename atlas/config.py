# Config loader
import os
from pathlib import Path

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROJECT_ROOT = Path(".").resolve()
CHUNK_DIR = PROJECT_ROOT / ".chunks"
LINES_DIR = PROJECT_ROOT / ".lines"
DB_PATH = PROJECT_ROOT / ".codeatlas.sqlite"
MAX_TOKENS = 8192
MAX_CHUNK_LINES = 80
CONTEXT_LINES = 10

EMBED_PROVIDER = "openai"
EMBED_MODEL = "text-embedding-3-small"

QDRANT_COLLECTION = "codeatlas_chunks"
QDRANT_DIM = 1536  # For text-embedding-3-small
QDRANT_PATH = PROJECT_ROOT / ".codeatlas.qdrant"

JOERN_SERVER_URL = "http://localhost:8080/query-sync"

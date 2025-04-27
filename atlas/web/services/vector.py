import logging

from atlas.config import EMBED_PROVIDER, EMBED_MODEL
from atlas.embedding.embedding_dispatcher import get_embedder
from atlas.qdrant.chunks_loader import execute_qdrant_query

logger = logging.getLogger(__name__)

def handle(query: str):
    logger.info(f"Running semantic query '{query}'")
    embedder = get_embedder(EMBED_PROVIDER, EMBED_MODEL)
    embedding = embedder.retrieve_embedding_for_query(query)

    rows = execute_qdrant_query(embedding, 10)
    return rows

import json
import logging

from atlas.config import CHUNK_DIR, EMBED_MODEL, EMBED_PROVIDER
from atlas.embedding.base_embedder import Embedding
from atlas.embedding.embedding_dispatcher import get_embedder

logger = logging.getLogger(__name__)


def save_embeddings(chunks_with_embedding):
    for chunk in chunks_with_embedding:
        chunk_file = CHUNK_DIR / f"chunk_{chunk.chunk_id}.json"
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if len(chunk.errors) > 0:
                if 'errors' not in data:
                    data['errors'] = []
                data['errors'].append({'source': 'embedding', 'error': json.dumps(chunk.errors)})
                with open(chunk_file, "r+", encoding="utf-8") as w:
                    json.dump(data, w, indent=2)
            else:
                with open(chunk_file, "r+", encoding="utf-8") as w:
                    data['embedding'] = chunk.embedding
                    json.dump(data, w, indent=2)


def embed_chunks():
    chunks = []
    batch_no = 1
    embedder = get_embedder(EMBED_PROVIDER, EMBED_MODEL)
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunk_id = data['chunk_id']
            source = data.get('source', '')
            chunks.append(Embedding(chunk_id, source))
        if len(chunks) >= 30:
            logger.info(f"Running batch num {batch_no}")
            chunks_with_embedding = embedder.retrieve_embedding(chunks)
            save_embeddings(chunks_with_embedding)
            chunks = []
            batch_no += 1

    if len(chunks) > 0:
        logger.info(f"Running batch num {batch_no}. This batch is the last.")
        chunks_with_embedding = embedder.retrieve_embedding(chunks)
        save_embeddings(chunks_with_embedding)

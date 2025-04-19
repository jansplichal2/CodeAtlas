import json

from atlas.config import CHUNK_DIR, EMBED_MODEL, EMBED_PROVIDER
from atlas.embedding.base_embedder import Embedding
from atlas.embedding.embedding_dispatcher import get_embedder


def save_embeddings(chunks_with_embedding):
    for chunk in chunks_with_embedding:
        chunk_file = CHUNK_DIR / f"chunk_{chunk.chunk_id}.json"
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if len(chunk.errors) > 0:
                if 'errors' not in data:
                    data['errors'] = []
                data['errors'].append({'source': 'embedding', 'error': '\n'.join(chunk.errors)})
                with open(chunk_file, "r+", encoding="utf-8") as w:
                    json.dump(data, w, indent=2)
            else:
                with open(chunk_file, "r+", encoding="utf-8") as w:
                    data['embedding'] = chunk.embedding
                    json.dump(data, w, indent=2)


def embed_chunks():
    chunks = []
    embedder = get_embedder(EMBED_PROVIDER, EMBED_MODEL)
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunk_id = data['chunk_id']
            source = data.get('source', '')
            chunks.append(Embedding(chunk_id, source))
        if len(chunks) >= 100:
            chunks_with_embedding = embedder.retrieve_embedding(chunks)
            save_embeddings(chunks_with_embedding)
            chunks = []

    if len(chunks) > 0:
        chunks_with_embedding = embedder.retrieve_embedding(chunks)
        save_embeddings(chunks_with_embedding)


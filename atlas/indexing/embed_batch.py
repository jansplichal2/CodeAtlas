import openai
import time
import os
from typing import List, Tuple
from atlas.memory.storage import connect_db, update_chunk_status
from atlas.indexing.qdrant_index import index_embeddings
from atlas.config import MAX_TOKENS, CHUNK_DIR, EMBED_MODEL


def get_ready_chunks(limit: int = 100) -> List[Tuple[int, str]]:
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, source FROM chunks WHERE status = 'ready' AND tokens <= ? LIMIT ?",
            (MAX_TOKENS, limit)
        )
        return cur.fetchall()


def embed_chunk_texts(chunk_texts: List[str]) -> List[List[float]]:
    max_retries = 5
    delay = 1

    for attempt in range(max_retries):
        try:
            response = openai.embeddings.create(
                input=chunk_texts,
                model=EMBED_MODEL
            )
            return [res.embedding for res in response.data]
        except openai.OpenAIError as e:
            print(f"⚠️ Embedding failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise


def cleanup_chunks(ids: List[int]):
    for chunk_id in ids:
        for file in CHUNK_DIR.glob(f"*{chunk_id}*.json"):
            try:
                os.remove(file)
                print(f"🧹 Removed {file.name}")
            except Exception as e:
                print(f"⚠️ Failed to remove {file.name}: {e}")


def embed_ready_chunks(batch_size: int = 100):
    ready = get_ready_chunks(limit=batch_size)
    if not ready:
        print("✅ No ready chunks to embed.")
        return

    ids, texts = zip(*ready)
    embeddings = embed_chunk_texts(list(texts))
    print(f"🔗 Embedded {len(embeddings)} chunks.")

    pairs = list(zip(ids, embeddings))
    index_embeddings(pairs)
    update_chunk_status(ids, "embedded")
    cleanup_chunks(ids)
    print(f"✅ Updated and cleaned up {len(ids)} chunks.")

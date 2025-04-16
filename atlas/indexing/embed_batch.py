import openai
import time
import os
from typing import List, Tuple
from atlas.memory.storage import connect_db, update_chunk_status
from atlas.indexing.qdrant_index import index_embeddings
from atlas.config import MAX_TOKENS, CHUNK_DIR, EMBED_MODEL


def get_ready_chunks(limit: int = 100) -> List[Tuple[str, str]]:
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT chunk_id, source FROM chunks WHERE status = 'ready' AND tokens <= ? LIMIT ?",
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


def cleanup_chunks(chunk_ids: List[str]):
    for chunk_id in chunk_ids:
        file = CHUNK_DIR / f"chunk_{chunk_id}.json"
        if file.exists():
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

    chunk_ids, texts = zip(*ready)
    embeddings = embed_chunk_texts(list(texts))
    print(f"🔗 Embedded {len(embeddings)} chunks.")

    pairs = list(zip(chunk_ids, embeddings))

    try:
        index_embeddings(pairs)
        update_chunk_status(chunk_ids, "embedded")
        cleanup_chunks(chunk_ids)
        print(f"✅ Updated and cleaned up {len(chunk_ids)} chunks.")
    except Exception as e:
        print(f"❌ Failed during indexing: {e}")
        print("⚠️ Cleanup skipped to avoid deleting unsaved chunks.")

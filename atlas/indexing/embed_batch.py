import openai
import time
from typing import List, Tuple
from atlas.memory.storage import connect_db
from atlas.config import MAX_TOKENS

EMBED_MODEL = "text-embedding-3-small"


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


def embed_ready_chunks(batch_size: int = 100):
    ready = get_ready_chunks(limit=batch_size)
    if not ready:
        print("✅ No ready chunks to embed.")
        return

    ids, texts = zip(*ready)
    embeddings = embed_chunk_texts(list(texts))
    print(f"🔗 Embedded {len(embeddings)} chunks.")
    return list(zip(ids, embeddings))

import os
from typing import List

from atlas.config import MAX_TOKENS, CHUNK_DIR, EMBED_MODEL







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
        cleanup_chunks(chunk_ids)
        print(f"✅ Updated and cleaned up {len(chunk_ids)} chunks.")
    except Exception as e:
        print(f"❌ Failed during indexing: {e}")
        print("⚠️ Cleanup skipped to avoid deleting unsaved chunks.")

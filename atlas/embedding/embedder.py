import json

from atlas.config import CHUNK_DIR


def embed_ready_chunks(batch_size: int = 100):
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    # ready = get_ready_chunks(limit=batch_size)
    # if not ready:
    #     print("✅ No ready chunks to embed.")
    #     return
    #
    # chunk_ids, texts = zip(*ready)
    # embeddings = embed_chunk_texts(list(texts))
    # print(f"🔗 Embedded {len(embeddings)} chunks.")
    #
    # pairs = list(zip(chunk_ids, embeddings))
    #
    # try:
    #     index_embeddings(pairs)
    #     cleanup_chunks(chunk_ids)
    #     print(f"✅ Updated and cleaned up {len(chunk_ids)} chunks.")
    # except Exception as e:
    #     print(f"❌ Failed during indexing: {e}")
    #     print("⚠️ Cleanup skipped to avoid deleting unsaved chunks.")

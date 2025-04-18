import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from atlas.config import QDRANT_COLLECTION, QDRANT_DIM, QDRANT_HOST, QDRANT_PORT,CHUNK_DIR
import numpy as np

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def ensure_qdrant_collection():
    existing = client.get_collections().collections
    if QDRANT_COLLECTION not in [col.name for col in existing]:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=QDRANT_DIM, distance=Distance.COSINE)
        )


def load_chunks_to_qdrant():
    ensure_qdrant_collection()
    records = []
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        records.append(PointStruct(
            id=data['chunk_id'],
            vector=np.array(data['embedding'], dtype=np.float32).tolist(),
            payload={
                "type": data['type'],
                "name": data['name'],
                "chunk_no": data['chunk_no'],
                "start_line": data['start_line'],
                "end_line": data['end_line'],
                "file_path": data['file_path'],
                "source": data['source'],
            }
        ))
    client.upsert(collection_name=QDRANT_COLLECTION, points=records)
    print(f"📌 Indexed {len(records)} chunks into Qdrant.")


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

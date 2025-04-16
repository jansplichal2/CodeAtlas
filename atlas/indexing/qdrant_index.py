from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from atlas.memory.storage import connect_db
from atlas.config import QDRANT_COLLECTION, QDRANT_DIM, QDRANT_HOST, QDRANT_PORT
from typing import List, Tuple
import numpy as np

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def ensure_qdrant_collection():
    existing = client.get_collections().collections
    if QDRANT_COLLECTION not in [col.name for col in existing]:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=QDRANT_DIM, distance=Distance.COSINE)
        )


def get_chunk_metadata(chunk_id: str) -> dict:
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT chunk_type, name, file_path, start_line, end_line FROM chunks WHERE chunk_id = ?",
            (chunk_id,)
        )
        row = cur.fetchone()
        if row:
            return {
                "chunk_type": row[0],
                "name": row[1],
                "file_path": row[2],
                "start_line": row[3],
                "end_line": row[4]
            }
        return {}


def index_embeddings(pairs: List[Tuple[str, List[float]]]):
    ensure_qdrant_collection()
    points = []
    for chunk_id, embedding in pairs:
        payload = get_chunk_metadata(chunk_id)
        points.append(PointStruct(
            id=chunk_id,
            vector=np.array(embedding, dtype=np.float32).tolist(),
            payload=payload
        ))
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    print(f"📌 Indexed {len(points)} chunks into Qdrant.")

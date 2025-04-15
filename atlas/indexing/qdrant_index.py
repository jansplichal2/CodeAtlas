from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from atlas.config import PROJECT_ROOT, QDRANT_COLLECTION, QDRANT_DIM
from typing import List, Tuple
import numpy as np

client = QdrantClient(path=PROJECT_ROOT / ".qdrant")


def ensure_qdrant_collection():
    existing = client.get_collections().collections
    if QDRANT_COLLECTION not in [col.name for col in existing]:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=QDRANT_DIM, distance=Distance.COSINE)
        )


def index_embeddings(pairs: List[Tuple[int, List[float]]]):
    ensure_qdrant_collection()
    points = [
        PointStruct(
            id=chunk_id,
            vector=np.array(embedding, dtype=np.float32).tolist(),
            payload={}
        )
        for chunk_id, embedding in pairs
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    print(f"📌 Indexed {len(points)} chunks into Qdrant.")

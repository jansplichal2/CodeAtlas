import json
import logging
import numpy as np

from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from atlas.config import QDRANT_COLLECTION, QDRANT_DIM, QDRANT_PATH, CHUNK_DIR

client = QdrantClient(path=QDRANT_PATH)
logger = logging.getLogger(__name__)


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
        if len(data.get('errors', [])) == 0:
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
    logger.info(f"Indexed {len(records)} chunks into Qdrant.")


def execute_qdrant_query(embedding: List[float], limit: int):
    result = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=embedding,
        limit=limit
    )
    return result.points


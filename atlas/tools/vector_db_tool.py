from atlas.tools.base import BaseTool
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, PointStruct, SearchRequest
from atlas.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, EMBED_MODEL
import numpy as np
import openai

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


class VectorDBTool(BaseTool):
    name = "vector_db_search"

    def run(self, query: str, top_k: int = 5):
        embedding = openai.embeddings.create(input=query, model=EMBED_MODEL).data[0].embedding
        results = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=np.array(embedding, dtype=np.float32).tolist(),
            limit=top_k
        )
        return [hit.payload for hit in results]

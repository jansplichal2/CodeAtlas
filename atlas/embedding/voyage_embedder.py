import logging
import time
import voyageai

from typing import List
from voyageai.error import VoyageError

from atlas.config import EMBED_MODEL
from atlas.embedding.base_embedder import BaseEmbedder, Embedding

logger = logging.getLogger(__name__)


class VoyageEmbedder(BaseEmbedder):
    def __init__(self, model_type):
        super().__init__(model_type)
        self.client = voyageai.Client(max_retries=3)

    def retrieve_embedding(self, chunks: List[Embedding]) -> List[Embedding]:
        texts = [embed.chunk_text for embed in chunks]

        try:
            time.sleep(0.05)  # for rate limiting, should be improved
            response = self.client.embed(
                texts=texts,
                model=self.model_type,
                input_type="document"
            )
            for chunk, embed in zip(chunks, response.embeddings):
                chunk.embedding = embed
            return chunks

        except VoyageError as e:
            for chunk in chunks:
                if 'errors' not in chunk:
                    chunk.errors = []
                chunk.errors.append({'source': 'embedding', 'error': str(e)})
            return chunks


    def retrieve_embedding_for_query(self, query: str):
        try:
            result = self.client.embed(
                texts=[query],
                model=EMBED_MODEL,
                input_type="query"
            )
            return result.embeddings[0]
        except VoyageError as e:
            logger.error(f"Query embedding failed: {e}")
            return None

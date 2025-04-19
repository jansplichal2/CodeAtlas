from typing import List


class Embedding:
    def __init__(self, chunk_id: str, chunk_text: str):
        self.chunk_id = chunk_id
        self.chunk_text = chunk_text
        self.embedding = []
        self.errors = []


class BaseEmbedder:
    def __init__(self, model_type):
        self.model_type = model_type

    def retrieve_embedding(self, chunks: List[Embedding]) -> List[Embedding]:
        raise NotImplementedError

    def retrieve_embedding_for_query(self, query: str):
        raise NotImplementedError

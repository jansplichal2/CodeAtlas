import openai
import time
from typing import List

from atlas.embedding.base_embedder import BaseEmbedder, Embedding


class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model_type):
        super().__init__(model_type)

    def retrieve_embedding(self, chunks: List[Embedding]) -> List[Embedding]:
        max_retries = 5
        delay = 1

        for attempt in range(max_retries):
            try:
                response = openai.embeddings.create(
                    input=[embed.chunk_text for embed in chunks],
                    model=self.model_type
                )
                embeddings = [res.embedding for res in response.data]
                for chunk, embed in zip(chunks, embeddings):
                    chunk.embedding = embed

                return chunks
            except openai.OpenAIError as e:
                print(f"⚠️ Embedding failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    for chunk in chunks:
                        if 'errors' not in chunk:
                            chunk['errors'] = []
                        chunk['errors'].append({'source': 'embedding', 'error': str(e)})
                    return chunks

import openai
import logging

from pydantic import Field
from qdrant_client import QdrantClient
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.agents.base_agent import BaseIOSchema

logger = logging.getLogger(__name__)


class VectorDBToolConfig(BaseToolConfig):
    """
    Configuration for VectorDBAtomicTool.
    """
    qdrant_client: QdrantClient = Field(..., description="Instance of QdrantClient.")
    collection_name: str = Field(..., description="Name of the Qdrant collection.")
    embedding_model: str = Field(..., description="Name of the OpenAI embedding model.")

    class Config:
        arbitrary_types_allowed = True


class VectorDBToolInputSchema(BaseIOSchema):
    """
    Input schema for vector database search.
    """
    query: str = Field(..., description="Text query to search in the vector database.")
    top_k: int = Field(10, description="Number of top results to return.")


class VectorDBToolOutputSchema(BaseIOSchema):
    """
    Output schema for vector database search results.
    """
    results: list = Field(..., description="List of payload dictionaries returned by the vector search.")
    error: str = Field("", description="Error message if query failed, empty otherwise.")


class VectorDBTool(BaseTool):
    """
    Search Qdrant vector database for relevant code chunks.
    """
    input_schema = VectorDBToolInputSchema
    output_schema = VectorDBToolOutputSchema

    def __init__(self, config: VectorDBToolConfig):
        super().__init__(config)
        self.embedding_model = config.embedding_model
        self.qdrant_client = config.qdrant_client
        self.collection_name = config.collection_name

    def run(self, params: VectorDBToolInputSchema) -> VectorDBToolOutputSchema:
        try:
            logger.info(f"Execution of Vector query was requested: {params.query}")
            embedding = openai.embeddings.create(
                input=params.query,
                model=self.embedding_model
            ).data[0].embedding
        except Exception as e:
            logger.error(f"Failed to get embedding from OpenAI: {e}", exc_info=True)
            return VectorDBToolOutputSchema(results=[], error=f"Retrieving OpenAI embedding failed: {e}")

        try:
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=params.top_k
            )
            hits = [hit.payload for hit in results.points]
            return VectorDBToolOutputSchema(results=hits, error='')
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}", exc_info=True)
            return VectorDBToolOutputSchema(results=[], error=f"Vector DB query failed: {e}")


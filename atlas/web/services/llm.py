import logging

from qdrant_client import qdrant_client

from atlas.agents.agent_workflow import run
from atlas.sqlite.utils import get_db_connection

logger = logging.getLogger(__name__)

def handle(query: str, llm_provider: str, llm_model: str):
    logger.info(f"Calling LLM (provider={llm_provider}, model={llm_model}) with semantic query '{query}'")
    with get_db_connection() as sqlite:
        result = run(query, sqlite, qdrant_client)
        return result
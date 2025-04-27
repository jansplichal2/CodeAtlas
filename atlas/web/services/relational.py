import logging
from atlas.sqlite.utils import execute_sql_query

logger = logging.getLogger(__name__)

def handle(query: str):
    logger.info(f"Running sqlite query '{query}'")
    return execute_sql_query(query)
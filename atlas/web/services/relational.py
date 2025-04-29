import logging
from atlas.sqlite.utils import execute_sql_query
from atlas.web.services.utils import ServiceException

logger = logging.getLogger(__name__)

def handle(query: str):
    logger.info(f"Running sqlite query '{query}'")
    try:
        return execute_sql_query(query)
    except Exception as e:
        logger.error("Query to relation db failed", exc_info=e)
        raise ServiceException(str(e))
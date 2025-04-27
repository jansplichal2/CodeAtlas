import logging
from atlas.joern.client import run_command

logger = logging.getLogger(__name__)

def handle(query: str):
    logger.info(f"Running joern query '{query}'")
    return run_command(query)
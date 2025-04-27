import requests
import logging
import re

from atlas.config import JOERN_SERVER_URL

logger = logging.getLogger(__name__)
ansi_escape_pattern = re.compile(r'\x1b\[[0-9;]*m')

def run_command(query: str):
    payload = {
        "query": query
    }

    response = requests.post(JOERN_SERVER_URL, json=payload)
    response.raise_for_status()

    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error("Response content is not valid JSON:")
        logger.error(response.text)
        raise

    stdout_with_codes = response_data["stdout"]
    cleaned_output = ansi_escape_pattern.sub('', stdout_with_codes)

    return cleaned_output


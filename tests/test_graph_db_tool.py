import logging
from atlas.joern.client import run_command

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TEST_QUERIES = {
"List all methods": "cpg.method.name",
"Find eval calls": 'cpg.call.filter(_.code.matches(".*eval.*")).code',
"List all files": "cpg.file.name",
"List all classes": "cpg.typeDecl.name",
"Find calls to 'authorize'": 'cpg.call.filter(_.name.matches("authorize")).code',
}

def test_graph_db():
    logger.info("Running GraphDBTool test queries...")

    for description, query in TEST_QUERIES.items():
        logger.info(f"\n=== {description} ===")
        try:
            result = run_command(query)
            logger.info(f"Result:\n{result}")
        except Exception as e:
            logger.error(f"Query failed: {e}")


if __name__ == "__main__":
    test_graph_db()

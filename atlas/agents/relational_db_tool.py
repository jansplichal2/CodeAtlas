import sqlite3
import logging

from pydantic import Field
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.agents.base_agent import BaseIOSchema

logger = logging.getLogger(__name__)


class RelationalDBToolInputSchema(BaseIOSchema):
    """
    Input schema for relational database queries.
    """
    query: str = Field(..., description="SQL query to execute on the code metadata SQLite database.")


class RelationalDBToolOutputSchema(BaseIOSchema):
    """
    Output schema for relational database tool.
    """
    rows: list = Field(..., description="Rows returned by the SQL query.")
    error: str = Field("", description="Error message if query failed, empty otherwise.")


class RelationalDBToolConfig(BaseToolConfig):
    """
    Configuration for RelationalDBToolConfig.
    """
    conn: sqlite3.Connection = Field(..., description="Sqlite connection.")

    class Config:
        arbitrary_types_allowed = True


class RelationalDBTool(BaseTool):
    """
    Execute SQL query against the codebase metadata SQLite database.
    """
    input_schema = RelationalDBToolInputSchema
    output_schema = RelationalDBToolOutputSchema

    def __init__(self, config: RelationalDBToolConfig):
        super().__init__(config)
        self.conn = config.conn

    def run(self, params: RelationalDBToolInputSchema) -> RelationalDBToolOutputSchema:
        try:
            logger.info(f"Execution of SQlite query was requested: {params.query}")
            cursor = self.conn.cursor()
            cursor.execute(params.query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            hits = [dict(zip(columns, row)) for row in rows]
            return RelationalDBToolOutputSchema(rows=hits, error='')
        except Exception as e:
            logger.error(f"Sqlite search failed: {e}", exc_info=True)
            return RelationalDBToolOutputSchema(rows=[], error=f"Sqlite DB query failed: {e}")


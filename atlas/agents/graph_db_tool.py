import logging
from pydantic import Field
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.agents.base_agent import BaseIOSchema
from atlas.joern.client import run_command

logger = logging.getLogger(__name__)

class GraphDBToolInputSchema(BaseIOSchema):
    """
    Input schema for Graph DB queries (Joern).
    """
    query: str = Field(..., description="Joern query to execute against the code property graph (CPG).")


class GraphDBToolOutputSchema(BaseIOSchema):
    """
    Output schema for Graph DB tool.
    """
    result: str = Field(..., description="Raw result of the Joern query.")
    error: str = Field("", description="Error message if query failed, empty otherwise.")


class GraphDBToolConfig(BaseToolConfig):
    """
    Configuration for GraphDBTool (currently no configuration fields).
    """
    pass

class GraphDBTool(BaseTool):
    """
    Executes a single Joern query against the Graph DB (CPG).
    """
    input_schema = GraphDBToolInputSchema
    output_schema = GraphDBToolOutputSchema

    def __init__(self, config: GraphDBToolConfig):
        super().__init__(config)

    def run(self, params: GraphDBToolInputSchema) -> GraphDBToolOutputSchema:
        try:
            logger.info(f"Execution of Joern query was requested: {params.query}")
            result = run_command(params.query)
            return GraphDBToolOutputSchema(result=result, error='')
        except Exception as e:
            logger.error(f"Joern query failed: {e}", exc_info=True)
            return GraphDBToolOutputSchema(result='', error=f"Joern query failed: {e}")
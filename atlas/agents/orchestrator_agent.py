import logging

from typing import Union, Optional, Literal
from pydantic import Field

from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig

from atlas.agents.relational_db_tool import RelationalDBToolConfig, RelationalDBToolInputSchema
from atlas.agents.vector_db_tool import VectorDBToolConfig, VectorDBToolInputSchema

logger = logging.getLogger(__name__)


class ReasoningInputSchema(BaseIOSchema):
    """Input schema for the Orchestrator Agent. Contains original user query, context and iteration number."""
    original_query: str = Field(..., description="The user's original text query.")
    context: str = Field(..., description="Context retrieved from knowledge sources (e.g., initial vector search, "
                                          "previous tool outputs).")
    iteration: int = Field(1, description="Current iteration number.")


class AgentDecisionSchema(BaseIOSchema):
    """Combined output schema for the Orchestrator Agent. Contains the tool to use and its parameters."""
    thought: str = Field(
        ...,
        description="Your step-by-step reasoning based on the query and context to decide the next action."
    )
    action: Literal['final_answer', 'call_vector_db', 'call_relational_db'] = Field(
        ...,
        description="The action to take next."
    )

    tool_parameters: Optional[Union[RelationalDBToolInputSchema, VectorDBToolInputSchema]] = Field(
        None,
        description="Parameters if action is 'call_vector_db' or 'call_relational_db'"
    )
    final_answer: Optional[str] = Field(None, description="The final answer if action is 'final_answer'")


class OrchestratorAgentConfig(BaseAgentConfig):
    """Configuration for the Orchestrator Agent."""

    vector_db_config: VectorDBToolConfig
    relational_db_config: RelationalDBToolConfig




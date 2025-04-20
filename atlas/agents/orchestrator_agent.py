import openai
import instructor
import logging

from typing import Union, Optional, Literal
from pydantic import Field

from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig

from atlas.agents.relational_db_tool import RelationalDBToolConfig, RelationalDBToolInputSchema
from atlas.agents.vector_db_tool import VectorDBToolConfig, VectorDBToolInputSchema

logger = logging.getLogger(__name__)


class ReasoningInputSchema(BaseIOSchema):
    original_query: str = Field(..., description="The user's original text query.")
    context: str = Field(..., description="Context retrieved from knowledge sources (e.g., initial vector search, "
                                          "previous tool outputs).")
    iteration: int = Field(1, description="Current iteration number.")


class AgentDecisionSchema(BaseIOSchema):
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


SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT UNIQUE,
    chunk_type TEXT,
    name TEXT,
    chunk_no INTEGER,
    start_line INTEGER,
    end_line INTEGER,
    file_path TEXT,
    source TEXT,
    created_at TEXT
);
"""

orchestrator_agent = BaseAgent(
    BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI()),
        model="gpt-4o-mini",
        system_prompt_generator=SystemPromptGenerator(
            background=[
                "You will receive a query and context, and your goal is to answer the query."
            ],
            output_instructions=[
                "First reason and then choose an action.",
                "If you can answer, choose final_answer and provide the final_answer.",
                "If you need more info, choose call_vector_db or call_relational_db and provide the necessary "
                "tool_parameters.",
                "Use the provided context and potentially ask for specific tool calls to get missing information.",
                "When you use call_relational_db create a query valid for this schema " + SCHEMA
            ],
        ),
        input_schema=ReasoningInputSchema,
        output_schema=AgentDecisionSchema,
    )
)



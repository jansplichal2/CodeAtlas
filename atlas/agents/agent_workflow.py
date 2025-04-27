import datetime
import logging
import openai
import instructor

from typing import Union

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

from atlas.agents.orchestrator_agent import ReasoningInputSchema, AgentDecisionSchema
from atlas.agents.relational_db_tool import RelationalDBToolOutputSchema, RelationalDBTool, RelationalDBToolInputSchema, \
    RelationalDBToolConfig
from atlas.agents.vector_db_tool import VectorDBTool, VectorDBToolInputSchema, VectorDBToolOutputSchema, \
    VectorDBToolConfig
from atlas.config import QDRANT_COLLECTION, EMBED_MODEL

MAX_ITERATIONS = 5
logger = logging.getLogger(__name__)


def get_initial_context(query: str, vdb_tool: VectorDBTool) -> str:
    logger.info(f"Fetching initial context for: '{query}'")
    try:
        # Use the VectorDBTool directly for simplicity here, or a raw client call
        params = VectorDBToolInputSchema(query=query, top_k=5)  # Get top 5 snippets initially
        results: VectorDBToolOutputSchema = vdb_tool.run(params)
        # Format results into a string for the LLM
        context_str = "\n---\n".join([str(payload) for payload in results.results])
        return context_str if context_str else "No initial context found."
    except Exception as e:
        logger.info(f"Error fetching initial context: {e}", exc_info=True)
        return f"Error fetching initial context: {e}"


# --- Helper: Format Tool Output for LLM ---
def format_tool_output_for_llm(output: Union[VectorDBToolOutputSchema, RelationalDBToolOutputSchema]) -> str:
    if isinstance(output, RelationalDBToolOutputSchema):
        if output.error:
            return f"Relational DB Tool Execution Failed: {output.error}"
        else:
            return "Relational DB Tool Output:\n" + "\n".join(str(row) for row in output.rows)
    elif isinstance(output, VectorDBToolOutputSchema):
        if output.error:
            return f"Vector DB Tool Execution Failed: {output.error}"
        else:
            return "Vector DB Tool Output:\n" + "\n".join(str(res) for res in output.results)
    else:
        return "Error: Unknown tool output type."


def run_agent_workflow(user_query: str, main_agent: BaseAgent, vector_db_tool: VectorDBTool,
                       relational_db_tool: RelationalDBTool):
    """
    Orchestrates the multi-step agent workflow to answer a user query.

    Args:
        user_query: The initial query from the user.
        main_agent: The configured reasoning agent instance (using ReasoningInputSchema/AgentDecisionSchema).
        vector_db_tool: Instantiated vector DB tool.
        relational_db_tool: Instantiated relational DB tool (ensure read-only connection if possible).

    Returns:
        The final answer string or an error/fallback message.
    """
    # Use current date for logging context, if desired
    current_date = datetime.date.today()
    logger.info(f"[{current_date}] Starting workflow for query: '{user_query}'")

    # 1. Initial Context Fetch
    try:
        initial_context = get_initial_context(user_query, vector_db_tool)
        logger.debug(f"Initial context fetched (first 500 chars):\n{initial_context[:500]}...")
    except Exception as e:
        logger.error(f"Fatal: Failed to get initial context: {e}", exc_info=True)
        return f"Error: Could not retrieve initial context needed to answer the query. Details: {e}"

    current_context = initial_context
    final_response = None
    last_tool_output_formatted = None

    # --- Main Interaction Loop ---
    for i in range(MAX_ITERATIONS):
        iteration_num = i + 1
        logger.info(f"--- Starting Iteration {iteration_num}/{MAX_ITERATIONS} ---")

        # 4. Prepare Agent Input
        agent_input = ReasoningInputSchema(
            original_query=user_query,
            context=current_context,
            iteration=iteration_num
        )

        # 5. Run Agent
        try:
            agent_decision: AgentDecisionSchema = main_agent.run(agent_input)
            logger.info(f"Agent Action Decision: {agent_decision.action}")
            logger.debug(f"Agent Thought Process: {agent_decision.thought}")
        except Exception as e:
            logger.error(f"Agent execution failed on iteration {iteration_num}: {e}", exc_info=True)
            final_response = f"Error: The agent failed to make a decision during iteration {iteration_num}. Details: {e}"
            break  # Exit loop on agent failure

        # 6. Process Agent Decision
        try:
            if agent_decision.action == 'final_answer':
                if agent_decision.final_answer is not None and agent_decision.final_answer.strip():
                    logger.info("Agent decided on final answer.")
                    final_response = agent_decision.final_answer
                    break
                else:
                    logger.warning("Agent action was 'final_answer' but no answer text was provided.")
                    current_context = "Agent failed to provide a final answer despite choosing the action. Please reassess the situation based on previous context and the original query."
                    last_tool_output_formatted = current_context

            elif agent_decision.action == 'call_vector_db':
                if agent_decision.tool_parameters and isinstance(agent_decision.tool_parameters,
                                                                 VectorDBToolInputSchema):
                    logger.info("Agent requests tool call: vector_db")
                    logger.debug(f"Tool parameters: {agent_decision.tool_parameters}")
                    # --- Directly call the tool's run method ---
                    tool_output_obj: VectorDBToolOutputSchema = vector_db_tool.run(agent_decision.tool_parameters)
                    last_tool_output_formatted = format_tool_output_for_llm(tool_output_obj)
                    current_context = last_tool_output_formatted
                    logger.debug(f"Tool output (formatted, first 500 chars):\n{current_context[:500]}...")
                elif agent_decision.tool_parameters:
                    logger.warning(
                        f"Agent requested 'call_vector_db' but parameters were wrong type: {type(agent_decision.tool_parameters)}")
                    current_context = f"Agent provided incorrect parameter type for 'call_vector_db'. Expected VectorDBToolInputSchema, got {type(agent_decision.tool_parameters)}. Please reassess."
                    last_tool_output_formatted = current_context
                else:
                    logger.warning("Agent chose action 'call_vector_db' but provided no tool parameters.")
                    current_context = "Agent action was 'call_vector_db' but tool parameters were missing. Please reassess the situation based on previous context and the original query."
                    last_tool_output_formatted = current_context

            elif agent_decision.action == 'call_relational_db':
                if agent_decision.tool_parameters and isinstance(agent_decision.tool_parameters,
                                                                 RelationalDBToolInputSchema):
                    logger.info("Agent requests tool call: relational_db")
                    logger.debug(f"Tool parameters: {agent_decision.tool_parameters}")
                    # --- Directly call the tool's run method ---
                    tool_output_obj: RelationalDBToolOutputSchema = relational_db_tool.run(
                        agent_decision.tool_parameters)
                    last_tool_output_formatted = format_tool_output_for_llm(tool_output_obj)
                    current_context = last_tool_output_formatted
                    logger.debug(f"Tool output (formatted, first 500 chars):\n{current_context[:500]}...")
                elif agent_decision.tool_parameters:
                    logger.warning(
                        f"Agent requested 'call_relational_db' but parameters were wrong type: {type(agent_decision.tool_parameters)}")
                    current_context = f"Agent provided incorrect parameter type for 'call_relational_db'. Expected RelationalDBToolInputSchema, got {type(agent_decision.tool_parameters)}. Please reassess."
                    last_tool_output_formatted = current_context
                else:
                    logger.warning("Agent chose action 'call_relational_db' but provided no tool parameters.")
                    current_context = "Agent action was 'call_relational_db' but tool parameters were missing. Please reassess the situation based on previous context and the original query."
                    last_tool_output_formatted = current_context

            else:
                logger.error(f"Unknown or invalid agent action received: {agent_decision.action}")
                final_response = f"Error: Agent returned an invalid action '{agent_decision.action}'."
                break

        except Exception as e:
            # Catch errors during tool execution or formatting step
            tool_name = agent_decision.action if agent_decision.action.startswith('call_') else 'processing'
            logger.error(f"Error during {tool_name} execution/formatting on iteration {iteration_num}: {e}",
                         exc_info=True)
            # Provide error info back to the agent for the next turn
            current_context = f"Error encountered during the last action ({tool_name}): {e}. Please analyze this error and the previous state to decide the next step."
            last_tool_output_formatted = current_context
            # Allow loop to continue so agent can potentially react to the error

    # --- After Loop ---
    if final_response:
        logger.info("Workflow finished with a final response.")
        return final_response
    else:
        logger.warning(
            f"Workflow finished after reaching max iterations ({MAX_ITERATIONS}). No final answer provided by agent.")
        fallback_message = f"Maximum attempts ({MAX_ITERATIONS}) reached. The agent could not provide a final answer."
        if last_tool_output_formatted:
            fallback_message += f"\nLast information gathered or status:\n{last_tool_output_formatted}"
        elif current_context != initial_context:
            fallback_message += f"\nLast status:\n{current_context}"
        return fallback_message


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT UNIQUE,
    chunk_type TEXT, -- class, function, sql_statement, jsp or unknown
    name TEXT, -- name of class or function
    chunk_no INTEGER, -- if the class/function needs to be split into many parts, this is the part no
    start_line INTEGER, -- start line in the source
    end_line INTEGER, -- end line in the source
    file_path TEXT, -- file path relative to project directory
    source TEXT, -- source code
    created_at TEXT
);
"""

QDRANT_SCHEMA = """
{
    "type": "function",  # class, function, sql_statement, jsp or unknown
    "name": "getTarget", # name of class or function   
    "chunk_no": 1,       # if the class/function needs to be split into many parts, this is the part no
    "start_line": 10,    # start line in the source
    "end_line": 60,      # end line in the source
    "file_path": "myproject/authorization/authorization-base/src/main/java/domain/name/project/authorization/visitor/api/AuthorizationVisitor.java",       # file path relative to project directory
    "source": "Here will be source code for getTarget function from line 10 to line 60",          # source code
}
"""


def run(query: str, sqlite_client, qdrant_client):
    orchestrator_agent = BaseAgent(
        BaseAgentConfig(
            client=instructor.from_openai(openai.OpenAI()),
            model="gpt-4o-mini",
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "You will receive a query and context, and your goal is to answer the query."
                ],
                steps=[
                    "First reason and then choose an action.",
                    "If you can answer with confidence, choose final_answer and provide the final_answer.",
                    "You are encouraged to use tool when in doubt, choose call_vector_db or call_relational_db and provide the necessary "
                    "tool_parameters.",
                    "Use the provided context and potentially ask for specific tool calls to get missing information.",
                    "When you use call_relational_db create a query valid for this schema " + SQLITE_SCHEMA,
                    "When you use call_vector_db you use a semantic query - the output will be in this format " + QDRANT_SCHEMA
                ],
            ),
            input_schema=ReasoningInputSchema,
            output_schema=AgentDecisionSchema,
        )
    )

    vector_tool_cfg = VectorDBToolConfig(
        qdrant_client=qdrant_client,
        collection_name=QDRANT_COLLECTION,
        embedding_model=EMBED_MODEL
    )

    db_tool_cfg = RelationalDBToolConfig(
        conn=sqlite_client
    )

    vector_db_tool = VectorDBTool(vector_tool_cfg)
    relational_db_tool = RelationalDBTool(db_tool_cfg)
    logger.info("Tools configured, running the main workflow...")
    final_result = run_agent_workflow(query, orchestrator_agent, vector_db_tool, relational_db_tool)
    return final_result


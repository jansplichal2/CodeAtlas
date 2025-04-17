from atlas.agents.contextualizer import ContextualizerAgent
from atlas.agents.decision_and_query import DecisionAndQueryAgent


def run_agents_on_query(user_query: str, max_steps: int = 3):
    print(f"🧪 Running agent system on: '{user_query}'")

    context_agent = ContextualizerAgent()
    decision_agent = DecisionAndQueryAgent(max_steps=max_steps)

    # Step 1: Get context from vector DB
    context = context_agent.run(user_query, top_k=5)
    print(f"\\n📚 Retrieved {len(context)} context items")

    # Step 2: Let decision agent reason with tools
    result = decision_agent.run(user_goal=user_query, context=context)

    print(f"\\n✅ Final output from DecisionAndQueryAgent:")
    for step in result:
        print(f"→ Tool: {step['tool']}")
        print(f"  Result: {step['result']}")
    return result


if __name__ == "__main__":
    # Simulate a broken SQL to trigger fallback to vector DB
    run_agents_on_query("SELECT * FROM non_existing_table", max_steps=3)

from atlas.tools.vector_db_tool import VectorDBTool
from atlas.tools.relational_db_tool import RelationalDBTool


class DecisionAndQueryAgent:
    def __init__(self, max_steps: int = 5):
        self.vector_tool = VectorDBTool()
        self.relational_tool = RelationalDBTool()
        self.max_steps = max_steps

    def run(self, user_goal: str, context: list):
        print(f"🤖 DecisionAndQueryAgent: reasoning on goal: '{user_goal}'")
        steps = 0
        history = []

        while steps < self.max_steps:
            steps += 1
            print(f"🔁 Step {steps}")
            # Simulate simple decision logic (placeholder for LLM reasoning)
            if "SELECT" in user_goal.upper():
                result = self.relational_tool.run(user_goal)
                history.append({"tool": "relational_db_query", "result": result})
            else:
                result = self.vector_tool.run(query=user_goal)
                history.append({"tool": "vector_db_search", "result": result})
            break  # Simulated single-step for now

        return history

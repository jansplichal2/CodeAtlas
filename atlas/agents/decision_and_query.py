from atlas.agents.tools.vector_db_tool import VectorDBTool
from atlas.agents.tools.relational_db_tool import RelationalDBTool


class DecisionAndQueryAgent:
    def __init__(self, max_steps: int = 5):
        self.vector_tool = VectorDBTool()
        self.relational_tool = RelationalDBTool()
        self.max_steps = max_steps
        self.history = []

    def run_step(self, goal: str, context: list, step: int):
        print(f"🔁 Step {step}")
        # Basic example rule: SQL first, fallback to vector if error
        if step == 1 or (self.history and self.history[-1].get("error")):
            if "SELECT" in goal.upper():
                result = self.relational_tool.run(goal)
                return {"tool": "relational_db_query", "result": result}
        # fallback to vector search if prior failed
        return {
            "tool": "vector_db_search",
            "result": self.vector_tool.run(query=goal)
        }

    def run(self, user_goal: str, context: list):
        print(f"🤖 DecisionAndQueryAgent: reasoning on goal: '{user_goal}'")
        for step in range(1, self.max_steps + 1):
            step_result = self.run_step(user_goal, context, step)
            self.history.append(step_result)

            # Optional break condition: successful SQL with > 0 rows
            if (
                    step_result["tool"] == "relational_db_query"
                    and isinstance(step_result["result"], list)
                    and len(step_result["result"]) > 0
            ):
                print(f"✅ SQL returned {len(step_result['result'])} rows")
                break

        return self.history

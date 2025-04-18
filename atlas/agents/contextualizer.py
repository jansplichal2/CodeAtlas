from atlas.agents.tools.vector_db_tool import VectorDBTool


class ContextualizerAgent:
    def __init__(self):
        self.vector_tool = VectorDBTool()

    def run(self, user_query: str, top_k: int = 5):
        print(f"🧠 ContextualizerAgent: retrieving context for: '{user_query}'")
        return self.vector_tool.run(query=user_query, top_k=top_k)

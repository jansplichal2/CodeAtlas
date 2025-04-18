import sqlite3
from atlas.agents.tools.base import BaseTool
from atlas.config import DB_PATH


class RelationalDBTool(BaseTool):
    name = "relational_db_query"

    def run(self, query: str):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            except Exception as e:
                return {"error": str(e)}

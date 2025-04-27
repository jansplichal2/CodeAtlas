from atlas.sqlite.utils import execute_sql_query

def handle(query: str):
    return execute_sql_query(query)
import logging

def get_method_context(db_conn, parent_type, parent_method, line_no, context_lines=5):
    start = line_no - context_lines
    end = line_no + context_lines

    logging.info(f"get_method_context: {parent_type}, {parent_method}, {line_no}, {context_lines}")

    cursor = db_conn.cursor()
    try:
        query = """
        SELECT file_path, file_line_no, source, parent_method, parent_type
        FROM lines
        WHERE parent_type = ?
          AND parent_method = ?
          AND file_line_no BETWEEN ? AND ?
        ORDER BY file_line_no
        """
        cursor.execute(query, (parent_type, parent_method, start, end))
        rows = cursor.fetchall()

        if not rows:
            return None

        return {
            "file_path": rows[0][0],
            "parent_method": rows[0][3],
            "parent_type": rows[0][4],
            "lines": [
                {"line_no": row[1], "source": row[2]} for row in rows
            ]
        }
    finally:
        cursor.close()
import sqlite3
from server.db import get_db

def normalize(rows):
    normalized = []
    for row in rows:
        new_row = []
        for v in row:
            if isinstance(v, str):
                new_row.append(v.strip().lower())
            elif isinstance(v, float):
                new_row.append(round(v, 2))
            else:
                new_row.append(v)
        normalized.append(tuple(new_row))
    return sorted(normalized)

def grade(query: str, expected_output: list) -> float:
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()

        if not result:
            return 0.0

        got = normalize(result)
        want = normalize(expected_output)

        if got == want:
            return 1.0

        matched = sum(1 for row in got if row in want)
        partial = matched / max(len(want), len(got))
        return round(partial * 0.5, 2)

    except Exception:
        return 0.0
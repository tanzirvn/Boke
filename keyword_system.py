# keyword_system.py
from database import get_conn
import json

def add_keyword(keyword, ktype, content, admin_id, category=None, extras=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO keywords (keyword, type, content, extras, admin_id, category) VALUES (?,?,?,?,?,?)",
        (keyword.lower().strip(), ktype, content, json.dumps(extras) if extras else None, admin_id, category)
    )
    conn.commit()
    conn.close()
    return True

def delete_keyword(keyword):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM keywords WHERE keyword = ?", (keyword.lower().strip(),))
    changed = c.rowcount
    conn.commit()
    conn.close()
    return changed > 0

def edit_keyword(keyword, **fields):
    allowed = {"type", "content", "extras", "category"}
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    params.append(keyword.lower().strip())
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"UPDATE keywords SET {', '.join(updates)} WHERE keyword = ?", tuple(params))
    conn.commit()
    conn.close()
    return True

def get_keyword(keyword):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, keyword, type, content, extras FROM keywords WHERE keyword = ?", (keyword.lower().strip(),))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    import json
    return {"id": row[0], "keyword": row[1], "type": row[2], "content": row[3], "extras": json.loads(row[4]) if row[4] else None}

def list_keywords(limit=100):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, keyword, type, category, admin_id, created_at FROM keywords ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
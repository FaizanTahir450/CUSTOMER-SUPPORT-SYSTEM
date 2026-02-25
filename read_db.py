import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'customer_support.db')

if not os.path.exists(DB_PATH):
    print(f"ERROR: Database file not found: {DB_PATH}")
    sys.exit(2)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print(f"Opened database: {DB_PATH}\n")

# List tables
cur.execute("SELECT name, type, sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY name;")
tables = cur.fetchall()
if not tables:
    print("No tables or views found in the database.")
    conn.close()
    sys.exit(0)

for t in tables:
    name = t['name']
    kind = t['type']
    sql = t['sql']
    print(f"== {kind.upper()}: {name} ==")
    if sql:
        print(sql)
    else:
        print("(no CREATE statement available)")

    # show row count
    try:
        cur.execute(f"SELECT COUNT(*) as cnt FROM '{name}'")
        cnt = cur.fetchone()['cnt']
    except Exception as e:
        cnt = f"error: {e}"
    print(f"Rows: {cnt}")

    # show up to 5 sample rows
    try:
        cur.execute(f"SELECT * FROM '{name}' LIMIT 5")
        rows = cur.fetchall()
        if rows:
            cols = rows[0].keys()
            print(' | '.join(cols))
            for r in rows:
                print(' | '.join([str(r[c]) for c in cols]))
        else:
            print("(no rows)")
    except Exception as e:
        print(f"Could not read rows: {e}")

    print('\n')

conn.close()
print('Done.')

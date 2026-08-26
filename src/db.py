import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "premier_league.duckdb"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def get_connection():
    con = duckdb.connect(str(DB_PATH))
    with open(SCHEMA_PATH) as f:
        con.execute(f.read())
    return con

if __name__ == "__main__":
    con = get_connection()
    print("Tables:", con.execute("SHOW TABLES").fetchall())

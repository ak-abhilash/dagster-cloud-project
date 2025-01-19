import duckdb
import os
from tabulate import tabulate

def query_duckdb():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    db_path = os.path.join(project_dir, 'data', 'processed.db')

    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return

    conn = duckdb.connect(db_path)

    print("\nAvailable Tables:")
    tables = conn.execute("SHOW TABLES").fetchall()
    print(tabulate(tables, headers=['Table Name']))

    columns = conn.execute("SELECT * FROM test_table LIMIT 0").description
    column_names = [col[0] for col in columns]

    print("\nSample Data:")
    result = conn.execute("SELECT * FROM test_table LIMIT 5").fetchall()
    print(tabulate(result, headers=column_names))

    conn.close()

if __name__ == "__main__":
    query_duckdb()
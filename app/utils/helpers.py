import duckdb
import pandas as pd
import os

def init_db():
    """Initializes an in-memory DuckDB connection."""
    return duckdb.connect(database=':memory:')

def load_data(conn, raw_path, ref_path):
    """Loads CSV data into DuckDB tables."""
    raw_df = pd.read_csv(raw_path, dtype=str) # Read as string to prevent early parsing errors
    ref_df = pd.read_csv(ref_path, dtype=str)
    
    conn.execute("CREATE OR REPLACE TABLE raw_data AS SELECT * FROM raw_df")
    conn.execute("CREATE OR REPLACE TABLE ref_data AS SELECT * FROM ref_df")
    return raw_df, ref_df
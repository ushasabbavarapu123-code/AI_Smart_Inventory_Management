import os
import sys
import pandas as pd
from typing import Dict

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import get_db_connection, setup_logger

logger = setup_logger("extract")

def extract_tables() -> Dict[str, pd.DataFrame]:
    """
    Extracts all tables from the SQLite database, profiles their structures,
    saves raw snapshot files to data/raw/, and returns a dictionary of DataFrames.
    """
    logger.info("Starting Data Extraction phase...")
    
    # Define paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    # Establish connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get list of all tables in the database
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
        logger.info(f"Identified database tables for extraction: {tables}")
    except Exception as e:
        logger.error(f"Failed to query database tables: {e}")
        conn.close()
        raise
        
    extracted_dfs: Dict[str, pd.DataFrame] = {}
    
    for table in tables:
        logger.info(f"Extracting table: '{table}'")
        try:
            # Query table into pandas DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            
            # Profile dataset
            row_count = len(df)
            col_count = len(df.columns)
            mem_usage = df.memory_usage(deep=True).sum() / (1024 * 1024) # MB
            missing_vals = df.isnull().sum().to_dict()
            dup_count = df.duplicated().sum()
            dtypes = df.dtypes.to_dict()
            
            # Log profiling metrics
            logger.info(f"Table '{table}' extraction profile:")
            logger.info(f"  - Rows: {row_count}")
            logger.info(f"  - Columns: {col_count}")
            logger.info(f"  - Memory Usage: {mem_usage:.4f} MB")
            logger.info(f"  - Duplicate Records: {dup_count}")
            logger.info(f"  - Data Types: { {col: str(dtype) for col, dtype in dtypes.items()} }")
            logger.info(f"  - Missing Values: {missing_vals}")
            
            # Save raw CSV file
            raw_csv_path = os.path.join(raw_dir, f"{table}.csv")
            df.to_csv(raw_csv_path, index=False, encoding="utf-8")
            logger.info(f"Saved raw snapshot to: {raw_csv_path}")
            
            extracted_dfs[table] = df
        except Exception as e:
            logger.error(f"Failed to extract table '{table}': {e}")
            conn.close()
            raise
            
    conn.close()
    logger.info("Data Extraction phase completed successfully.")
    return extracted_dfs

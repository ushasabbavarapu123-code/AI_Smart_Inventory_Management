import os
import sys
import sqlite3
import pandas as pd
from typing import Dict, Optional

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import get_db_connection, setup_logger, get_settings

logger = setup_logger("extract")

def extract_tables(conn: Optional[sqlite3.Connection] = None) -> Dict[str, pd.DataFrame]:
    """
    Extracts all operational tables from the SQLite database, profiles their structures,
    saves raw snapshot files to data/raw/ if configured, and returns a dictionary of DataFrames.
    
    Args:
        conn: Optional SQLite connection to use. If None, retrieves one from settings.
        
    Returns:
        Dict[str, pd.DataFrame]: Extracted tables mapped by table name.
    """
    logger.info("Starting Data Extraction phase...")
    settings = get_settings()
    
    # Establish connection if not provided
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cursor = conn.cursor()
    
    try:
        # Get list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
        logger.info(f"Identified database tables for extraction: {tables}")
    except Exception as e:
        logger.error(f"Failed to query database tables: {e}")
        if should_close:
            conn.close()
        raise
        
    extracted_dfs: Dict[str, pd.DataFrame] = {}
    
    raw_dir = os.path.join(settings.export_dir, "..", "raw")
    raw_dir = os.path.abspath(raw_dir)
    os.makedirs(raw_dir, exist_ok=True)
    
    for table in tables:
        logger.debug(f"Extracting table: '{table}'")
        try:
            # Query table directly into pandas DataFrame without copy overhead
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            
            # Save raw CSV file for backup and debugging
            raw_csv_path = os.path.join(raw_dir, f"{table}.csv")
            df.to_csv(raw_csv_path, index=False, encoding="utf-8")
            logger.debug(f"Saved raw snapshot of '{table}' ({len(df)} rows) to: {raw_csv_path}")
            
            extracted_dfs[table] = df
        except Exception as e:
            logger.error(f"Failed to extract table '{table}': {e}")
            if should_close:
                conn.close()
            raise
            
    if should_close:
        conn.close()
        
    logger.info("Data Extraction phase completed successfully.")
    return extracted_dfs

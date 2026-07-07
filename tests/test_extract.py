import os
import sqlite3
import pytest
import pandas as pd
from extract import extract_tables
from utils import get_db_connection

def test_extract_tables_success(mock_db_path):
    """Verifies that all tables are extracted successfully from a valid database."""
    conn = get_db_connection(mock_db_path)
    dfs = extract_tables(conn)
    
    assert isinstance(dfs, dict)
    expected_tables = {'products', 'inventory', 'sales', 'forecasts', 'suppliers', 'purchase_orders', 'users', 'audit_logs'}
    assert expected_tables.issubset(set(dfs.keys()))
    
    # Assert counts
    assert len(dfs["products"]) == 2
    assert len(dfs["sales"]) == 3
    assert len(dfs["suppliers"]) == 1

def test_extract_tables_missing_db():
    """Verifies that a FileNotFoundError is raised if database path does not exist."""
    with pytest.raises(FileNotFoundError):
        get_db_connection("non_existent_db_path.db")

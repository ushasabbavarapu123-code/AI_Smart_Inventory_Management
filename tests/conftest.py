import os
import sys
import tempfile
import sqlite3
import pytest
import shutil
import pandas as pd
from typing import Generator

# Add project root and pipeline folder to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PIPELINE_ROOT = os.path.join(PROJECT_ROOT, "pipeline")
if PIPELINE_ROOT not in sys.path:
    sys.path.insert(0, PIPELINE_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import utils
from config.settings import Settings

@pytest.fixture(scope="session")
def temp_dir() -> Generator[str, None, None]:
    """Creates a temporary directory for test file exports."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture(scope="session")
def mock_db_path(temp_dir: str) -> str:
    """Creates a mock SQLite database path with sample tables and records."""
    db_path = os.path.join(temp_dir, "test_inventory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create tables
    cursor.execute("""
    CREATE TABLE products (
        product_id TEXT PRIMARY KEY,
        sku TEXT UNIQUE,
        name TEXT,
        category TEXT,
        unit_cost REAL,
        reorder_point INTEGER,
        created_at TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE suppliers (
        supplier_id TEXT PRIMARY KEY,
        name TEXT,
        contact_person TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        lead_time_days INTEGER,
        rating REAL,
        created_at TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE inventory (
        inventory_id TEXT PRIMARY KEY,
        product_id TEXT,
        quantity INTEGER,
        location TEXT,
        last_updated TEXT,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE sales (
        sale_id TEXT PRIMARY KEY,
        product_id TEXT,
        sale_date TEXT,
        quantity INTEGER,
        unit_price REAL,
        customer_type TEXT,
        created_at TEXT,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE purchase_orders (
        po_id TEXT PRIMARY KEY,
        supplier_id TEXT,
        product_id TEXT,
        quantity INTEGER,
        unit_cost REAL,
        order_date TEXT,
        expected_delivery TEXT,
        actual_delivery TEXT,
        status TEXT,
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE forecasts (
        forecast_id TEXT PRIMARY KEY,
        product_id TEXT,
        forecast_date TEXT,
        predicted_qty REAL,
        confidence_low REAL,
        confidence_high REAL,
        model_used TEXT,
        generated_at TEXT,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        full_name TEXT,
        role TEXT,
        is_active INTEGER,
        last_login TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE audit_logs (
        log_id TEXT PRIMARY KEY,
        action TEXT,
        entity TEXT,
        entity_id TEXT,
        user_id TEXT,
        old_value TEXT,
        new_value TEXT,
        ip_address TEXT,
        timestamp TEXT
    );
    """)
    
    # 2. Insert mock data
    cursor.execute("""
    INSERT INTO products VALUES (
        'p1', 'ELEC-LAP-001', 'Test Laptop', 'Electronics', 500.0, 10, '2026-06-01T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO products VALUES (
        'p2', 'ELEC-MOU-002', 'Test Mouse', 'Electronics', 10.0, 5, '2026-06-01T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO suppliers VALUES (
        's1', 'TechSupplier Ltd', 'John', 'john@tech.com', '123', 5, 4.5, '2026-06-01T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO inventory VALUES (
        'i1', 'p1', 15, 'Warehouse-A', '2026-07-01T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO inventory VALUES (
        'i2', 'p2', 3, 'Warehouse-B', '2026-07-01T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO sales VALUES (
        'sa1', 'p1', '2026-07-02', 2, 750.0, 'Retail', '2026-07-02T18:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO sales VALUES (
        'sa2', 'p2', '2026-07-03', 10, 20.0, 'Wholesale', '2026-07-03T18:00:00Z'
    );
    """)
    # Add sales outlier for IQR capping testing (normally quantity is ~2-10, so 100 is an outlier)
    cursor.execute("""
    INSERT INTO sales VALUES (
        'sa3', 'p2', '2026-07-04', 100, 20.0, 'Wholesale', '2026-07-04T18:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO purchase_orders VALUES (
        'po1', 's1', 'p1', 20, 500.0, '2026-06-15', '2026-06-22', '2026-06-21', 'Received', 'Urgent', '2026-06-15T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO forecasts VALUES (
        'f1', 'p1', '2026-08-01', 45.0, 30.0, 60.0, 'ARIMA', '2026-07-07T12:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO users VALUES (
        'u1', 'admin@test.com', 'hash', 'Admin User', 'Admin', 1, '2026-07-07T10:00:00Z'
    );
    """)
    cursor.execute("""
    INSERT INTO audit_logs VALUES (
        'l1', 'CREATE_SALE', 'sales', 'sa1', 'system', NULL, NULL, '127.0.0.1', '2026-07-02T18:00:00Z'
    );
    """)
    
    conn.commit()
    conn.close()
    return db_path

@pytest.fixture(autouse=True)
def configure_test_settings(mock_db_path: str, temp_dir: str):
    """
    Automatically configures global settings to point to the temporary test DB
    and output directory for every test execution.
    """
    settings = utils.get_settings()
    settings.db_path = mock_db_path
    settings.export_dir = temp_dir
    settings.save_timestamped_archive = False
    settings.export_formats = ["csv"]
    yield settings

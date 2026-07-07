import os
import logging
import sqlite3
from typing import Optional

def setup_logger(name: str = "pipeline") -> logging.Logger:
    """
    Configures and returns a logger that outputs to both console and a log file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "pipeline.log")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def get_db_path() -> str:
    """
    Resolves the SQLite database path. Checks:
    1. Environment variable INVENTORY_DB_PATH
    2. app/.env file (DB_PATH value relative to app/)
    3. Default path data/inventory.db relative to project root
    """
    logger = setup_logger("utils")
    
    # 1. Check Env Variable
    env_db_path = os.environ.get("INVENTORY_DB_PATH")
    if env_db_path:
        logger.info(f"Using database path from INVENTORY_DB_PATH: {env_db_path}")
        return os.path.abspath(env_db_path)

    # Resolve project root (one level up from pipeline/)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # 2. Check app/.env
    app_env_path = os.path.join(project_root, "app", ".env")
    if os.path.exists(app_env_path):
        try:
            with open(app_env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("DB_PATH="):
                        db_val = line.strip().split("=", 1)[1]
                        # Resolve path relative to app folder
                        resolved_path = os.path.abspath(os.path.join(project_root, "app", db_val))
                        logger.info(f"Using database path from app/.env: {resolved_path}")
                        return resolved_path
        except Exception as e:
            logger.warning(f"Error reading app/.env: {e}")

    # 3. Default Path
    default_path = os.path.abspath(os.path.join(project_root, "data", "inventory.db"))
    logger.info(f"Using default database path: {default_path}")
    return default_path

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    """
    logger = setup_logger("utils")
    if not db_path:
        db_path = get_db_path()
        
    if not os.path.exists(db_path):
        err_msg = f"Database file not found at: {db_path}"
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    try:
        conn = sqlite3.connect(db_path)
        # Enable foreign key constraints in sqlite
        conn.execute("PRAGMA foreign_keys = ON;")
        logger.info(f"Successfully connected to SQLite database at {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database at {db_path}: {e}")
        raise

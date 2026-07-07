import os
import sys
import logging
import sqlite3
from typing import Optional

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.settings import Settings

_settings_instance: Optional[Settings] = None

def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Returns a cached global instance of the Settings configuration.
    """
    global _settings_instance
    if _settings_instance is None or config_path is not None:
        _settings_instance = Settings(config_path)
    return _settings_instance

def setup_logger(name: str = "pipeline", level: Optional[str] = None) -> logging.Logger:
    """
    Configures and returns a logger that outputs to both console and a log file.
    Uses configurations from the Settings object.
    """
    logger = logging.getLogger(name)
    settings = get_settings()
    
    # Resolve log level
    log_level_str = level or settings.log_level
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        # Update level for existing handlers in case level changed
        for handler in logger.handlers:
            handler.setLevel(log_level)
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )

    # Console Handler
    if settings.log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File Handler
    if settings.log_to_file:
        log_file = settings.log_file_path
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Establishes a connection to the SQLite database.
    If no db_path is passed, the path from the Settings config is used.
    """
    logger = setup_logger("utils")
    settings = get_settings()
    
    target_path = db_path or settings.db_path
    
    if not os.path.exists(target_path):
        err_msg = f"Database file not found at: {target_path}"
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    try:
        conn = sqlite3.connect(target_path)
        # Enable foreign key constraints in SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        logger.debug(f"Successfully connected to SQLite database at {target_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database at {target_path}: {e}")
        raise

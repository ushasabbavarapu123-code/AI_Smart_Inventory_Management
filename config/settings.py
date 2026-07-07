import os
import sys
from typing import Dict, Any, List

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Load python-dotenv if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, "app", ".env"))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

class Settings:
    """
    Central settings class that loads configuration from config.yaml
    and overrides them with environment variables if present.
    """
    def __init__(self, config_path: str = None):
        if not config_path:
            config_path = os.path.join(PROJECT_ROOT, "config", "config.yaml")
        
        self.config_path = config_path
        self.config_dict = self._load_config_file(config_path)
        
        # Database Settings
        self.db_path = self._get_setting("database.path", "data/inventory.db")
        # Check env variable overrides
        env_inventory_db_path = os.environ.get("INVENTORY_DB_PATH")
        env_db_path = os.environ.get("DB_PATH")
        
        if env_inventory_db_path:
            self.db_path = env_inventory_db_path
            if not os.path.isabs(self.db_path):
                self.db_path = os.path.abspath(os.path.join(PROJECT_ROOT, self.db_path))
        elif env_db_path:
            # DB_PATH from app/.env is relative to the app/ directory
            self.db_path = env_db_path
            if not os.path.isabs(self.db_path):
                self.db_path = os.path.abspath(os.path.join(PROJECT_ROOT, "app", self.db_path))
        else:
            if not os.path.isabs(self.db_path):
                self.db_path = os.path.abspath(os.path.join(PROJECT_ROOT, self.db_path))

        # Export Settings
        self.export_dir = os.path.abspath(
            os.path.join(PROJECT_ROOT, self._get_setting("export.directory", "data/exports"))
        )
        self.export_formats = self._get_setting("export.formats", ["csv", "xlsx", "parquet", "pkl"])
        self.save_timestamped_archive = self._get_setting("export.save_timestamped_archive", True)

        # Logging Settings
        self.log_level = os.environ.get("LOG_LEVEL") or self._get_setting("logging.level", "INFO")
        self.log_to_console = self._get_setting("logging.log_to_console", True)
        self.log_to_file = self._get_setting("logging.log_to_file", True)
        self.log_file_path = os.path.abspath(
            os.path.join(PROJECT_ROOT, self._get_setting("logging.log_file_path", "logs/pipeline.log"))
        )

        # Feature Flags
        self.run_profiling = self._get_setting("feature_flags.run_profiling", True)
        self.run_validation = self._get_setting("feature_flags.run_validation", True)
        self.generate_quality_scorecard = self._get_setting("feature_flags.generate_quality_scorecard", True)
        self.generate_data_dictionary = self._get_setting("feature_flags.generate_data_dictionary", True)
        self.clean_only = self._get_setting("feature_flags.clean_only", False)

        # Pipeline Options
        self.outlier_iqr_multiplier = float(self._get_setting("pipeline_options.outlier_iqr_multiplier", 1.5))
        self.default_supplier_lead_time = int(self._get_setting("pipeline_options.default_supplier_lead_time", 7))
        self.default_supplier_rating = float(self._get_setting("pipeline_options.default_supplier_rating", 3.0))
        self.max_days_until_stockout = float(self._get_setting("pipeline_options.max_days_until_stockout", 999.0))

    def _load_config_file(self, path: str) -> Dict[str, Any]:
        """Loads the YAML file or falls back to an empty dict if not found or PyYAML is missing."""
        if not os.path.exists(path):
            return {}
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            # Simple fallback parser for key-value pair subset if pyyaml is not loaded yet
            # Since we will install PyYAML shortly, this acts as a helper.
            config = {}
            try:
                with open(path, "r", encoding="utf-8") as f:
                    section = ""
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if ":" in line and not line.startswith("-"):
                            key, val = line.split(":", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if val == "":
                                section = key
                                config[section] = {}
                            else:
                                if section:
                                    config[section][key] = self._parse_val(val)
                                else:
                                    config[key] = self._parse_val(val)
                        elif line.startswith("-") and section:
                            val = line[1:].strip().strip('"').strip("'")
                            if not isinstance(config[section], list):
                                config[section] = []
                            config[section].append(self._parse_val(val))
            except Exception:
                pass
            return config
        except Exception:
            return {}

    def _parse_val(self, val: str) -> Any:
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    def _get_setting(self, path: str, default: Any) -> Any:
        """Retrieves a nested setting using dot notation, e.g. 'database.path'."""
        keys = path.split(".")
        curr = self.config_dict
        for key in keys:
            if isinstance(curr, dict) and key in curr:
                curr = curr[key]
            else:
                return default
        return curr

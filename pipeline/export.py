import os
import sys
import datetime
import pandas as pd
from typing import Dict, List

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger

logger = setup_logger("export")

def export_datasets(processed_dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """
    Exports final enriched datasets in CSV, Excel (XLSX), Parquet, and Pickle formats.
    Saves outputs in data/exports/ and in a timestamped archival directory.
    Returns a list of all successfully written file paths.
    """
    logger.info("Starting Data Export phase...")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Define export paths
    export_dir = os.path.join(project_root, "data", "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    # Create timestamped subfolder
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(export_dir, "timestamped", timestamp)
    os.makedirs(archive_dir, exist_ok=True)
    
    logger.info(f"Target standard export directory: {export_dir}")
    logger.info(f"Target archive directory: {archive_dir}")
    
    exported_paths: List[str] = []
    
    for name, df in processed_dfs.items():
        logger.info(f"Exporting table: '{name}' (rows: {len(df)})")
        
        # We need copies to modify date datatypes to string/timestamp depending on format
        csv_df = df.copy()
        xlsx_df = df.copy()
        parquet_df = df.copy()
        pickle_df = df.copy()
        
        # Ensure column datatypes are compatible with Parquet
        # Parquet doesn't allow mixed types or object columns easily unless they are string
        for col in parquet_df.columns:
            if parquet_df[col].dtype == object:
                # If column is series of objects (like strings), cast to string
                # Check if it has datetime values
                try:
                    parquet_df[col] = parquet_df[col].astype(str)
                except Exception:
                    pass
            elif pd.api.types.is_datetime64_any_dtype(parquet_df[col]):
                # Parquet handles datetime64, keep it
                pass
                
        # Fix date types for Excel (excel handles datetimes well, but keep it clean)
        for col in xlsx_df.columns:
            if pd.api.types.is_datetime64_any_dtype(xlsx_df[col]):
                # Remove timezone if any, Excel doesn't support tz-aware datetimes
                xlsx_df[col] = xlsx_df[col].dt.tz_localize(None)

        # Base filenames
        csv_name = f"{name}.csv"
        xlsx_name = f"{name}.xlsx"
        parquet_name = f"{name}.parquet"
        pkl_name = f"{name}.pkl"

        # Standard active locations
        csv_path = os.path.join(export_dir, csv_name)
        xlsx_path = os.path.join(export_dir, xlsx_name)
        parquet_path = os.path.join(export_dir, parquet_name)
        pkl_path = os.path.join(export_dir, pkl_name)
        
        # Timestamped archive locations
        arch_csv_path = os.path.join(archive_dir, csv_name)
        arch_xlsx_path = os.path.join(archive_dir, xlsx_name)
        arch_parquet_path = os.path.join(archive_dir, parquet_name)
        arch_pkl_path = os.path.join(archive_dir, pkl_name)

        try:
            # 1. Export CSV
            # Format datetime columns as standard strings
            for col in csv_df.columns:
                if pd.api.types.is_datetime64_any_dtype(csv_df[col]):
                    csv_df[col] = csv_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            csv_df.to_csv(csv_path, index=False, encoding="utf-8")
            csv_df.to_csv(arch_csv_path, index=False, encoding="utf-8")
            exported_paths.extend([csv_path, arch_csv_path])
            
            # 2. Export Excel (requires openpyxl)
            xlsx_df.to_excel(xlsx_path, index=False, engine="openpyxl")
            xlsx_df.to_excel(arch_xlsx_path, index=False, engine="openpyxl")
            exported_paths.extend([xlsx_path, arch_xlsx_path])
            
            # 3. Export Parquet (requires pyarrow)
            parquet_df.to_parquet(parquet_path, index=False, engine="pyarrow")
            parquet_df.to_parquet(arch_parquet_path, index=False, engine="pyarrow")
            exported_paths.extend([parquet_path, arch_parquet_path])
            
            # 4. Export Pickle
            pickle_df.to_pickle(pkl_path)
            pickle_df.to_pickle(arch_pkl_path)
            exported_paths.extend([pkl_path, arch_pkl_path])
            
            logger.info(f"Successfully exported table '{name}' in CSV, XLSX, Parquet, and Pickle formats.")
            
        except Exception as e:
            logger.error(f"Failed to export table '{name}': {e}")
            raise

    logger.info("Data Export phase completed successfully.")
    return exported_paths

import os
import sys
import datetime
import pandas as pd
from typing import Dict, List, Optional

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_settings

logger = setup_logger("export")

def export_datasets(processed_dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """
    Exports final enriched datasets in configured formats (e.g. CSV, XLSX, Parquet, Pickle).
    Saves outputs in the configured exports directory and in a timestamped archival directory.
    Returns a list of all successfully written file paths.
    """
    logger.info("Starting Data Export phase...")
    settings = get_settings()
    
    export_dir = settings.export_dir
    os.makedirs(export_dir, exist_ok=True)
    
    # Create timestamped subfolder if configured
    archive_dir: Optional[str] = None
    if settings.save_timestamped_archive:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = os.path.join(export_dir, "timestamped", timestamp)
        os.makedirs(archive_dir, exist_ok=True)
        logger.debug(f"Target archive directory: {archive_dir}")
        
    logger.debug(f"Target standard export directory: {export_dir}")
    
    exported_paths: List[str] = []
    configured_formats = [f.lower().strip() for f in settings.export_formats]
    
    for name, df in processed_dfs.items():
        if df.empty:
            logger.warning(f"Table '{name}' is empty. Skipping export.")
            continue
            
        logger.debug(f"Exporting table: '{name}' (rows: {len(df)})")
        
        # 1. Export CSV
        if "csv" in configured_formats:
            csv_path = os.path.join(export_dir, f"{name}.csv")
            # Format datetime columns as standard strings for CSV
            csv_df = df.copy()
            for col in csv_df.columns:
                if pd.api.types.is_datetime64_any_dtype(csv_df[col]):
                    csv_df[col] = csv_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            csv_df.to_csv(csv_path, index=False, encoding="utf-8")
            exported_paths.append(csv_path)
            
            if archive_dir:
                arch_csv_path = os.path.join(archive_dir, f"{name}.csv")
                csv_df.to_csv(arch_csv_path, index=False, encoding="utf-8")
                exported_paths.append(arch_csv_path)

        # 2. Export Excel (requires openpyxl)
        if "xlsx" in configured_formats:
            xlsx_path = os.path.join(export_dir, f"{name}.xlsx")
            xlsx_df = df.copy()
            # Remove timezones for Excel compatibility
            for col in xlsx_df.columns:
                if pd.api.types.is_datetime64_any_dtype(xlsx_df[col]):
                    xlsx_df[col] = xlsx_df[col].dt.tz_localize(None)
                    
            xlsx_df.to_excel(xlsx_path, index=False, engine="openpyxl")
            exported_paths.append(xlsx_path)
            
            if archive_dir:
                arch_xlsx_path = os.path.join(archive_dir, f"{name}.xlsx")
                xlsx_df.to_excel(arch_xlsx_path, index=False, engine="openpyxl")
                exported_paths.append(arch_xlsx_path)
                
        # 3. Export Parquet (requires pyarrow)
        if "parquet" in configured_formats or "pq" in configured_formats:
            parquet_path = os.path.join(export_dir, f"{name}.parquet")
            parquet_df = df.copy()
            
            # Standardize object/string dtypes for parquet compatibility
            for col in parquet_df.columns:
                if parquet_df[col].dtype == object:
                    parquet_df[col] = parquet_df[col].astype(str)
                    
            parquet_df.to_parquet(parquet_path, index=False, engine="pyarrow")
            exported_paths.append(parquet_path)
            
            if archive_dir:
                arch_parquet_path = os.path.join(archive_dir, f"{name}.parquet")
                parquet_df.to_parquet(arch_parquet_path, index=False, engine="pyarrow")
                exported_paths.append(arch_parquet_path)
                
        # 4. Export Pickle
        if "pkl" in configured_formats or "pickle" in configured_formats:
            pkl_path = os.path.join(export_dir, f"{name}.pkl")
            df.to_pickle(pkl_path)
            exported_paths.append(pkl_path)
            
            if archive_dir:
                arch_pkl_path = os.path.join(archive_dir, f"{name}.pkl")
                df.to_pickle(arch_pkl_path)
                exported_paths.append(arch_pkl_path)
                
        logger.info(f"Successfully exported table '{name}' to {configured_formats}")
        
    logger.info("Data Export phase completed successfully.")
    return exported_paths

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Tuple

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_settings

logger = setup_logger("clean")

def profile_data_quality(dfs: Dict[str, pd.DataFrame]) -> Dict[str, dict]:
    """
    Analyzes the DataFrames and reports data quality issues.
    
    Args:
        dfs (Dict[str, pd.DataFrame]): Input DataFrames to profile.
        
    Returns:
        Dict[str, dict]: Mapping of table names to dictionaries of identified issues.
    """
    logger.info("Starting Data Quality Profiling...")
    report = {}
    now = pd.Timestamp.now()

    for name, df in dfs.items():
        if df.empty:
            logger.warning(f"Table '{name}' is empty.")
            continue

        issues = {
            "missing_values": {},
            "duplicates": 0,
            "negative_values": {},
            "future_dates": 0,
            "whitespace_issues": 0,
            "mixed_casing": {}
        }
        
        # Missing values (vectorized)
        null_counts = df.isnull().sum()
        for col, null_count in null_counts.items():
            if null_count > 0:
                issues["missing_values"][str(col)] = int(null_count)
                
        # Duplicates (vectorized)
        issues["duplicates"] = int(df.duplicated().sum())
        
        # Negative quantities / prices (vectorized)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                issues["negative_values"][str(col)] = int(neg_count)
                
        # Whitespace and Casing checks (vectorized)
        string_cols = df.select_dtypes(include=[object]).columns
        for col in string_cols:
            # Check for leading/trailing whitespaces
            ws_count = df[col].dropna().astype(str).str.contains(r"^\s+|\s+$", regex=True).sum()
            if ws_count > 0:
                issues["whitespace_issues"] += int(ws_count)
            
            # Check for casing consistency in categorical fields
            if col in ["category", "location", "customer_type", "status", "role"]:
                unique_vals = df[col].dropna().unique()
                unique_vals_lower = {v.lower().strip() for v in unique_vals}
                if len(unique_vals) != len(unique_vals_lower):
                    issues["mixed_casing"][str(col)] = list(unique_vals)

        # Future dates check
        date_cols = [c for c in df.columns if any(x in c for x in ["date", "updated", "timestamp", "generated", "created"])]
        for col in date_cols:
            try:
                dates = pd.to_datetime(df[col], errors="coerce")
                # Forecast dates can be in the future, so skip forecasts.forecast_date
                if not (name == "forecasts" and col == "forecast_date"):
                    future_count = (dates > now + pd.Timedelta(days=1)).sum()
                    if future_count > 0:
                        issues["future_dates"] += int(future_count)
            except Exception:
                pass
                
        report[name] = issues
        logger.debug(f"Data quality profile for '{name}': {issues}")
        
    logger.info("Data Quality Profiling completed.")
    return report

def cap_outliers_iqr(df: pd.DataFrame, col: str, multiplier: float = 1.5) -> Tuple[pd.DataFrame, int]:
    """
    Caps numeric values outside [Q1 - multiplier * IQR, Q3 + multiplier * IQR] bounds.
    Returns the modified DataFrame and count of capped records.
    """
    if col not in df.columns or len(df) == 0:
        return df, 0
    
    # Check if column is numeric
    if not pd.api.types.is_numeric_dtype(df[col]):
        return df, 0
        
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    # Track how many values will be capped
    under_mask = df[col] < lower_bound
    over_mask = df[col] > upper_bound
    cap_count = int(under_mask.sum() + over_mask.sum())
    
    if cap_count > 0:
        logger.info(f"Column '{col}': Capping {cap_count} outliers to IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]")
        # Cap values using np.clip
        df[col] = np.clip(df[col], lower_bound, upper_bound)
        
    return df, cap_count

def clean_dataset(dfs: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], dict]:
    """
    Cleans the operational DataFrames: removes duplicates, trims whitespaces, normalizes text,
    imputes missing data, handles outliers via IQR, and enforces referential integrity.
    Returns cleaned DataFrames dictionary and execution metrics.
    """
    logger.info("Starting Data Cleaning process...")
    settings = get_settings()
    cleaned_dfs = {}
    
    metrics = {
        "rows_removed": {},
        "rows_corrected": {},
        "duplicates_removed": {}
    }
    
    now = pd.Timestamp.now()
    iqr_mult = settings.outlier_iqr_multiplier

    # Step 1: Initialize Clean copies and perform local table cleaning
    for name, df_raw in dfs.items():
        df = df_raw.copy()
        initial_rows = len(df)
        
        # 1. Duplicate Removal
        df = df.drop_duplicates()
        dups_removed = initial_rows - len(df)
        metrics["duplicates_removed"][name] = dups_removed
        if dups_removed > 0:
            logger.info(f"Table '{name}': Removed {dups_removed} duplicate rows.")

        # 2. Trim string whitespace and normalize text
        string_cols = df.select_dtypes(include=[object]).columns
        for col in string_cols:
            # Use str.strip() to preserve NaNs without casting to string "nan"
            df[col] = df[col].astype(str).str.strip().replace({"nan": np.nan, "None": np.nan, "": np.nan})
            
            # Text normalization cases
            if col == "sku":
                df[col] = df[col].str.upper()
            elif col in ["category", "location", "customer_type", "status", "role"]:
                df[col] = df[col].str.title()
            elif "email" in col:
                df[col] = df[col].str.lower()
                
        # 3. Convert date columns to datetime
        date_cols = [c for c in df.columns if any(x in c for x in ["date", "updated", "timestamp", "generated", "created"])]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            
        # 4. Correct numerical types and enforce bounds
        if name == "products":
            df["category"] = df["category"].fillna("Other")
            df["name"] = df["name"].fillna("Unknown Product")
            df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(0.0)
            df["reorder_point"] = pd.to_numeric(df["reorder_point"], errors="coerce").fillna(10).astype(int)
            df = df[(df["unit_cost"] >= 0) & (df["reorder_point"] >= 0)]
            
        elif name == "inventory":
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
            df["location"] = df["location"].fillna("Warehouse-A")
            df = df[df["quantity"] >= 0]
            
        elif name == "sales":
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
            df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
            df["customer_type"] = df["customer_type"].fillna("Retail")
            
            df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)]
            
            # Outlier Handling
            df, cap_sales_qty = cap_outliers_iqr(df, "quantity", multiplier=iqr_mult)
            metrics["rows_corrected"]["sales_quantity_capped"] = cap_sales_qty
            
            # Remove sales dated in the future
            df = df[df["sale_date"] <= now + pd.Timedelta(days=1)]
            
        elif name == "suppliers":
            df["name"] = df["name"].fillna("Unknown Supplier")
            df["lead_time_days"] = pd.to_numeric(df["lead_time_days"], errors="coerce").fillna(
                settings.default_supplier_lead_time
            ).astype(int)
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(settings.default_supplier_rating)
            
            df = df[(df["lead_time_days"] >= 0) & (df["rating"] >= 0)]
            df["rating"] = np.clip(df["rating"], 0.0, 5.0)
            
            # Outlier Handling
            df, cap_lead = cap_outliers_iqr(df, "lead_time_days", multiplier=iqr_mult)
            metrics["rows_corrected"]["supplier_lead_time_capped"] = cap_lead
            
        elif name == "purchase_orders":
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
            df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(0.0)
            df["status"] = df["status"].fillna("Pending")
            
            df = df[(df["quantity"] > 0) & (df["unit_cost"] >= 0)]
            df = df[df["order_date"] <= now + pd.Timedelta(days=1)]
            
        elif name == "forecasts":
            df["predicted_qty"] = pd.to_numeric(df["predicted_qty"], errors="coerce").fillna(0.0)
            df["confidence_low"] = pd.to_numeric(df["confidence_low"], errors="coerce").fillna(0.0)
            df["confidence_high"] = pd.to_numeric(df["confidence_high"], errors="coerce").fillna(0.0)
            df = df[df["predicted_qty"] >= 0]
            
        elif name == "audit_logs":
            df["user_id"] = df["user_id"].fillna("system")
            df["action"] = df["action"].fillna("UNKNOWN")
            
        metrics["rows_removed"][name] = initial_rows - len(df)
        cleaned_dfs[name] = df

    # Step 2: Referential Integrity (ensure child tables reference existing parent keys)
    valid_prod_ids = set(cleaned_dfs["products"]["product_id"].unique())
    valid_supplier_ids = set(cleaned_dfs["suppliers"]["supplier_id"].unique())

    for table in ["inventory", "sales", "purchase_orders", "forecasts"]:
        if table in cleaned_dfs:
            df = cleaned_dfs[table]
            initial_len = len(df)
            df = df[df["product_id"].isin(valid_prod_ids)]
            removed_orphans = initial_len - len(df)
            if removed_orphans > 0:
                logger.warning(f"Table '{table}': Dropped {removed_orphans} orphan records violating product_id foreign key constraint.")
                metrics["rows_removed"][f"{table}_product_orphans"] = removed_orphans
            cleaned_dfs[table] = df

    if "purchase_orders" in cleaned_dfs:
        df = cleaned_dfs["purchase_orders"]
        initial_len = len(df)
        df = df[df["supplier_id"].isin(valid_supplier_ids)]
        removed_orphans = initial_len - len(df)
        if removed_orphans > 0:
            logger.warning(f"Table 'purchase_orders': Dropped {removed_orphans} orphan records violating supplier_id foreign key constraint.")
            metrics["rows_removed"]["purchase_orders_supplier_orphans"] = removed_orphans
        cleaned_dfs["purchase_orders"] = df

    # Step 3: Save cleaned datasets as CSVs
    cleaned_dir = os.path.join(settings.export_dir, "..", "cleaned")
    cleaned_dir = os.path.abspath(cleaned_dir)
    os.makedirs(cleaned_dir, exist_ok=True)
    
    for name, df in cleaned_dfs.items():
        export_df = df.copy()
        date_cols = [c for c in export_df.columns if any(x in c for x in ["date", "updated", "timestamp", "generated", "created"])]
        for col in date_cols:
            if col in ["sale_date", "forecast_date", "order_date", "expected_delivery", "actual_delivery"]:
                export_df[col] = export_df[col].dt.strftime("%Y-%m-%d")
            else:
                # Format to standard ISO string format
                export_df[col] = export_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3] + "Z"
                
        cleaned_csv_path = os.path.join(cleaned_dir, f"{name}.csv")
        export_df.to_csv(cleaned_csv_path, index=False, encoding="utf-8")
        logger.debug(f"Saved cleaned table to: {cleaned_csv_path}")

    logger.info("Data Cleaning process completed successfully.")
    return cleaned_dfs, metrics

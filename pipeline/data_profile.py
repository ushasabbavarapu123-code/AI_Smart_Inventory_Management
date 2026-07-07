import os
import sys
import pandas as pd
import numpy as np
from typing import Dict

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_settings

logger = setup_logger("profile")

def generate_profile_report(dfs: Dict[str, pd.DataFrame], output_path: str):
    """
    Generates a markdown data profiling report containing detailed summary statistics,
    cardinality, missing percentages, memory usage, and distribution analytics.
    """
    logger.info(f"Generating data quality and profiling report at {output_path}...")
    
    md = []
    md.append("# Data Profile Report")
    md.append(f"\n**Execution Timestamp:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append("\nThis document provides structural, statistical, and memory profiles of the operational datasets.\n")
    
    md.append("## 1. Executive Summary")
    md.append("High-level metrics across all tables:")
    md.append("\n| Table Name | Rows | Columns | Memory Usage (KB) | Duplicate % | Missing Values % |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    total_rows = 0
    total_mem = 0.0
    
    for name, df in sorted(dfs.items()):
        row_count = len(df)
        col_count = len(df.columns)
        mem_kb = df.memory_usage(deep=True).sum() / 1024
        dup_pct = (df.duplicated().sum() / row_count * 100) if row_count > 0 else 0.0
        missing_pct = (df.isnull().sum().sum() / (row_count * col_count) * 100) if (row_count * col_count) > 0 else 0.0
        
        md.append(f"| `{name}` | {row_count:,} | {col_count} | {mem_kb:.2f} KB | {dup_pct:.2f}% | {missing_pct:.2f}% |")
        total_rows += row_count
        total_mem += mem_kb
        
    md.append(f"| **Total / Summary** | **{total_rows:,}** | **N/A** | **{total_mem:.2f} KB** | **N/A** | **N/A** |\n")
    
    md.append("---")
    
    # Generate detailed reports table-by-table
    for name, df in sorted(dfs.items()):
        row_count = len(df)
        md.append(f"\n## Table Profile: `{name}`")
        md.append(f"Dimensions: {row_count:,} rows × {len(df.columns)} columns.\n")
        
        md.append("| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / row_count * 100) if row_count > 0 else 0.0
            
            unique_count = df[col].nunique()
            card_pct = (unique_count / row_count * 100) if row_count > 0 else 0.0
            
            # Numeric stats
            min_val, max_val, mean_val, std_val = "N/A", "N/A", "N/A", "N/A"
            if pd.api.types.is_numeric_dtype(df[col]) and not df[col].empty:
                valid_vals = df[col].dropna()
                if not valid_vals.empty:
                    min_val = f"{valid_vals.min():.2f}"
                    max_val = f"{valid_vals.max():.2f}"
                    mean_val = f"{valid_vals.mean():.2f}"
                    std_val = f"{valid_vals.std():.2f}" if len(valid_vals) > 1 else "0.00"
            elif pd.api.types.is_datetime64_any_dtype(df[col]) and not df[col].empty:
                valid_vals = df[col].dropna()
                if not valid_vals.empty:
                    min_val = valid_vals.min().strftime("%Y-%m-%d")
                    max_val = valid_vals.max().strftime("%Y-%m-%d")
            else:
                # Text/Boolean / non-numeric fallback
                valid_vals = df[col].dropna()
                if not valid_vals.empty:
                    sample = str(valid_vals.iloc[0])
                    if len(sample) > 20:
                        sample = sample[:17] + "..."
                    min_val = f"'{sample}'"
            
            md.append(f"| `{col}` | {dtype} | {null_count} ({null_pct:.1f}%) | {unique_count:,} | {card_pct:.1f}% | {min_val} | {max_val} | {mean_val} | {std_val} |")
        
        # Distribution Summary / Value counts for categorical columns (cardinality < 10)
        categorical_cols = [c for c in df.columns if df[c].nunique() < 10 and c != rule_pk_for_table(name)]
        if categorical_cols:
            md.append("\n### Categorical Value Distributions")
            for col in categorical_cols:
                v_counts = df[col].value_counts(dropna=False)
                counts_str = ", ".join([f"**{val}**: {cnt} ({cnt/row_count*100:.1f}%)" for val, cnt in v_counts.items()])
                md.append(f"- **{col}**: {counts_str}")
        md.append("\n---\n")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    logger.info(f"DATA_PROFILE_REPORT.md successfully written to: {output_path}")

def rule_pk_for_table(name: str) -> str:
    """Helper to return primary key name by table."""
    pk_map = {
        "products": "product_id",
        "inventory": "inventory_id",
        "sales": "sale_id",
        "suppliers": "supplier_id",
        "purchase_orders": "po_id",
        "forecasts": "forecast_id",
        "users": "user_id",
        "audit_logs": "log_id"
    }
    return pk_map.get(name, "")

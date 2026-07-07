import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger

logger = setup_logger("validate")

def validate_datasets(processed_dfs: Dict[str, pd.DataFrame]) -> dict:
    """
    Validates that the processed datasets meet all data integrity, relational, and business rules.
    Returns a summary report of the validation checks.
    """
    logger.info("Starting Data Validation phase...")
    
    validation_report = {
        "success": True,
        "tables": {}
    }
    
    now = pd.Timestamp.now()
    
    # ----------------------------------------------------
    # Table-specific Validation Rules
    # ----------------------------------------------------
    rules = {
        "products": {
            "pk": "product_id",
            "required": ["product_id", "sku", "name", "category", "unit_cost", "reorder_point"],
            "numeric_bounds": {
                "unit_cost": (0.0, float("inf")),
                "reorder_point": (0.0, float("inf"))
            }
        },
        "inventory": {
            "pk": "inventory_id",
            "required": ["inventory_id", "product_id", "quantity", "location"],
            "numeric_bounds": {
                "quantity": (0.0, float("inf")),
                "inventory_value": (0.0, float("inf"))
            }
        },
        "sales": {
            "pk": "sale_id",
            "required": ["sale_id", "product_id", "sale_date", "quantity", "unit_price"],
            "numeric_bounds": {
                "quantity": (1.0, float("inf")), # sales quantity must be > 0
                "unit_price": (0.0, float("inf")),
                "revenue": (0.0, float("inf")),
                "profit_margin": (-10.0, 1.0) # margin can be negative but should not exceed 1.0 (100%)
            }
        },
        "suppliers": {
            "pk": "supplier_id",
            "required": ["supplier_id", "name", "lead_time_days", "rating"],
            "numeric_bounds": {
                "lead_time_days": (0.0, 365.0), # cap lead time check at a year
                "rating": (0.0, 5.0) # ratings must be [0, 5]
            }
        },
        "purchase_orders": {
            "pk": "po_id",
            "required": ["po_id", "supplier_id", "product_id", "quantity", "unit_cost", "order_date", "status"],
            "numeric_bounds": {
                "quantity": (1.0, float("inf")),
                "unit_cost": (0.0, float("inf"))
            }
        },
        "forecasts": {
            "pk": "forecast_id",
            "required": ["forecast_id", "product_id", "forecast_date", "predicted_qty"],
            "numeric_bounds": {
                "predicted_qty": (0.0, float("inf")),
                "confidence_low": (0.0, float("inf")),
                "confidence_high": (0.0, float("inf"))
            }
        }
    }

    # Run validation checks
    for name, df in processed_dfs.items():
        if name not in rules:
            continue
            
        logger.info(f"Validating table '{name}'...")
        table_report = {
            "success": True,
            "row_count": len(df),
            "errors": [],
            "warnings": []
        }
        
        rule = rules[name]
        
        # 1. Primary Key Uniqueness
        pk = rule["pk"]
        if pk in df.columns:
            dups = df[pk].duplicated().sum()
            if dups > 0:
                table_report["success"] = False
                table_report["errors"].append(f"Primary key '{pk}' has {dups} duplicate records.")
        else:
            table_report["success"] = False
            table_report["errors"].append(f"Primary key column '{pk}' is missing.")
            
        # 2. Required Fields
        for col in rule["required"]:
            if col in df.columns:
                nulls = df[col].isnull().sum()
                if nulls > 0:
                    table_report["success"] = False
                    table_report["errors"].append(f"Required field '{col}' contains {nulls} null values.")
            else:
                table_report["success"] = False
                table_report["errors"].append(f"Required column '{col}' is missing.")
                
        # 3. Numeric Bounds
        for col, (min_val, max_val) in rule["numeric_bounds"].items():
            if col in df.columns:
                # Filter non-null values
                vals = df[col].dropna()
                out_of_bounds = ((vals < min_val) | (vals > max_val)).sum()
                if out_of_bounds > 0:
                    table_report["success"] = False
                    table_report["errors"].append(
                        f"Numeric column '{col}' has {out_of_bounds} values outside allowed range [{min_val}, {max_val}]."
                    )
                    
        # 4. Future Dates Validation
        date_cols = [c for c in df.columns if "date" in c or "updated" in c or "timestamp" in c or "generated" in c or "created" in c]
        for col in date_cols:
            if col in df.columns and not (name == "forecasts" and col == "forecast_date"):
                try:
                    dates = pd.to_datetime(df[col], errors="coerce")
                    future_dates = (dates > now + pd.Timedelta(days=1)).sum()
                    if future_dates > 0:
                        table_report["success"] = False
                        table_report["errors"].append(f"Date column '{col}' contains {future_dates} future dates.")
                except Exception as e:
                    table_report["warnings"].append(f"Could not parse dates in '{col}' for future validation: {e}")
                    
        # Store table validation status
        validation_report["tables"][name] = table_report
        if not table_report["success"]:
            validation_report["success"] = False
            logger.error(f"Table '{name}' validation failed. Errors: {table_report['errors']}")
        else:
            logger.info(f"Table '{name}' validation passed successfully.")

    # ----------------------------------------------------
    # 5. Referential Integrity (Foreign Keys)
    # ----------------------------------------------------
    logger.info("Verifying Referential Integrity...")
    ref_report = {
        "success": True,
        "errors": []
    }
    
    prod_ids = set(processed_dfs["products"]["product_id"].unique())
    supplier_ids = set(processed_dfs["suppliers"]["supplier_id"].unique())
    
    # Check inventory -> products
    inv_orphans = processed_dfs["inventory"][~processed_dfs["inventory"]["product_id"].isin(prod_ids)]
    if len(inv_orphans) > 0:
        ref_report["success"] = False
        ref_report["errors"].append(f"Inventory table contains {len(inv_orphans)} orphan product_id references.")
        
    # Check sales -> products
    sales_orphans = processed_dfs["sales"][~processed_dfs["sales"]["product_id"].isin(prod_ids)]
    if len(sales_orphans) > 0:
        ref_report["success"] = False
        ref_report["errors"].append(f"Sales table contains {len(sales_orphans)} orphan product_id references.")
        
    # Check purchase orders -> products
    po_prod_orphans = processed_dfs["purchase_orders"][~processed_dfs["purchase_orders"]["product_id"].isin(prod_ids)]
    if len(po_prod_orphans) > 0:
        ref_report["success"] = False
        ref_report["errors"].append(f"Purchase orders contain {len(po_prod_orphans)} orphan product_id references.")
        
    # Check purchase orders -> suppliers
    po_sup_orphans = processed_dfs["purchase_orders"][~processed_dfs["purchase_orders"]["supplier_id"].isin(supplier_ids)]
    if len(po_sup_orphans) > 0:
        ref_report["success"] = False
        ref_report["errors"].append(f"Purchase orders contain {len(po_sup_orphans)} orphan supplier_id references.")
        
    validation_report["referential_integrity"] = ref_report
    if not ref_report["success"]:
        validation_report["success"] = False
        logger.error(f"Referential integrity checks failed. Errors: {ref_report['errors']}")
    else:
        logger.info("Referential integrity checks passed successfully.")
        
    validation_report["status"] = "PASSED" if validation_report["success"] else "FAILED"
    logger.info(f"Data Validation completed. Global Status: {validation_report['status']}")
    
    return validation_report

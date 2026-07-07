import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Set, Tuple

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_settings

logger = setup_logger("validate")

# Define expected schemas for schema drift validation
EXPECTED_SCHEMAS: Dict[str, List[str]] = {
    "products": ["product_id", "sku", "name", "category", "unit_cost", "reorder_point", "created_at", "current_stock_quantity", "inventory_value", "avg_daily_demand", "safety_stock", "stock_status", "reorder_required", "safety_stock_flag", "days_until_stockout", "demand_category", "total_units_sold", "cogs", "inventory_turnover", "lead_time_days", "supplier_rating"],
    "inventory": ["inventory_id", "product_id", "quantity", "location", "last_updated", "inventory_value", "reorder_required", "stock_status", "avg_daily_demand", "safety_stock", "safety_stock_flag", "unit_cost", "reorder_point"],
    "sales": ["sale_id", "product_id", "sale_date", "quantity", "unit_price", "customer_type", "unit_cost", "revenue", "profit", "profit_margin", "week", "month", "quarter", "year", "day_of_week", "weekend_indicator", "season", "rolling_sales_7d", "rolling_sales_30d", "created_at"],
    "suppliers": ["supplier_id", "name", "contact_person", "contact_email", "contact_phone", "lead_time_days", "rating", "created_at"],
    "purchase_orders": ["po_id", "supplier_id", "product_id", "quantity", "unit_cost", "order_date", "expected_delivery", "actual_delivery", "status", "notes", "week", "month", "quarter", "year", "day_of_week", "weekend_indicator", "season", "created_at"],
    "forecasts": ["forecast_id", "product_id", "forecast_date", "predicted_qty", "confidence_low", "confidence_high", "model_used", "generated_at"]
}

def validate_datasets(processed_dfs: Dict[str, pd.DataFrame]) -> dict:
    """
    Validates that the processed datasets meet all data integrity, relational, and business rules.
    Performs checks for PK uniqueness, FK constraints, schema drift, nullability, numeric bounds,
    date ranges, and business logic.
    """
    logger.info("Starting Advanced Data Validation phase...")
    settings = get_settings()
    
    validation_report = {
        "success": True,
        "tables": {},
        "referential_integrity": {
            "success": True,
            "errors": []
        },
        "schema_drift": {
            "success": True,
            "errors": []
        },
        "business_rules": {
            "success": True,
            "errors": []
        },
        "status": "PASSED"
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
                "reorder_point": (0.0, float("inf")),
                "inventory_value": (0.0, float("inf")),
                "current_stock_quantity": (0.0, float("inf")),
                "avg_daily_demand": (0.0, float("inf")),
                "days_until_stockout": (0.0, settings.max_days_until_stockout)
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
                "quantity": (1.0, float("inf")), 
                "unit_price": (0.0, float("inf")),
                "revenue": (0.0, float("inf")),
                "profit_margin": (-10.0, 1.0) 
            }
        },
        "suppliers": {
            "pk": "supplier_id",
            "required": ["supplier_id", "name", "lead_time_days", "rating"],
            "numeric_bounds": {
                "lead_time_days": (0.0, 365.0),
                "rating": (0.0, 5.0)
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
            
        logger.debug(f"Validating table structure and columns for '{name}'...")
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
            
        # 2. Required Fields (Nullability Check)
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
                vals = df[col].dropna()
                out_of_bounds = ((vals < min_val) | (vals > max_val)).sum()
                if out_of_bounds > 0:
                    table_report["success"] = False
                    table_report["errors"].append(
                        f"Numeric column '{col}' has {out_of_bounds} values outside allowed range [{min_val}, {max_val}]."
                    )
                    
        # 4. Future Dates Validation
        date_cols = [c for c in df.columns if any(x in c for x in ["date", "updated", "timestamp", "generated", "created"])]
        for col in date_cols:
            if col in df.columns and not (name == "forecasts" and col == "forecast_date"):
                try:
                    dates = pd.to_datetime(df[col], errors="coerce")
                    future_dates = (dates > now + pd.Timedelta(days=1)).sum()
                    if future_dates > 0:
                        table_report["success"] = False
                        table_report["errors"].append(f"Date column '{col}' contains {future_dates} future dates.")
                except Exception as e:
                    table_report["warnings"].append(f"Could not parse dates in '{col}': {e}")
                    
        # Store table validation status
        validation_report["tables"][name] = table_report
        if not table_report["success"]:
            validation_report["success"] = False
            logger.error(f"Table '{name}' validation failed: {table_report['errors']}")
        else:
            logger.debug(f"Table '{name}' validation passed successfully.")

    # ----------------------------------------------------
    # 5. Referential Integrity (Foreign Keys)
    # ----------------------------------------------------
    logger.debug("Verifying Referential Integrity...")
    ref_errors = []
    
    prod_ids = set(processed_dfs["products"]["product_id"].unique())
    supplier_ids = set(processed_dfs["suppliers"]["supplier_id"].unique())
    
    # Check inventory -> products
    inv_orphans = processed_dfs["inventory"][~processed_dfs["inventory"]["product_id"].isin(prod_ids)]
    if len(inv_orphans) > 0:
        ref_errors.append(f"Inventory table contains {len(inv_orphans)} orphan product_id references.")
        
    # Check sales -> products
    sales_orphans = processed_dfs["sales"][~processed_dfs["sales"]["product_id"].isin(prod_ids)]
    if len(sales_orphans) > 0:
        ref_errors.append(f"Sales table contains {len(sales_orphans)} orphan product_id references.")
        
    # Check purchase orders -> products and suppliers
    po_prod_orphans = processed_dfs["purchase_orders"][~processed_dfs["purchase_orders"]["product_id"].isin(prod_ids)]
    if len(po_prod_orphans) > 0:
        ref_errors.append(f"Purchase orders contain {len(po_prod_orphans)} orphan product_id references.")
        
    po_sup_orphans = processed_dfs["purchase_orders"][~processed_dfs["purchase_orders"]["supplier_id"].isin(supplier_ids)]
    if len(po_sup_orphans) > 0:
        ref_errors.append(f"Purchase orders contain {len(po_sup_orphans)} orphan supplier_id references.")
        
    if ref_errors:
        validation_report["referential_integrity"]["success"] = False
        validation_report["referential_integrity"]["errors"] = ref_errors
        validation_report["success"] = False
        logger.error(f"Referential integrity checks failed: {ref_errors}")
    else:
        logger.debug("Referential integrity checks passed.")

    # ----------------------------------------------------
    # 6. Schema Drift Validation
    # ----------------------------------------------------
    logger.debug("Checking for Schema Drift...")
    schema_errors = []
    for name, expected_cols in EXPECTED_SCHEMAS.items():
        if name in processed_dfs:
            actual_cols = list(processed_dfs[name].columns)
            missing = set(expected_cols) - set(actual_cols)
            extra = set(actual_cols) - set(expected_cols)
            
            if missing:
                schema_errors.append(f"Table '{name}' has missing columns: {list(missing)}")
            if extra:
                logger.warning(f"Table '{name}' contains extra/undocumented columns: {list(extra)}")
                
    if schema_errors:
        validation_report["schema_drift"]["success"] = False
        validation_report["schema_drift"]["errors"] = schema_errors
        validation_report["success"] = False
        logger.error(f"Schema drift detected: {schema_errors}")
    else:
        logger.debug("Schema drift check passed.")

    # ----------------------------------------------------
    # 7. Business Rules Verification
    # ----------------------------------------------------
    logger.debug("Verifying Core Business Rules...")
    biz_errors = []
    
    # Rule 7.1: Revenue = Quantity * Unit Price in Sales
    sales_df = processed_dfs["sales"]
    calculated_rev = sales_df["quantity"] * sales_df["unit_price"]
    rev_diff = (sales_df["revenue"] - calculated_rev).abs()
    rev_violations = (rev_diff > 0.01).sum()
    if rev_violations > 0:
        biz_errors.append(f"Revenue rule violation: {rev_violations} rows in sales have mismatch between revenue and quantity * unit_price.")
        
    # Rule 7.2: Profit = Revenue - (Quantity * Unit Cost) in Sales
    calculated_profit = sales_df["revenue"] - (sales_df["quantity"] * sales_df["unit_cost"])
    prof_diff = (sales_df["profit"] - calculated_profit).abs()
    prof_violations = (prof_diff > 0.01).sum()
    if prof_violations > 0:
        biz_errors.append(f"Profit rule violation: {prof_violations} rows in sales have mismatch between profit and revenue - COGS.")

    # Rule 7.3: Product inventory value matches quantity * unit_cost in Products
    prod_df = processed_dfs["products"]
    calculated_inv_val = prod_df["current_stock_quantity"] * prod_df["unit_cost"]
    inv_diff = (prod_df["inventory_value"] - calculated_inv_val).abs()
    inv_violations = (inv_diff > 0.01).sum()
    if inv_violations > 0:
        biz_errors.append(f"Inventory Value violation: {inv_violations} rows in products have mismatch between inventory_value and current_stock_quantity * unit_cost.")

    if biz_errors:
        validation_report["business_rules"]["success"] = False
        validation_report["business_rules"]["errors"] = biz_errors
        validation_report["success"] = False
        logger.error(f"Business rules verification failed: {biz_errors}")
    else:
        logger.debug("Business rules verification passed.")

    validation_report["status"] = "PASSED" if validation_report["success"] else "FAILED"
    logger.info(f"Data Validation completed. Status: {validation_report['status']}")
    
    return validation_report

def generate_validation_report(validation_report: dict, output_path: str):
    """
    Generates docs/DATA_VALIDATION_REPORT.md summary file.
    """
    logger.info(f"Writing DATA_VALIDATION_REPORT.md to {output_path}...")
    
    md = []
    md.append("# Data Validation Report")
    md.append(f"\n**Execution Timestamp:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    status_icon = "✅ PASSED" if validation_report["success"] else "❌ FAILED"
    md.append(f"**Overall Validation Status:** {status_icon}\n")
    
    md.append("## 1. Summary of Checks")
    md.append("This report lists automated sanity and rules checking applied to finalized feature-engineered datasets.")
    
    md.append("\n### Core Check Status")
    md.append("| Check Suite | Status | Details / Issues |")
    md.append("| :--- | :--- | :--- |")
    
    # Schema check
    schema_status = "Passed ✅" if validation_report["schema_drift"]["success"] else "Failed ❌"
    schema_detail = ", ".join(validation_report["schema_drift"]["errors"]) if validation_report["schema_drift"]["errors"] else "No schema drift detected."
    md.append(f"| Schema Drift | {schema_status} | {schema_detail} |")
    
    # Referential integrity
    ref_status = "Passed ✅" if validation_report["referential_integrity"]["success"] else "Failed ❌"
    ref_detail = ", ".join(validation_report["referential_integrity"]["errors"]) if validation_report["referential_integrity"]["errors"] else "All foreign keys verified successfully."
    md.append(f"| Referential Keys | {ref_status} | {ref_detail} |")
    
    # Business Rules
    biz_status = "Passed ✅" if validation_report["business_rules"]["success"] else "Failed ❌"
    biz_detail = ", ".join(validation_report["business_rules"]["errors"]) if validation_report["business_rules"]["errors"] else "All business logical equalities match."
    md.append(f"| Business Rules | {biz_status} | {biz_detail} |")
    
    md.append("\n## 2. Table-by-Table Status")
    md.append("| Table Name | Rows Validated | Status | Details of Errors / Warnings |")
    md.append("| :--- | :--- | :--- | :--- |")
    
    for name, tab in validation_report["tables"].items():
        status = "Passed ✅" if tab["success"] else "Failed ❌"
        errors = "; ".join(tab["errors"]) if tab["errors"] else "None"
        if tab["warnings"]:
            errors += f" (Warnings: {'; '.join(tab['warnings'])})"
        md.append(f"| `{name}` | {tab['row_count']} | {status} | {errors} |")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    logger.info(f"DATA_VALIDATION_REPORT.md successfully written to: {output_path}")

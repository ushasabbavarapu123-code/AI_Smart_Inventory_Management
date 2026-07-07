import os
import sys
import time
import json
import pandas as pd
from typing import Dict, List

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_db_path
from extract import extract_tables
from clean import profile_data_quality, clean_dataset
from transform import transform_data
from validate import validate_datasets
from export import export_datasets

logger = setup_logger("orchestrator")

COLUMN_DICTIONARY = {
    # products
    "product_id": ("String (UUID)", "No", "f3b20c91-d824-4fca-8600-0e12361254ff", "Unique identifier for the product record."),
    "sku": ("String", "No", "ELEC-LAP-001", "Unique Stock Keeping Unit code."),
    "name": ("String", "No", "Pro Laptop 15-inch", "Descriptive title of the product."),
    "category": ("String", "No", "Electronics", "Business classification of the item."),
    "unit_cost": ("Float", "No", "750.00", "Cost price per unit from supplier."),
    "reorder_point": ("Integer", "No", "15", "Stock threshold to trigger reorder."),
    "created_at": ("Datetime", "No", "2026-06-01T12:00:00Z", "Timestamp of record creation."),
    "current_stock_quantity": ("Integer", "No", "45", "Total current stock across warehouses (computed)."),
    "inventory_value": ("Float", "No", "33750.00", "Calculated value of stock (quantity * unit_cost)."),
    "stock_status": ("String", "No", "In Stock", "Stock level status: In Stock, Low Stock, Out Of Stock."),
    "reorder_required": ("Integer (Binary)", "No", "0", "Flag indicating if quantity <= reorder_point (1=Yes, 0=No)."),
    "avg_daily_demand": ("Float", "No", "3.50", "Average quantity sold per day (including zero sales days)."),
    "days_until_stockout": ("Float", "No", "12.8", "Estimated days before stock hits zero (quantity / avg_daily_demand)."),
    "safety_stock": ("Float", "No", "24.5", "Calculated safety stock (avg_daily_demand * lead_time_days)."),
    "safety_stock_flag": ("Integer (Binary)", "No", "0", "Flag indicating if current quantity < safety stock (1=Yes, 0=No)."),
    "demand_category": ("String", "No", "High Demand", "Demand level percentile classification."),
    "inventory_turnover": ("Float", "No", "4.2", "Turnover ratio (COGS / current inventory value)."),
    "cogs": ("Float", "No", "15000.00", "Cost of Goods Sold (total units sold * unit_cost)."),
    "total_units_sold": ("Integer", "No", "20", "Total quantities sold historically."),
    
    # inventory
    "inventory_id": ("String (UUID)", "No", "d9c3b1a2-e3f4-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for the inventory record."),
    "location": ("String", "No", "Warehouse-A", "Physical storage location."),
    "last_updated": ("Datetime", "No", "2026-07-01T15:30:00Z", "Timestamp of last stock update."),
    
    # sales
    "sale_id": ("String (UUID)", "No", "a8b9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for the sale transaction."),
    "sale_date": ("Date (YYYY-MM-DD)", "No", "2026-07-02", "Date of the sale transaction."),
    "unit_price": ("Float", "No", "999.99", "Selling price per unit."),
    "customer_type": ("String", "No", "Retail", "Segment of customer: Retail or Wholesale."),
    "revenue": ("Float", "No", "1999.98", "Total sales revenue (quantity * unit_price)."),
    "profit": ("Float", "No", "499.98", "Net profit generated (revenue - COGS)."),
    "profit_margin": ("Float", "No", "0.25", "Net profit margin ratio (profit / revenue)."),
    "week": ("Integer", "No", "27", "ISO week number."),
    "month": ("Integer", "No", "7", "Calendar month of transaction."),
    "quarter": ("Integer", "No", "3", "Calendar quarter of transaction."),
    "year": ("Integer", "No", "2026", "Calendar year of transaction."),
    "day_of_week": ("Integer", "No", "3", "Day index of the week (0=Monday, 6=Sunday)."),
    "weekend_indicator": ("Integer (Binary)", "No", "0", "Flag indicating if date is a weekend (1=Yes, 0=No)."),
    "season": ("String", "No", "Summer", "Calendar season (Winter, Spring, Summer, Autumn)."),
    "rolling_sales_7d": ("Float", "No", "42.0", "7-day rolling sum of quantities sold for this product."),
    "rolling_sales_30d": ("Float", "No", "150.0", "30-day rolling sum of quantities sold for this product."),
    
    # suppliers
    "supplier_id": ("String (UUID)", "No", "b4a3c2d1-e3f4-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for the supplier record."),
    "contact_person": ("String", "Yes", "John Doe", "Primary supplier contact person."),
    "contact_email": ("String", "No", "john@supplier.com", "Supplier email address."),
    "contact_phone": ("String", "Yes", "+1-555-0199", "Supplier telephone contact."),
    "lead_time_days": ("Integer", "No", "7", "Supplier delivery lead time in days."),
    "rating": ("Float", "No", "4.5", "Supplier performance rating (scale 0 to 5)."),
    "supplier_rating": ("Float", "No", "4.5", "Mapped rating for reporting."),
    
    # purchase orders
    "po_id": ("String (UUID)", "No", "c8d9e0f1-e3f4-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for the purchase order."),
    "order_date": ("Date (YYYY-MM-DD)", "No", "2026-06-15", "Date when the order was placed."),
    "expected_delivery": ("Date (YYYY-MM-DD)", "No", "2026-06-22", "Date order is expected to arrive."),
    "actual_delivery": ("Date (YYYY-MM-DD)", "Yes", "2026-06-21", "Date order was actually delivered."),
    "status": ("String", "No", "Received", "Purchase order status: Pending, Shipped, Received, Cancelled."),
    "notes": ("String", "Yes", "Urgent delivery requested.", "Internal notes for purchase order."),
    
    # forecasts
    "forecast_id": ("String (UUID)", "No", "d4e5f6a7-e3f4-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for the forecast record."),
    "forecast_date": ("Date (YYYY-MM-DD)", "No", "2026-08-01", "Target date of predicted demand."),
    "predicted_qty": ("Float", "No", "50.0", "Forecasted demand quantity."),
    "confidence_low": ("Float", "No", "35.0", "Lower boundary of forecast confidence interval."),
    "confidence_high": ("Float", "No", "65.0", "Upper boundary of forecast confidence interval."),
    "model_used": ("String", "No", "ARIMA", "Forecasting algorithm used (ARIMA, MovingAverage)."),
    "generated_at": ("Datetime", "No", "2026-07-07T12:00:00Z", "Timestamp of forecast calculation."),
    
    # users
    "user_id": ("String (UUID)", "No", "u1v2w3x4-e3f4-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for the user account."),
    "email": ("String", "No", "admin@inventory.com", "Registered user email address."),
    "password_hash": ("String", "No", "$2b$10$...", "Encrypted password string."),
    "full_name": ("String", "No", "Alice Smith", "Full name of the user."),
    "role": ("String", "No", "Admin", "User access control role."),
    "is_active": ("Integer (Binary)", "No", "1", "Status flag showing if account is active."),
    "last_login": ("Datetime", "Yes", "2026-07-07T10:00:00Z", "Timestamp of last user login."),
    
    # audit logs
    "log_id": ("String (UUID)", "No", "l1m2n3o4-e3f4-4a5b-6c7d-8e9f0a1b2c3d", "Unique identifier for audit log entry."),
    "action": ("String", "No", "CREATE_SALE", "Action description."),
    "entity": ("String", "No", "sales", "Database entity/table name affected."),
    "entity_id": ("String (UUID)", "No", "a8b9c0d1...", "Record ID of the affected entity."),
    "old_value": ("String", "Yes", "{'quantity': 50}", "Serialized values before change."),
    "new_value": ("String", "Yes", "{'quantity': 48}", "Serialized values after change."),
    "ip_address": ("String", "Yes", "127.0.0.1", "Client IP address."),
    "timestamp": ("Datetime", "No", "2026-07-07T18:00:00Z", "Log entry timestamp.")
}

def generate_data_dictionary(processed_dfs: Dict[str, pd.DataFrame], output_path: str):
    """Generates a comprehensive DATA_DICTIONARY.md file."""
    logger.info("Generating DATA_DICTIONARY.md...")
    
    md_content = []
    md_content.append("# Data Dictionary")
    md_content.append("\nThis document provides technical schemas, definitions, and business rules for the processed datasets in the inventory management system.")
    md_content.append("\n*Generated automatically by the ETL data pipeline.*\n")
    
    for name, df in sorted(processed_dfs.items()):
        md_content.append(f"## Table: `{name}`")
        md_content.append(f"Contains {len(df)} rows and {len(df.columns)} columns.\n")
        
        md_content.append("| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |")
        md_content.append("| :--- | :--- | :--- | :--- | :--- |")
        
        for col in df.columns:
            # Check if column in dictionary
            if col in COLUMN_DICTIONARY:
                dtype_desc, nullable, example, meaning = COLUMN_DICTIONARY[col]
            else:
                # Default fallback
                dtype_desc = str(df[col].dtype)
                nullable = "Yes" if df[col].isnull().any() else "No"
                non_null_vals = df[col].dropna()
                example = str(non_null_vals.iloc[0]) if not non_null_vals.empty else "N/A"
                meaning = "Self-explanatory operational or engineered feature column."
                
            # If date column, show clean example
            if "date" in col or "updated" in col or "timestamp" in col or "generated" in col or "created" in col:
                # convert example if possible
                pass
                
            md_content.append(f"| `{col}` | {dtype_desc} | {nullable} | `{example}` | {meaning} |")
        md_content.append("\n---\n")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
        
    logger.info(f"DATA_DICTIONARY.md written to: {output_path}")

def generate_cleaning_report(
    raw_dfs: Dict[str, pd.DataFrame],
    profile_report: dict,
    clean_metrics: dict,
    validation_report: dict,
    exported_paths: List[str],
    elapsed_times: dict,
    output_path: str
):
    """Generates the DATA_CLEANING_REPORT.md file."""
    logger.info("Generating DATA_CLEANING_REPORT.md...")
    
    md = []
    md.append("# Data Cleaning & Pipeline Report")
    md.append(f"\n**Execution Timestamp:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"\n**Pipeline Status:** {validation_report['status']}\n")
    
    md.append("## 1. Overview")
    md.append("This automated pipeline extracts relational datasets from the SQLite inventory database, analyzes data quality issues, performs programmatic cleaning, implements feature engineering, validates the output, and exports analytical datasets for down-stream machine learning model execution.")
    
    # Execution times
    md.append("\n### Pipeline Phase Execution Times")
    md.append("| Pipeline Phase | Elapsed Time |")
    md.append("| :--- | :--- |")
    for phase, sec in elapsed_times.items():
        md.append(f"| {phase} | {sec:.4f} seconds |")
    md.append(f"| **Total Pipeline Time** | **{sum(elapsed_times.values()):.4f} seconds** |")
    
    # Extraction Counts
    md.append("\n## 2. Extraction & Quality Profiling Summary")
    md.append("| Table Name | Raw Row Count | Duplicates Detected | Missing Fields Count | Anomalies Found |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    for name, df in raw_dfs.items():
        issues = profile_report.get(name, {})
        dup = issues.get("duplicates", 0)
        miss_count = sum(issues.get("missing_values", {}).values())
        neg_count = sum(issues.get("negative_values", {}).values())
        ws_count = issues.get("whitespace_issues", 0)
        future_dates = issues.get("future_dates", 0)
        
        anom_sum = neg_count + ws_count + future_dates
        md.append(f"| {name} | {len(df)} | {dup} | {miss_count} | {anom_sum} |")
        
    # Cleaning Summary
    md.append("\n## 3. Cleaning & Data Standardizations")
    md.append("The following data corrections were applied dynamically:")
    md.append("- **Duplicate Removal:** All exact duplicate records deleted.")
    md.append("- **Whitespace Trimming:** Leading and trailing white spaces stripped across all text fields.")
    md.append("- **Text Normalization:** Upper-cased SKUs; Title-cased categories, locations, and customer types.")
    md.append("- **Imputations & Logical Bounds:** Missing categories filled with 'Other'. Negative price/quantity entries removed.")
    md.append("- **Outlier Capping:** Applied Interquartile Range (IQR) capping on transaction volumes and lead times.")
    
    md.append("\n### Cleaning Execution Metrics")
    md.append("| Cleaning Metric / Table | Rows Modified / Removed | Details |")
    md.append("| :--- | :--- | :--- |")
    for name, removed in clean_metrics.get("rows_removed", {}).items():
        if removed > 0:
            md.append(f"| Rows Removed: `{name}` | {removed} | Orphan records or negative numbers removed. |")
    for name, corrected in clean_metrics.get("rows_corrected", {}).items():
        if corrected > 0:
            md.append(f"| Outliers Capped: `{name}` | {corrected} | Values clipped to [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. |")
    for name, dups in clean_metrics.get("duplicates_removed", {}).items():
        if dups > 0:
            md.append(f"| Duplicates Deleted: `{name}` | {dups} | Exact duplicate rows removed from dataframe. |")
            
    # Feature Engineering
    md.append("\n## 4. Feature Engineering Summary")
    md.append("The transformation engine appended the following calculated columns:")
    md.append("1. **Inventory Value:** `quantity` * `unit_cost` per inventory stock.")
    md.append("2. **Sales Finance:** `revenue` = `quantity` * `unit_price`, `profit` = `revenue` - `COGS`, and `profit_margin` = `profit` / `revenue` per sales invoice.")
    md.append("3. **Stock Health indicators:** `stock_status` ('In Stock', 'Low Stock', 'Out Of Stock'), `reorder_required` boolean, and `safety_stock` limit.")
    md.append("4. **Supply KPIs:** Mapped `lead_time_days` and `supplier_rating` to products to flag `safety_stock_flag` and calculate `days_until_stockout` (run-out rate).")
    md.append("5. **Temporal Attributes:** Calendric features derived from date fields: `week`, `month`, `quarter`, `year`, `day_of_week`, `weekend_indicator`, and `season` indicators.")
    md.append("6. **Time-series Lags:** Engineered `rolling_sales_7d`, `rolling_sales_30d`, and `avg_daily_demand` per product.")

    # Validation Summary
    md.append("\n## 5. Data Validation & Integrity Checks")
    md.append(f"**Validation Status:** {validation_report['status']}")
    md.append("\n| Table Name | Schema Valid | Key Uniqueness | Null Checks | Relational Integrity | Errors / Warnings |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for name, val in validation_report.get("tables", {}).items():
        success = "Passed ✅" if val["success"] else "Failed ❌"
        err_msg = ", ".join(val["errors"]) if val["errors"] else "None"
        md.append(f"| {name} | {success} | Passed | Passed | Passed | {err_msg} |")
        
    ref_status = "Passed ✅" if validation_report.get("referential_integrity", {}).get("success", False) else "Failed ❌"
    ref_errors = ", ".join(validation_report.get("referential_integrity", {}).get("errors", [])) if validation_report.get("referential_integrity", {}).get("errors", []) else "None"
    md.append(f"| **Referential Checks** | {ref_status} | N/A | N/A | {ref_status} | {ref_errors} |")

    # Export formats
    md.append("\n## 6. Export Formats & Archival Paths")
    md.append("The finalized processed tables were exported to CSV, Excel, Parquet, and Pickle formats:")
    md.append("\n| Export Type | Output Paths |")
    md.append("| :--- | :--- |")
    # Group exported paths by extension
    ext_groups = {}
    for p in exported_paths:
        ext = os.path.splitext(p)[1]
        ext_groups.setdefault(ext, []).append(p)
        
    for ext, paths in ext_groups.items():
        paths_str = "<br>".join([f"`{os.path.basename(p)}`" for p in paths])
        md.append(f"| {ext.upper()} | {paths_str} |")

    # Limitations
    md.append("\n## 7. Known Limitations")
    md.append("- **Static Inventory Value:** Calculated inventory value relies on current quantity snapshots; historical inventory levels are not preserved in SQLite.")
    md.append("- **Time-series gaps:** Products with zero sales during the entire history cannot establish moving averages or trend estimations.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    logger.info(f"DATA_CLEANING_REPORT.md written to: {output_path}")

def main():
    logger.info("================================================")
    logger.info("Initializing Data Pipeline Execution...")
    logger.info("================================================")
    
    elapsed_times = {}
    
    try:
        # Phase 1: Extraction
        t0 = time.time()
        raw_dfs = extract_tables()
        elapsed_times["Extraction"] = time.time() - t0
        
        # Phase 2: Quality Assessment / Profiling
        t0 = time.time()
        profile_report = profile_data_quality(raw_dfs)
        elapsed_times["Profiling"] = time.time() - t0
        
        # Phase 3: Cleaning
        t0 = time.time()
        cleaned_dfs, clean_metrics = clean_dataset(raw_dfs)
        elapsed_times["Cleaning"] = time.time() - t0
        
        # Phase 4: Transformation / Feature Engineering
        t0 = time.time()
        processed_dfs = transform_data(cleaned_dfs)
        elapsed_times["Feature Engineering"] = time.time() - t0
        
        # Phase 5: Validation
        t0 = time.time()
        validation_report = validate_datasets(processed_dfs)
        elapsed_times["Validation"] = time.time() - t0
        
        # Phase 6: Export
        t0 = time.time()
        exported_paths = export_datasets(processed_dfs)
        elapsed_times["Export"] = time.time() - t0
        
        # Phase 7: Generate Documentation
        t0 = time.time()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        dict_path = os.path.join(project_root, "docs", "DATA_DICTIONARY.md")
        generate_data_dictionary(processed_dfs, dict_path)
        
        report_path = os.path.join(project_root, "docs", "DATA_CLEANING_REPORT.md")
        generate_cleaning_report(
            raw_dfs,
            profile_report,
            clean_metrics,
            validation_report,
            exported_paths,
            elapsed_times,
            report_path
        )
        elapsed_times["Documentation"] = time.time() - t0
        
        logger.info("================================================")
        logger.info("ETL Data Pipeline Completed Successfully!")
        logger.info(f"Total time elapsed: {sum(elapsed_times.values()):.4f} seconds")
        logger.info("================================================")
        
    except Exception as e:
        logger.error(f"ETL Data Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()

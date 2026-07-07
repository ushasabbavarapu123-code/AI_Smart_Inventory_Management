import os
import sys
import pandas as pd
import numpy as np
from typing import Dict

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_settings

logger = setup_logger("transform")

# Vectorized season mapping dictionary
MONTH_TO_SEASON = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn"
}

def transform_data(cleaned_dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Applies feature engineering to the cleaned operational dataframes.
    Enriches products, sales, and inventory tables with calculated business metrics.
    
    Args:
        cleaned_dfs (Dict[str, pd.DataFrame]): Input cleaned DataFrames.
        
    Returns:
        Dict[str, pd.DataFrame]: Enriched and transformed DataFrames.
    """
    logger.info("Starting Feature Engineering & Transformation...")
    settings = get_settings()
    
    # 0. Fast local copies to avoid side effects
    products = cleaned_dfs["products"].copy()
    inventory = cleaned_dfs["inventory"].copy()
    sales = cleaned_dfs["sales"].copy()
    suppliers = cleaned_dfs["suppliers"].copy()
    purchase_orders = cleaned_dfs["purchase_orders"].copy()
    forecasts = cleaned_dfs["forecasts"].copy()
    audit_logs = cleaned_dfs["audit_logs"].copy()
    
    # Ensure dates are datetime objects
    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    purchase_orders["order_date"] = pd.to_datetime(purchase_orders["order_date"])
    if "expected_delivery" in purchase_orders.columns:
        purchase_orders["expected_delivery"] = pd.to_datetime(purchase_orders["expected_delivery"])
    if "actual_delivery" in purchase_orders.columns:
        purchase_orders["actual_delivery"] = pd.to_datetime(purchase_orders["actual_delivery"])

    # ----------------------------------------------------
    # 1. PRE-COMPUTATIONS (Daily Sales Time Series & Demand)
    # ----------------------------------------------------
    # Find complete range of sales dates
    min_date = sales["sale_date"].min()
    max_date = sales["sale_date"].max()
    logger.info(f"Historical sales date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    
    # Create complete date index
    all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
    product_ids = products["product_id"].unique()
    
    # Build complete grid of Date x Product
    grid = pd.MultiIndex.from_product([all_dates, product_ids], names=["sale_date", "product_id"]).to_frame().reset_index(drop=True)
    
    # Group actual sales daily by product
    sales_daily = sales.groupby(["sale_date", "product_id"])["quantity"].sum().reset_index()
    
    # Merge grid with daily sales
    grid_sales = pd.merge(grid, sales_daily, on=["sale_date", "product_id"], how="left").fillna(0)
    grid_sales = grid_sales.sort_values(by=["product_id", "sale_date"]).reset_index(drop=True)
    
    # Calculate Rolling Sales (7-day and 30-day) on daily grid
    logger.info("Calculating rolling sales (7-day and 30-day)...")
    grid_sales["rolling_sales_7d"] = grid_sales.groupby("product_id")["quantity"].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum()
    )
    grid_sales["rolling_sales_30d"] = grid_sales.groupby("product_id")["quantity"].transform(
        lambda x: x.rolling(window=30, min_periods=1).sum()
    )
    
    # Calculate Average Daily Demand per product
    avg_daily_demand = grid_sales.groupby("product_id")["quantity"].mean().reset_index(name="avg_daily_demand")
    logger.info("Calculated average daily demand per product.")
    
    # ----------------------------------------------------
    # 2. PRODUCT TABLE ENRICHMENT
    # ----------------------------------------------------
    logger.info("Enriching Products table...")
    
    # Vectorized computation of primary supplier (most frequent supplier in POs per product)
    po_counts = purchase_orders.groupby(["product_id", "supplier_id"]).size().reset_index(name="count")
    po_supplier_map = po_counts.sort_values("count", ascending=False).drop_duplicates("product_id")[["product_id", "supplier_id"]]
    
    products_enriched = pd.merge(products, po_supplier_map, on="product_id", how="left")
    
    # Merge lead time and supplier rating
    products_enriched = pd.merge(products_enriched, suppliers[["supplier_id", "lead_time_days", "rating"]], on="supplier_id", how="left")
    products_enriched["lead_time_days"] = products_enriched["lead_time_days"].fillna(settings.default_supplier_lead_time).astype(int)
    products_enriched["supplier_rating"] = products_enriched["rating"].fillna(settings.default_supplier_rating)
    products_enriched.drop(columns=["supplier_id", "rating"], errors="ignore", inplace=True)
    
    # Aggregate current inventory quantities
    stock_sum = inventory.groupby("product_id")["quantity"].sum().reset_index(name="current_stock_quantity")
    products_enriched = pd.merge(products_enriched, stock_sum, on="product_id", how="left").fillna({"current_stock_quantity": 0})
    products_enriched["current_stock_quantity"] = products_enriched["current_stock_quantity"].astype(int)
    
    # Calculate Inventory Value
    products_enriched["inventory_value"] = products_enriched["current_stock_quantity"] * products_enriched["unit_cost"]
    
    # Merge Average Daily Demand
    products_enriched = pd.merge(products_enriched, avg_daily_demand, on="product_id", how="left").fillna({"avg_daily_demand": 0.0})
    
    # Calculate Safety Stock (Average Daily Demand * lead_time_days)
    products_enriched["safety_stock"] = products_enriched["avg_daily_demand"] * products_enriched["lead_time_days"]
    
    # Calculate Stock Status
    status_conditions = [
        (products_enriched["current_stock_quantity"] == 0),
        (products_enriched["current_stock_quantity"] > 0) & (products_enriched["current_stock_quantity"] <= products_enriched["reorder_point"]),
        (products_enriched["current_stock_quantity"] > products_enriched["reorder_point"])
    ]
    status_choices = ["Out Of Stock", "Low Stock", "In Stock"]
    products_enriched["stock_status"] = np.select(status_conditions, status_choices, default="In Stock")
    
    # Reorder Required flag
    products_enriched["reorder_required"] = (products_enriched["current_stock_quantity"] <= products_enriched["reorder_point"]).astype(int)
    
    # Safety Stock Flag
    products_enriched["safety_stock_flag"] = (products_enriched["current_stock_quantity"] < products_enriched["safety_stock"]).astype(int)
    
    # Days Until Stockout
    products_enriched["days_until_stockout"] = np.where(
        products_enriched["avg_daily_demand"] > 0,
        products_enriched["current_stock_quantity"] / products_enriched["avg_daily_demand"],
        settings.max_days_until_stockout
    )
    products_enriched["days_until_stockout"] = np.minimum(products_enriched["days_until_stockout"], settings.max_days_until_stockout)
    
    # Demand Category (quantiles)
    demand_vals = products_enriched["avg_daily_demand"]
    q25 = demand_vals[demand_vals > 0].quantile(0.25) if not demand_vals[demand_vals > 0].empty else 0.0
    q75 = demand_vals[demand_vals > 0].quantile(0.75) if not demand_vals[demand_vals > 0].empty else 0.0
    
    demand_conditions = [
        (products_enriched["avg_daily_demand"] == 0),
        (products_enriched["avg_daily_demand"] > 0) & (products_enriched["avg_daily_demand"] <= q25),
        (products_enriched["avg_daily_demand"] > q25) & (products_enriched["avg_daily_demand"] <= q75),
        (products_enriched["avg_daily_demand"] > q75)
    ]
    demand_choices = ["No Demand", "Low Demand", "Medium Demand", "High Demand"]
    products_enriched["demand_category"] = np.select(demand_conditions, demand_choices, default="Medium Demand")
    
    # Inventory Turnover
    total_sales_qty = sales.groupby("product_id")["quantity"].sum().reset_index(name="total_units_sold")
    products_enriched = pd.merge(products_enriched, total_sales_qty, on="product_id", how="left").fillna({"total_units_sold": 0})
    products_enriched["cogs"] = products_enriched["total_units_sold"] * products_enriched["unit_cost"]
    
    products_enriched["inventory_turnover"] = np.where(
        products_enriched["inventory_value"] > 0,
        products_enriched["cogs"] / products_enriched["inventory_value"],
        0.0
    )
    
    # ----------------------------------------------------
    # 3. SALES TABLE ENRICHMENT & TIME FEATURES
    # ----------------------------------------------------
    logger.info("Enriching Sales table...")
    sales_enriched = pd.merge(sales, products[["product_id", "unit_cost"]], on="product_id", how="left")
    
    # Financial metrics
    sales_enriched["revenue"] = sales_enriched["quantity"] * sales_enriched["unit_price"]
    sales_enriched["profit"] = sales_enriched["revenue"] - (sales_enriched["quantity"] * sales_enriched["unit_cost"])
    sales_enriched["profit_margin"] = np.where(
        sales_enriched["revenue"] > 0,
        sales_enriched["profit"] / sales_enriched["revenue"],
        0.0
    )
    
    # Time Features (fully vectorized)
    sales_enriched["week"] = sales_enriched["sale_date"].dt.isocalendar().week.astype(int)
    sales_enriched["month"] = sales_enriched["sale_date"].dt.month.astype(int)
    sales_enriched["quarter"] = sales_enriched["sale_date"].dt.quarter.astype(int)
    sales_enriched["year"] = sales_enriched["sale_date"].dt.year.astype(int)
    sales_enriched["day_of_week"] = sales_enriched["sale_date"].dt.dayofweek.astype(int)
    sales_enriched["weekend_indicator"] = sales_enriched["day_of_week"].isin([5, 6]).astype(int)
    # Optimized map instead of apply
    sales_enriched["season"] = sales_enriched["month"].map(MONTH_TO_SEASON)
    
    # Merge Rolling Sales
    sales_enriched = pd.merge(
        sales_enriched,
        grid_sales[["sale_date", "product_id", "rolling_sales_7d", "rolling_sales_30d"]],
        on=["sale_date", "product_id"],
        how="left"
    ).fillna({"rolling_sales_7d": 0, "rolling_sales_30d": 0})
    
    # ----------------------------------------------------
    # 4. INVENTORY TABLE ENRICHMENT
    # ----------------------------------------------------
    logger.info("Enriching Inventory table...")
    inventory_enriched = pd.merge(inventory, products[["product_id", "unit_cost", "reorder_point"]], on="product_id", how="left")
    inventory_enriched["inventory_value"] = inventory_enriched["quantity"] * inventory_enriched["unit_cost"]
    inventory_enriched["reorder_required"] = (inventory_enriched["quantity"] <= inventory_enriched["reorder_point"]).astype(int)
    
    status_conditions_inv = [
        (inventory_enriched["quantity"] == 0),
        (inventory_enriched["quantity"] > 0) & (inventory_enriched["quantity"] <= inventory_enriched["reorder_point"]),
        (inventory_enriched["quantity"] > inventory_enriched["reorder_point"])
    ]
    inventory_enriched["stock_status"] = np.select(status_conditions_inv, status_choices, default="In Stock")
    
    inventory_enriched = pd.merge(
        inventory_enriched, 
        products_enriched[["product_id", "avg_daily_demand", "safety_stock", "safety_stock_flag"]], 
        on="product_id", 
        how="left"
    )
    
    # ----------------------------------------------------
    # 5. PURCHASE ORDERS ENRICHMENT & TIME FEATURES
    # ----------------------------------------------------
    logger.info("Enriching Purchase Orders table...")
    po_enriched = purchase_orders.copy()
    
    po_enriched["week"] = po_enriched["order_date"].dt.isocalendar().week.astype(int)
    po_enriched["month"] = po_enriched["order_date"].dt.month.astype(int)
    po_enriched["quarter"] = po_enriched["order_date"].dt.quarter.astype(int)
    po_enriched["year"] = po_enriched["order_date"].dt.year.astype(int)
    po_enriched["day_of_week"] = po_enriched["order_date"].dt.dayofweek.astype(int)
    po_enriched["weekend_indicator"] = po_enriched["day_of_week"].isin([5, 6]).astype(int)
    po_enriched["season"] = po_enriched["month"].map(MONTH_TO_SEASON)
    
    # ----------------------------------------------------
    # SAVE PROCESSED DATASETS
    # ----------------------------------------------------
    processed_dfs = {
        "products": products_enriched,
        "inventory": inventory_enriched,
        "sales": sales_enriched,
        "suppliers": suppliers.copy(),
        "purchase_orders": po_enriched,
        "forecasts": forecasts.copy(),
        "audit_logs": audit_logs
    }
    
    processed_dir = os.path.join(settings.export_dir, "..", "processed")
    processed_dir = os.path.abspath(processed_dir)
    os.makedirs(processed_dir, exist_ok=True)
    
    for name, df in processed_dfs.items():
        export_df = df.copy()
        date_cols = [c for c in export_df.columns if any(x in c for x in ["date", "updated", "timestamp", "generated", "created", "delivery"])]
        for col in date_cols:
            if col in export_df.columns:
                # Ensure the column is parsed as datetime
                export_df[col] = pd.to_datetime(export_df[col], errors="coerce")
                if col in ["sale_date", "forecast_date", "order_date", "expected_delivery", "actual_delivery"]:
                    export_df[col] = export_df[col].dt.strftime("%Y-%m-%d")
                else:
                    export_df[col] = export_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3] + "Z"
                    
        processed_csv_path = os.path.join(processed_dir, f"{name}_processed.csv")
        export_df.to_csv(processed_csv_path, index=False, encoding="utf-8")
        logger.debug(f"Saved processed table to: {processed_csv_path}")
        
    logger.info("Feature Engineering & Transformation completed successfully.")
    return processed_dfs

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger

logger = setup_logger("transform")

def get_season(month: int) -> str:
    """Helper to map calendar month to season."""
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

def transform_data(cleaned_dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Applies feature engineering to the cleaned operational dataframes.
    Enriches products, sales, and inventory tables with calculated business metrics.
    """
    logger.info("Starting Feature Engineering & Transformation...")
    
    # Extract clean dfs
    products = cleaned_dfs["products"].copy()
    inventory = cleaned_dfs["inventory"].copy()
    sales = cleaned_dfs["sales"].copy()
    suppliers = cleaned_dfs["suppliers"].copy()
    purchase_orders = cleaned_dfs["purchase_orders"].copy()
    forecasts = cleaned_dfs["forecasts"].copy()
    
    # ----------------------------------------------------
    # 1. PRE-COMPUTATIONS (Daily Sales Time Series & Demand)
    # ----------------------------------------------------
    # Convert dates to datetime objects for grouping
    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    
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
    # Mean of daily sales including zero-sales days
    avg_daily_demand = grid_sales.groupby("product_id")["quantity"].mean().reset_index(name="avg_daily_demand")
    logger.info("Calculated average daily demand per product.")
    
    # ----------------------------------------------------
    # 2. PRODUCT TABLE ENRICHMENT
    # ----------------------------------------------------
    logger.info("Enriching Products table...")
    # Add Supplier Info (we join on product's purchase orders or suppliers. For simplicity, we get the lead_time of suppliers who provide the product.
    # Let's map lead_time_days and rating of suppliers by finding the primary supplier for each product.
    # Primary supplier can be determined by the most frequent supplier in purchase orders for that product, or first supplier in suppliers.
    po_supplier_map = purchase_orders.groupby("product_id")["supplier_id"].agg(lambda x: x.value_counts().index[0] if not x.empty else None).reset_index()
    products_enriched = pd.merge(products, po_supplier_map, on="product_id", how="left")
    
    # Merge lead time and supplier rating
    products_enriched = pd.merge(products_enriched, suppliers[["supplier_id", "lead_time_days", "rating"]], on="supplier_id", how="left")
    products_enriched["lead_time_days"] = products_enriched["lead_time_days"].fillna(7).astype(int)
    products_enriched["supplier_rating"] = products_enriched["rating"].fillna(3.0)
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
    # Out of Stock: current_stock == 0
    # Low Stock: 0 < current_stock <= reorder_point
    # In Stock: current_stock > reorder_point
    status_conditions = [
        (products_enriched["current_stock_quantity"] == 0),
        (products_enriched["current_stock_quantity"] > 0) & (products_enriched["current_stock_quantity"] <= products_enriched["reorder_point"]),
        (products_enriched["current_stock_quantity"] > products_enriched["reorder_point"])
    ]
    status_choices = ["Out Of Stock", "Low Stock", "In Stock"]
    products_enriched["stock_status"] = np.select(status_conditions, status_choices, default="In Stock")
    
    # Reorder Required
    products_enriched["reorder_required"] = (products_enriched["current_stock_quantity"] <= products_enriched["reorder_point"]).astype(int)
    
    # Safety Stock Flag (current stock below safety stock)
    products_enriched["safety_stock_flag"] = (products_enriched["current_stock_quantity"] < products_enriched["safety_stock"]).astype(int)
    
    # Days Until Stockout
    products_enriched["days_until_stockout"] = np.where(
        products_enriched["avg_daily_demand"] > 0,
        products_enriched["current_stock_quantity"] / products_enriched["avg_daily_demand"],
        999.0
    )
    products_enriched["days_until_stockout"] = np.minimum(products_enriched["days_until_stockout"], 999.0) # Cap at 999
    
    # Demand Category
    # Categorize demand level using percentiles of average daily demand: High (>75%), Medium (25-75%), Low (0-25%), None (0)
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
    
    # Inventory Turnover: COGS / current inventory value.
    # Let's compute total units sold for each product
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
    # Join sales with products to get unit_cost
    sales_enriched = pd.merge(sales, products[["product_id", "unit_cost"]], on="product_id", how="left")
    
    # Revenue = qty * unit_price
    sales_enriched["revenue"] = sales_enriched["quantity"] * sales_enriched["unit_price"]
    
    # Profit = Revenue - COGS
    sales_enriched["profit"] = sales_enriched["revenue"] - (sales_enriched["quantity"] * sales_enriched["unit_cost"])
    
    # Profit Margin = Profit / Revenue
    sales_enriched["profit_margin"] = np.where(
        sales_enriched["revenue"] > 0,
        sales_enriched["profit"] / sales_enriched["revenue"],
        0.0
    )
    
    # Time Features
    sales_enriched["week"] = sales_enriched["sale_date"].dt.isocalendar().week.astype(int)
    sales_enriched["month"] = sales_enriched["sale_date"].dt.month.astype(int)
    sales_enriched["quarter"] = sales_enriched["sale_date"].dt.quarter.astype(int)
    sales_enriched["year"] = sales_enriched["sale_date"].dt.year.astype(int)
    sales_enriched["day_of_week"] = sales_enriched["sale_date"].dt.dayofweek.astype(int)
    sales_enriched["weekend_indicator"] = sales_enriched["day_of_week"].isin([5, 6]).astype(int)
    sales_enriched["season"] = sales_enriched["month"].apply(get_season)
    
    # Merge Rolling Sales
    # We join sales_enriched with grid_sales on product_id and sale_date
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
    
    # Reorder Required
    inventory_enriched["reorder_required"] = (inventory_enriched["quantity"] <= inventory_enriched["reorder_point"]).astype(int)
    
    # Stock Status
    status_conditions_inv = [
        (inventory_enriched["quantity"] == 0),
        (inventory_enriched["quantity"] > 0) & (inventory_enriched["quantity"] <= inventory_enriched["reorder_point"]),
        (inventory_enriched["quantity"] > inventory_enriched["reorder_point"])
    ]
    inventory_enriched["stock_status"] = np.select(status_conditions_inv, status_choices, default="In Stock")
    
    # Average Daily Demand & Safety Stock Flag
    inventory_enriched = pd.merge(inventory_enriched, products_enriched[["product_id", "avg_daily_demand", "safety_stock", "safety_stock_flag"]], on="product_id", how="left")
    
    # ----------------------------------------------------
    # 5. PURCHASE ORDERS ENRICHMENT & TIME FEATURES
    # ----------------------------------------------------
    logger.info("Enriching Purchase Orders table...")
    po_enriched = purchase_orders.copy()
    po_enriched["order_date"] = pd.to_datetime(po_enriched["order_date"])
    po_enriched["expected_delivery"] = pd.to_datetime(po_enriched["expected_delivery"])
    po_enriched["actual_delivery"] = pd.to_datetime(po_enriched["actual_delivery"])
    
    po_enriched["week"] = po_enriched["order_date"].dt.isocalendar().week.astype(int)
    po_enriched["month"] = po_enriched["order_date"].dt.month.astype(int)
    po_enriched["quarter"] = po_enriched["order_date"].dt.quarter.astype(int)
    po_enriched["year"] = po_enriched["order_date"].dt.year.astype(int)
    po_enriched["day_of_week"] = po_enriched["order_date"].dt.dayofweek.astype(int)
    po_enriched["weekend_indicator"] = po_enriched["day_of_week"].isin([5, 6]).astype(int)
    po_enriched["season"] = po_enriched["month"].apply(get_season)
    
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
        "audit_logs": cleaned_dfs["audit_logs"].copy()
    }
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    for name, df in processed_dfs.items():
        export_df = df.copy()
        date_cols = [c for c in export_df.columns if "date" in c or "updated" in c or "timestamp" in c or "generated" in c or "created" in c or "delivery" in c]
        for col in date_cols:
            if col in export_df.columns:
                # format dates as strings for CSV
                if col in ["sale_date", "forecast_date", "order_date", "expected_delivery", "actual_delivery"]:
                    export_df[col] = export_df[col].dt.strftime("%Y-%m-%d")
                else:
                    export_df[col] = export_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3] + "Z"
                    
        processed_csv_path = os.path.join(processed_dir, f"{name}_processed.csv")
        export_df.to_csv(processed_csv_path, index=False, encoding="utf-8")
        logger.info(f"Saved processed table to: {processed_csv_path}")
        
    logger.info("Feature Engineering & Transformation completed successfully.")
    return processed_dfs

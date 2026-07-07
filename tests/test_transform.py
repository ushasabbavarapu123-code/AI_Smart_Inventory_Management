import pandas as pd
import numpy as np
from transform import transform_data

def test_transform_features():
    """Verifies that feature engineering adds all expected columns and performs calculations correctly."""
    products = pd.DataFrame({
        "product_id": ["p1", "p2"],
        "sku": ["ELE-LAP", "ELE-MOU"],
        "name": ["Laptop", "Mouse"],
        "category": ["Electronics", "Electronics"],
        "unit_cost": [500.0, 10.0],
        "reorder_point": [10, 5]
    })
    
    inventory = pd.DataFrame({
        "inventory_id": ["i1", "i2"],
        "product_id": ["p1", "p2"],
        "quantity": [15, 3], # p1 is In Stock (15 > 10), p2 is Low Stock (3 <= 5)
        "location": ["Warehouse-A", "Warehouse-B"]
    })
    
    sales = pd.DataFrame({
        "sale_id": ["sa1", "sa2"],
        "product_id": ["p1", "p2"],
        "sale_date": [pd.Timestamp("2026-07-02"), pd.Timestamp("2026-07-03")],
        "quantity": [2, 10],
        "unit_price": [750.0, 20.0],
        "customer_type": ["Retail", "Wholesale"]
    })
    
    suppliers = pd.DataFrame({
        "supplier_id": ["s1"],
        "name": ["Supplier A"],
        "lead_time_days": [5],
        "rating": [4.5]
    })
    
    purchase_orders = pd.DataFrame({
        "po_id": ["po1"],
        "supplier_id": ["s1"],
        "product_id": ["p1"],
        "quantity": [20],
        "unit_cost": [500.0],
        "order_date": [pd.Timestamp("2026-06-15")],
        "expected_delivery": [pd.Timestamp("2026-06-22")],
        "actual_delivery": [pd.Timestamp("2026-06-21")],
        "status": ["Received"]
    })
    
    forecasts = pd.DataFrame({
        "forecast_id": ["f1"],
        "product_id": ["p1"],
        "forecast_date": [pd.Timestamp("2026-08-01")],
        "predicted_qty": [45.0],
        "confidence_low": [30.0],
        "confidence_high": [60.0],
        "model_used": ["ARIMA"]
    })
    
    cleaned_dfs = {
        "products": products,
        "inventory": inventory,
        "sales": sales,
        "suppliers": suppliers,
        "purchase_orders": purchase_orders,
        "forecasts": forecasts,
        "audit_logs": pd.DataFrame(columns=["log_id", "action", "timestamp"])
    }
    
    processed = transform_data(cleaned_dfs)
    
    # 1. Product Enriched Metrics
    prod_enriched = processed["products"]
    assert "inventory_value" in prod_enriched.columns
    assert prod_enriched[prod_enriched["product_id"] == "p1"]["inventory_value"].iloc[0] == 7500.0 # 15 * 500
    assert prod_enriched[prod_enriched["product_id"] == "p1"]["stock_status"].iloc[0] == "In Stock"
    assert prod_enriched[prod_enriched["product_id"] == "p2"]["stock_status"].iloc[0] == "Low Stock"
    
    # 2. Sales Enriched Metrics
    sales_enriched = processed["sales"]
    assert "revenue" in sales_enriched.columns
    assert "profit" in sales_enriched.columns
    assert "profit_margin" in sales_enriched.columns
    assert sales_enriched["revenue"].iloc[0] == 1500.0 # 2 * 750
    assert sales_enriched["profit"].iloc[0] == 500.0   # 1500 - (2 * 500)
    assert sales_enriched["profit_margin"].iloc[0] == 500.0 / 1500.0
    
    # Season mapping
    assert sales_enriched["season"].iloc[0] == "Summer" # July
    
    # Rolling Sales columns present
    assert "rolling_sales_7d" in sales_enriched.columns
    assert "rolling_sales_30d" in sales_enriched.columns

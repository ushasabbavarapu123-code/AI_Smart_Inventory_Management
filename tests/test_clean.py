import pandas as pd
import numpy as np
from clean import profile_data_quality, clean_dataset, cap_outliers_iqr

def test_profile_data_quality():
    """Tests that profiling correctly identifies null values, duplicates, and negative quantities."""
    df_sales = pd.DataFrame({
        "sale_id": ["s1", "s2", "s2", "s3"], # 1 duplicate
        "quantity": [5, -2, -2, 10],      # negative values
        "sale_date": ["2026-07-01", "2026-07-02", "2026-07-02", None] # 1 null
    })
    
    report = profile_data_quality({"sales": df_sales})
    assert "sales" in report
    assert report["sales"]["duplicates"] == 1
    assert report["sales"]["negative_values"]["quantity"] == 2
    assert report["sales"]["missing_values"]["sale_date"] == 1

def test_cap_outliers_iqr():
    """Tests that the IQR capping clips values outside threshold bounds."""
    df = pd.DataFrame({"quantity": [1, 2, 3, 2, 1, 100]}) # 100 is an outlier
    df_capped, capped_count = cap_outliers_iqr(df.copy(), "quantity", multiplier=1.5)
    
    assert capped_count == 1
    # Check that 100 was capped down to a lower bound (Q3 + 1.5*IQR)
    assert df_capped["quantity"].iloc[-1] < 100

def test_clean_dataset_removes_negatives_and_orphans():
    """Tests null imputation, negative value drops, and orphan child drops."""
    products = pd.DataFrame({
        "product_id": ["p1", "p2"],
        "sku": [" ele-lap ", "ele-mou"], # leading whitespace
        "name": ["Laptop", None],        # null name
        "category": [None, "Electronics"], # null category
        "unit_cost": [500.0, 10.0],
        "reorder_point": [10, 5],
        "created_at": ["2026-06-01", "2026-06-01"]
    })
    
    sales = pd.DataFrame({
        "sale_id": ["sa1", "sa2", "sa3"],
        "product_id": ["p1", "p3", "p2"], # p3 is an orphan product id (not in products)
        "sale_date": ["2026-07-01", "2026-07-02", "2026-07-03"],
        "quantity": [2, 5, -1],           # sa3 has negative quantity
        "unit_price": [750.0, 20.0, 20.0],
        "customer_type": ["retail", "wholesale", "retail"]
    })
    
    suppliers = pd.DataFrame({
        "supplier_id": ["s1"],
        "name": ["Supplier A"],
        "lead_time_days": [5],
        "rating": [4.5]
    })
    
    purchase_orders = pd.DataFrame(columns=["po_id", "supplier_id", "product_id", "quantity", "unit_cost", "order_date", "status"])
    forecasts = pd.DataFrame(columns=["forecast_id", "product_id", "forecast_date", "predicted_qty", "confidence_low", "confidence_high", "model_used"])
    audit_logs = pd.DataFrame(columns=["log_id", "action", "user_id"])
    
    raw_dfs = {
        "products": products,
        "sales": sales,
        "suppliers": suppliers,
        "inventory": pd.DataFrame(columns=["inventory_id", "product_id", "quantity", "location"]),
        "purchase_orders": purchase_orders,
        "forecasts": forecasts,
        "audit_logs": audit_logs
    }
    
    cleaned_dfs, metrics = clean_dataset(raw_dfs)
    
    # 1. Whitespace stripped and SKU uppercase
    assert cleaned_dfs["products"]["sku"].iloc[0] == "ELE-LAP"
    
    # 2. Imputations
    assert cleaned_dfs["products"]["name"].iloc[1] == "Unknown Product"
    assert cleaned_dfs["products"]["category"].iloc[0] == "Other"
    
    # 3. Negatives dropped: sales sa3 (qty = -1) removed
    # Also orphan sales sa2 (product_id = p3) dropped by referential integrity
    # Total sales remaining should be only sa1 (product_id = p1)
    assert len(cleaned_dfs["sales"]) == 1
    assert cleaned_dfs["sales"]["sale_id"].iloc[0] == "sa1"
    
    # 4. Orphans count tracked
    assert metrics["rows_removed"]["sales_product_orphans"] == 1

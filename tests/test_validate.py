import pandas as pd
from validate import validate_datasets

def test_validation_report_passes():
    """Verifies that clean, correct data passes validation checks."""
    products = pd.DataFrame({
        "product_id": ["p1"],
        "sku": ["SKU1"],
        "name": ["Name1"],
        "category": ["Category1"],
        "unit_cost": [10.0],
        "reorder_point": [5],
        "created_at": ["2026-06-01T12:00:00Z"],
        "current_stock_quantity": [10],
        "inventory_value": [100.0],
        "avg_daily_demand": [1.0],
        "safety_stock": [5.0],
        "stock_status": ["In Stock"],
        "reorder_required": [0],
        "safety_stock_flag": [0],
        "days_until_stockout": [10.0],
        "demand_category": ["Low Demand"],
        "total_units_sold": [5],
        "cogs": [50.0],
        "inventory_turnover": [0.5],
        "lead_time_days": [5],
        "supplier_rating": [4.0]
    })
    
    inventory = pd.DataFrame({
        "inventory_id": ["i1"],
        "product_id": ["p1"],
        "quantity": [10],
        "location": ["Loc1"],
        "last_updated": ["2026-07-01T12:00:00Z"],
        "inventory_value": [100.0],
        "reorder_required": [0],
        "stock_status": ["In Stock"],
        "avg_daily_demand": [1.0],
        "safety_stock": [5.0],
        "safety_stock_flag": [0],
        "unit_cost": [10.0],
        "reorder_point": [5]
    })
    
    sales = pd.DataFrame({
        "sale_id": ["s1"],
        "product_id": ["p1"],
        "sale_date": ["2026-07-02"],
        "quantity": [5],
        "unit_price": [20.0],
        "customer_type": ["Retail"],
        "unit_cost": [10.0],
        "revenue": [100.0], # 5 * 20
        "profit": [50.0],   # 100 - (5 * 10)
        "profit_margin": [0.5],
        "week": [27],
        "month": [7],
        "quarter": [3],
        "year": [2026],
        "day_of_week": [3],
        "weekend_indicator": [0],
        "season": ["Summer"],
        "rolling_sales_7d": [5.0],
        "rolling_sales_30d": [5.0],
        "created_at": ["2026-07-02T18:00:00Z"]
    })
    
    suppliers = pd.DataFrame({
        "supplier_id": ["s1"],
        "name": ["Supplier A"],
        "contact_person": ["John"],
        "contact_email": ["john@s.com"],
        "contact_phone": ["123"],
        "lead_time_days": [5],
        "rating": [4.5],
        "created_at": ["2026-06-01T12:00:00Z"]
    })
    
    purchase_orders = pd.DataFrame({
        "po_id": ["po1"],
        "supplier_id": ["s1"],
        "product_id": ["p1"],
        "quantity": [10],
        "unit_cost": [10.0],
        "order_date": ["2026-06-15"],
        "expected_delivery": ["2026-06-22"],
        "actual_delivery": ["2026-06-21"],
        "status": ["Received"],
        "notes": ["N/A"],
        "week": [25],
        "month": [6],
        "quarter": [2],
        "year": [2026],
        "day_of_week": [0],
        "weekend_indicator": [0],
        "season": ["Summer"],
        "created_at": ["2026-06-15T12:00:00Z"]
    })
    
    forecasts = pd.DataFrame({
        "forecast_id": ["f1"],
        "product_id": ["p1"],
        "forecast_date": ["2026-08-01"],
        "predicted_qty": [45.0],
        "confidence_low": [30.0],
        "confidence_high": [60.0],
        "model_used": ["ARIMA"],
        "generated_at": ["2026-07-07T12:00:00Z"]
    })
    
    processed_dfs = {
        "products": products,
        "inventory": inventory,
        "sales": sales,
        "suppliers": suppliers,
        "purchase_orders": purchase_orders,
        "forecasts": forecasts
    }
    
    report = validate_datasets(processed_dfs)
    assert report["success"] is True
    assert report["status"] == "PASSED"

def test_validation_report_fails_on_business_rule_violation():
    """Verifies that validation fails if revenue or profit calculations are incorrect."""
    products = pd.DataFrame({
        "product_id": ["p1"],
        "sku": ["SKU1"],
        "name": ["Name1"],
        "category": ["Category1"],
        "unit_cost": [10.0],
        "reorder_point": [5],
        "created_at": ["2026-06-01T12:00:00Z"],
        "current_stock_quantity": [10],
        "inventory_value": [100.0],
        "avg_daily_demand": [1.0],
        "safety_stock": [5.0],
        "stock_status": ["In Stock"],
        "reorder_required": [0],
        "safety_stock_flag": [0],
        "days_until_stockout": [10.0],
        "demand_category": ["Low Demand"],
        "total_units_sold": [5],
        "cogs": [50.0],
        "inventory_turnover": [0.5],
        "lead_time_days": [5],
        "supplier_rating": [4.0]
    })
    
    sales = pd.DataFrame({
        "sale_id": ["s1"],
        "product_id": ["p1"],
        "sale_date": ["2026-07-02"],
        "quantity": [5],
        "unit_price": [20.0],
        "customer_type": ["Retail"],
        "unit_cost": [10.0],
        # Incorrect revenue: 5 * 20 = 100, but set to 999.0 to trigger violation
        "revenue": [999.0], 
        "profit": [50.0],
        "profit_margin": [0.5],
        "week": [27],
        "month": [7],
        "quarter": [3],
        "year": [2026],
        "day_of_week": [3],
        "weekend_indicator": [0],
        "season": ["Summer"],
        "rolling_sales_7d": [5.0],
        "rolling_sales_30d": [5.0],
        "created_at": ["2026-07-02T18:00:00Z"]
    })
    
    # Other tables minimally defined to satisfy check schema structure
    processed_dfs = {
        "products": products,
        "inventory": pd.DataFrame(columns=["inventory_id", "product_id", "quantity", "location", "last_updated", "inventory_value", "reorder_required", "stock_status", "avg_daily_demand", "safety_stock", "safety_stock_flag", "unit_cost", "reorder_point"]),
        "sales": sales,
        "suppliers": pd.DataFrame(columns=["supplier_id", "name", "contact_person", "contact_email", "contact_phone", "lead_time_days", "rating", "created_at"]),
        "purchase_orders": pd.DataFrame(columns=["po_id", "supplier_id", "product_id", "quantity", "unit_cost", "order_date", "expected_delivery", "actual_delivery", "status", "notes", "week", "month", "quarter", "year", "day_of_week", "weekend_indicator", "season", "created_at"]),
        "forecasts": pd.DataFrame(columns=["forecast_id", "product_id", "forecast_date", "predicted_qty", "confidence_low", "confidence_high", "model_used", "generated_at"])
    }
    
    report = validate_datasets(processed_dfs)
    assert report["success"] is False
    assert report["business_rules"]["success"] is False
    assert len(report["business_rules"]["errors"]) > 0

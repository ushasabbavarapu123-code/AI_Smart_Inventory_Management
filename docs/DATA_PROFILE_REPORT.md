# Data Profile Report

**Execution Timestamp:** 2026-07-14 19:22:50

This document provides structural, statistical, and memory profiles of the operational datasets.

## 1. Executive Summary
High-level metrics across all tables:

| Table Name | Rows | Columns | Memory Usage (KB) | Duplicate % | Missing Values % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `audit_logs` | 1 | 9 | 0.24 KB | 0.00% | 22.22% |
| `forecasts` | 1 | 8 | 0.20 KB | 0.00% | 0.00% |
| `inventory` | 2 | 13 | 0.38 KB | 0.00% | 0.00% |
| `products` | 2 | 21 | 0.57 KB | 0.00% | 0.00% |
| `purchase_orders` | 1 | 18 | 0.30 KB | 0.00% | 0.00% |
| `sales` | 3 | 20 | 0.66 KB | 0.00% | 0.00% |
| `suppliers` | 1 | 8 | 0.23 KB | 0.00% | 0.00% |
| **Total / Summary** | **11** | **N/A** | **2.59 KB** | **N/A** | **N/A** |

---

## Table Profile: `audit_logs`
Dimensions: 1 rows × 9 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `log_id` | str | 0 (0.0%) | 1 | 100.0% | 'l1' | N/A | N/A | N/A |
| `action` | str | 0 (0.0%) | 1 | 100.0% | 'CREATE_SALE' | N/A | N/A | N/A |
| `entity` | str | 0 (0.0%) | 1 | 100.0% | 'sales' | N/A | N/A | N/A |
| `entity_id` | str | 0 (0.0%) | 1 | 100.0% | 'sa1' | N/A | N/A | N/A |
| `user_id` | str | 0 (0.0%) | 1 | 100.0% | 'system' | N/A | N/A | N/A |
| `old_value` | str | 1 (100.0%) | 0 | 0.0% | N/A | N/A | N/A | N/A |
| `new_value` | str | 1 (100.0%) | 0 | 0.0% | N/A | N/A | N/A | N/A |
| `ip_address` | str | 0 (0.0%) | 1 | 100.0% | '127.0.0.1' | N/A | N/A | N/A |
| `timestamp` | datetime64[us, UTC] | 0 (0.0%) | 1 | 100.0% | 2026-07-02 | 2026-07-02 | N/A | N/A |

### Categorical Value Distributions
- **action**: **CREATE_SALE**: 1 (100.0%)
- **entity**: **sales**: 1 (100.0%)
- **entity_id**: **sa1**: 1 (100.0%)
- **user_id**: **system**: 1 (100.0%)
- **old_value**: **nan**: 1 (100.0%)
- **new_value**: **nan**: 1 (100.0%)
- **ip_address**: **127.0.0.1**: 1 (100.0%)
- **timestamp**: **2026-07-02 18:00:00+00:00**: 1 (100.0%)

---


## Table Profile: `forecasts`
Dimensions: 1 rows × 8 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `forecast_id` | str | 0 (0.0%) | 1 | 100.0% | 'f1' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 1 | 100.0% | 'p1' | N/A | N/A | N/A |
| `forecast_date` | datetime64[us] | 0 (0.0%) | 1 | 100.0% | 2026-08-01 | 2026-08-01 | N/A | N/A |
| `predicted_qty` | float64 | 0 (0.0%) | 1 | 100.0% | 45.00 | 45.00 | 45.00 | 0.00 |
| `confidence_low` | float64 | 0 (0.0%) | 1 | 100.0% | 30.00 | 30.00 | 30.00 | 0.00 |
| `confidence_high` | float64 | 0 (0.0%) | 1 | 100.0% | 60.00 | 60.00 | 60.00 | 0.00 |
| `model_used` | str | 0 (0.0%) | 1 | 100.0% | 'ARIMA' | N/A | N/A | N/A |
| `generated_at` | datetime64[us, UTC] | 0 (0.0%) | 1 | 100.0% | 2026-07-07 | 2026-07-07 | N/A | N/A |

### Categorical Value Distributions
- **product_id**: **p1**: 1 (100.0%)
- **forecast_date**: **2026-08-01 00:00:00**: 1 (100.0%)
- **predicted_qty**: **45.0**: 1 (100.0%)
- **confidence_low**: **30.0**: 1 (100.0%)
- **confidence_high**: **60.0**: 1 (100.0%)
- **model_used**: **ARIMA**: 1 (100.0%)
- **generated_at**: **2026-07-07 12:00:00+00:00**: 1 (100.0%)

---


## Table Profile: `inventory`
Dimensions: 2 rows × 13 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `inventory_id` | str | 0 (0.0%) | 2 | 100.0% | 'i1' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 2 | 100.0% | 'p1' | N/A | N/A | N/A |
| `quantity` | int64 | 0 (0.0%) | 2 | 100.0% | 3.00 | 15.00 | 9.00 | 8.49 |
| `location` | str | 0 (0.0%) | 2 | 100.0% | 'Warehouse-A' | N/A | N/A | N/A |
| `last_updated` | datetime64[us, UTC] | 0 (0.0%) | 1 | 50.0% | 2026-07-01 | 2026-07-01 | N/A | N/A |
| `unit_cost` | float64 | 0 (0.0%) | 2 | 100.0% | 10.00 | 500.00 | 255.00 | 346.48 |
| `reorder_point` | int64 | 0 (0.0%) | 2 | 100.0% | 5.00 | 10.00 | 7.50 | 3.54 |
| `inventory_value` | float64 | 0 (0.0%) | 2 | 100.0% | 30.00 | 7500.00 | 3765.00 | 5282.09 |
| `reorder_required` | int64 | 0 (0.0%) | 2 | 100.0% | 0.00 | 1.00 | 0.50 | 0.71 |
| `stock_status` | str | 0 (0.0%) | 2 | 100.0% | 'In Stock' | N/A | N/A | N/A |
| `avg_daily_demand` | float64 | 0 (0.0%) | 2 | 100.0% | 0.67 | 36.67 | 18.67 | 25.46 |
| `safety_stock` | float64 | 0 (0.0%) | 2 | 100.0% | 3.33 | 256.67 | 130.00 | 179.13 |
| `safety_stock_flag` | int64 | 0 (0.0%) | 2 | 100.0% | 0.00 | 1.00 | 0.50 | 0.71 |

### Categorical Value Distributions
- **product_id**: **p1**: 1 (50.0%), **p2**: 1 (50.0%)
- **quantity**: **15**: 1 (50.0%), **3**: 1 (50.0%)
- **location**: **Warehouse-A**: 1 (50.0%), **Warehouse-B**: 1 (50.0%)
- **last_updated**: **2026-07-01 12:00:00+00:00**: 2 (100.0%)
- **unit_cost**: **500.0**: 1 (50.0%), **10.0**: 1 (50.0%)
- **reorder_point**: **10**: 1 (50.0%), **5**: 1 (50.0%)
- **inventory_value**: **7500.0**: 1 (50.0%), **30.0**: 1 (50.0%)
- **reorder_required**: **0**: 1 (50.0%), **1**: 1 (50.0%)
- **stock_status**: **In Stock**: 1 (50.0%), **Low Stock**: 1 (50.0%)
- **avg_daily_demand**: **0.6666666666666666**: 1 (50.0%), **36.666666666666664**: 1 (50.0%)
- **safety_stock**: **3.333333333333333**: 1 (50.0%), **256.66666666666663**: 1 (50.0%)
- **safety_stock_flag**: **0**: 1 (50.0%), **1**: 1 (50.0%)

---


## Table Profile: `products`
Dimensions: 2 rows × 21 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | str | 0 (0.0%) | 2 | 100.0% | 'p1' | N/A | N/A | N/A |
| `sku` | str | 0 (0.0%) | 2 | 100.0% | 'ELEC-LAP-001' | N/A | N/A | N/A |
| `name` | str | 0 (0.0%) | 2 | 100.0% | 'Test Laptop' | N/A | N/A | N/A |
| `category` | str | 0 (0.0%) | 1 | 50.0% | 'Electronics' | N/A | N/A | N/A |
| `unit_cost` | float64 | 0 (0.0%) | 2 | 100.0% | 10.00 | 500.00 | 255.00 | 346.48 |
| `reorder_point` | int64 | 0 (0.0%) | 2 | 100.0% | 5.00 | 10.00 | 7.50 | 3.54 |
| `created_at` | datetime64[us, UTC] | 0 (0.0%) | 1 | 50.0% | 2026-06-01 | 2026-06-01 | N/A | N/A |
| `lead_time_days` | int64 | 0 (0.0%) | 2 | 100.0% | 5.00 | 7.00 | 6.00 | 1.41 |
| `supplier_rating` | float64 | 0 (0.0%) | 2 | 100.0% | 3.00 | 4.50 | 3.75 | 1.06 |
| `current_stock_quantity` | int64 | 0 (0.0%) | 2 | 100.0% | 3.00 | 15.00 | 9.00 | 8.49 |
| `inventory_value` | float64 | 0 (0.0%) | 2 | 100.0% | 30.00 | 7500.00 | 3765.00 | 5282.09 |
| `avg_daily_demand` | float64 | 0 (0.0%) | 2 | 100.0% | 0.67 | 36.67 | 18.67 | 25.46 |
| `safety_stock` | float64 | 0 (0.0%) | 2 | 100.0% | 3.33 | 256.67 | 130.00 | 179.13 |
| `stock_status` | str | 0 (0.0%) | 2 | 100.0% | 'In Stock' | N/A | N/A | N/A |
| `reorder_required` | int64 | 0 (0.0%) | 2 | 100.0% | 0.00 | 1.00 | 0.50 | 0.71 |
| `safety_stock_flag` | int64 | 0 (0.0%) | 2 | 100.0% | 0.00 | 1.00 | 0.50 | 0.71 |
| `days_until_stockout` | float64 | 0 (0.0%) | 2 | 100.0% | 0.08 | 22.50 | 11.29 | 15.85 |
| `demand_category` | str | 0 (0.0%) | 2 | 100.0% | 'Low Demand' | N/A | N/A | N/A |
| `total_units_sold` | int64 | 0 (0.0%) | 2 | 100.0% | 2.00 | 110.00 | 56.00 | 76.37 |
| `cogs` | float64 | 0 (0.0%) | 2 | 100.0% | 1000.00 | 1100.00 | 1050.00 | 70.71 |
| `inventory_turnover` | float64 | 0 (0.0%) | 2 | 100.0% | 0.13 | 36.67 | 18.40 | 25.83 |

### Categorical Value Distributions
- **sku**: **ELEC-LAP-001**: 1 (50.0%), **ELEC-MOU-002**: 1 (50.0%)
- **name**: **Test Laptop**: 1 (50.0%), **Test Mouse**: 1 (50.0%)
- **category**: **Electronics**: 2 (100.0%)
- **unit_cost**: **500.0**: 1 (50.0%), **10.0**: 1 (50.0%)
- **reorder_point**: **10**: 1 (50.0%), **5**: 1 (50.0%)
- **created_at**: **2026-06-01 12:00:00+00:00**: 2 (100.0%)
- **lead_time_days**: **5**: 1 (50.0%), **7**: 1 (50.0%)
- **supplier_rating**: **4.5**: 1 (50.0%), **3.0**: 1 (50.0%)
- **current_stock_quantity**: **15**: 1 (50.0%), **3**: 1 (50.0%)
- **inventory_value**: **7500.0**: 1 (50.0%), **30.0**: 1 (50.0%)
- **avg_daily_demand**: **0.6666666666666666**: 1 (50.0%), **36.666666666666664**: 1 (50.0%)
- **safety_stock**: **3.333333333333333**: 1 (50.0%), **256.66666666666663**: 1 (50.0%)
- **stock_status**: **In Stock**: 1 (50.0%), **Low Stock**: 1 (50.0%)
- **reorder_required**: **0**: 1 (50.0%), **1**: 1 (50.0%)
- **safety_stock_flag**: **0**: 1 (50.0%), **1**: 1 (50.0%)
- **days_until_stockout**: **22.5**: 1 (50.0%), **0.08181818181818182**: 1 (50.0%)
- **demand_category**: **Low Demand**: 1 (50.0%), **High Demand**: 1 (50.0%)
- **total_units_sold**: **2**: 1 (50.0%), **110**: 1 (50.0%)
- **cogs**: **1000.0**: 1 (50.0%), **1100.0**: 1 (50.0%)
- **inventory_turnover**: **0.13333333333333333**: 1 (50.0%), **36.666666666666664**: 1 (50.0%)

---


## Table Profile: `purchase_orders`
Dimensions: 1 rows × 18 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `po_id` | str | 0 (0.0%) | 1 | 100.0% | 'po1' | N/A | N/A | N/A |
| `supplier_id` | str | 0 (0.0%) | 1 | 100.0% | 's1' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 1 | 100.0% | 'p1' | N/A | N/A | N/A |
| `quantity` | int64 | 0 (0.0%) | 1 | 100.0% | 20.00 | 20.00 | 20.00 | 0.00 |
| `unit_cost` | float64 | 0 (0.0%) | 1 | 100.0% | 500.00 | 500.00 | 500.00 | 0.00 |
| `order_date` | datetime64[us] | 0 (0.0%) | 1 | 100.0% | 2026-06-15 | 2026-06-15 | N/A | N/A |
| `expected_delivery` | datetime64[us] | 0 (0.0%) | 1 | 100.0% | 2026-06-22 | 2026-06-22 | N/A | N/A |
| `actual_delivery` | datetime64[us] | 0 (0.0%) | 1 | 100.0% | 2026-06-21 | 2026-06-21 | N/A | N/A |
| `status` | str | 0 (0.0%) | 1 | 100.0% | 'Received' | N/A | N/A | N/A |
| `notes` | str | 0 (0.0%) | 1 | 100.0% | 'Urgent' | N/A | N/A | N/A |
| `created_at` | datetime64[us, UTC] | 0 (0.0%) | 1 | 100.0% | 2026-06-15 | 2026-06-15 | N/A | N/A |
| `week` | int64 | 0 (0.0%) | 1 | 100.0% | 25.00 | 25.00 | 25.00 | 0.00 |
| `month` | int64 | 0 (0.0%) | 1 | 100.0% | 6.00 | 6.00 | 6.00 | 0.00 |
| `quarter` | int64 | 0 (0.0%) | 1 | 100.0% | 2.00 | 2.00 | 2.00 | 0.00 |
| `year` | int64 | 0 (0.0%) | 1 | 100.0% | 2026.00 | 2026.00 | 2026.00 | 0.00 |
| `day_of_week` | int64 | 0 (0.0%) | 1 | 100.0% | 0.00 | 0.00 | 0.00 | 0.00 |
| `weekend_indicator` | int64 | 0 (0.0%) | 1 | 100.0% | 0.00 | 0.00 | 0.00 | 0.00 |
| `season` | str | 0 (0.0%) | 1 | 100.0% | 'Summer' | N/A | N/A | N/A |

### Categorical Value Distributions
- **supplier_id**: **s1**: 1 (100.0%)
- **product_id**: **p1**: 1 (100.0%)
- **quantity**: **20**: 1 (100.0%)
- **unit_cost**: **500.0**: 1 (100.0%)
- **order_date**: **2026-06-15 00:00:00**: 1 (100.0%)
- **expected_delivery**: **2026-06-22 00:00:00**: 1 (100.0%)
- **actual_delivery**: **2026-06-21 00:00:00**: 1 (100.0%)
- **status**: **Received**: 1 (100.0%)
- **notes**: **Urgent**: 1 (100.0%)
- **created_at**: **2026-06-15 12:00:00+00:00**: 1 (100.0%)
- **week**: **25**: 1 (100.0%)
- **month**: **6**: 1 (100.0%)
- **quarter**: **2**: 1 (100.0%)
- **year**: **2026**: 1 (100.0%)
- **day_of_week**: **0**: 1 (100.0%)
- **weekend_indicator**: **0**: 1 (100.0%)
- **season**: **Summer**: 1 (100.0%)

---


## Table Profile: `sales`
Dimensions: 3 rows × 20 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sale_id` | str | 0 (0.0%) | 3 | 100.0% | 'sa1' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 2 | 66.7% | 'p1' | N/A | N/A | N/A |
| `sale_date` | datetime64[us] | 0 (0.0%) | 3 | 100.0% | 2026-07-02 | 2026-07-04 | N/A | N/A |
| `quantity` | int64 | 0 (0.0%) | 3 | 100.0% | 2.00 | 100.00 | 37.33 | 54.42 |
| `unit_price` | float64 | 0 (0.0%) | 2 | 66.7% | 20.00 | 750.00 | 263.33 | 421.47 |
| `customer_type` | str | 0 (0.0%) | 2 | 66.7% | 'Retail' | N/A | N/A | N/A |
| `created_at` | datetime64[us, UTC] | 0 (0.0%) | 3 | 100.0% | 2026-07-02 | 2026-07-04 | N/A | N/A |
| `unit_cost` | float64 | 0 (0.0%) | 2 | 66.7% | 10.00 | 500.00 | 173.33 | 282.90 |
| `revenue` | float64 | 0 (0.0%) | 3 | 100.0% | 200.00 | 2000.00 | 1233.33 | 929.16 |
| `profit` | float64 | 0 (0.0%) | 3 | 100.0% | 100.00 | 1000.00 | 533.33 | 450.92 |
| `profit_margin` | float64 | 0 (0.0%) | 2 | 66.7% | 0.33 | 0.50 | 0.44 | 0.10 |
| `week` | int64 | 0 (0.0%) | 1 | 33.3% | 27.00 | 27.00 | 27.00 | 0.00 |
| `month` | int64 | 0 (0.0%) | 1 | 33.3% | 7.00 | 7.00 | 7.00 | 0.00 |
| `quarter` | int64 | 0 (0.0%) | 1 | 33.3% | 3.00 | 3.00 | 3.00 | 0.00 |
| `year` | int64 | 0 (0.0%) | 1 | 33.3% | 2026.00 | 2026.00 | 2026.00 | 0.00 |
| `day_of_week` | int64 | 0 (0.0%) | 3 | 100.0% | 3.00 | 5.00 | 4.00 | 1.00 |
| `weekend_indicator` | int64 | 0 (0.0%) | 2 | 66.7% | 0.00 | 1.00 | 0.33 | 0.58 |
| `season` | str | 0 (0.0%) | 1 | 33.3% | 'Summer' | N/A | N/A | N/A |
| `rolling_sales_7d` | float64 | 0 (0.0%) | 3 | 100.0% | 2.00 | 110.00 | 40.67 | 60.18 |
| `rolling_sales_30d` | float64 | 0 (0.0%) | 3 | 100.0% | 2.00 | 110.00 | 40.67 | 60.18 |

### Categorical Value Distributions
- **product_id**: **p2**: 2 (66.7%), **p1**: 1 (33.3%)
- **sale_date**: **2026-07-02 00:00:00**: 1 (33.3%), **2026-07-03 00:00:00**: 1 (33.3%), **2026-07-04 00:00:00**: 1 (33.3%)
- **quantity**: **2**: 1 (33.3%), **10**: 1 (33.3%), **100**: 1 (33.3%)
- **unit_price**: **20.0**: 2 (66.7%), **750.0**: 1 (33.3%)
- **customer_type**: **Wholesale**: 2 (66.7%), **Retail**: 1 (33.3%)
- **created_at**: **2026-07-02 18:00:00+00:00**: 1 (33.3%), **2026-07-03 18:00:00+00:00**: 1 (33.3%), **2026-07-04 18:00:00+00:00**: 1 (33.3%)
- **unit_cost**: **10.0**: 2 (66.7%), **500.0**: 1 (33.3%)
- **revenue**: **1500.0**: 1 (33.3%), **200.0**: 1 (33.3%), **2000.0**: 1 (33.3%)
- **profit**: **500.0**: 1 (33.3%), **100.0**: 1 (33.3%), **1000.0**: 1 (33.3%)
- **profit_margin**: **0.5**: 2 (66.7%), **0.3333333333333333**: 1 (33.3%)
- **week**: **27**: 3 (100.0%)
- **month**: **7**: 3 (100.0%)
- **quarter**: **3**: 3 (100.0%)
- **year**: **2026**: 3 (100.0%)
- **day_of_week**: **3**: 1 (33.3%), **4**: 1 (33.3%), **5**: 1 (33.3%)
- **weekend_indicator**: **0**: 2 (66.7%), **1**: 1 (33.3%)
- **season**: **Summer**: 3 (100.0%)
- **rolling_sales_7d**: **2.0**: 1 (33.3%), **10.0**: 1 (33.3%), **110.0**: 1 (33.3%)
- **rolling_sales_30d**: **2.0**: 1 (33.3%), **10.0**: 1 (33.3%), **110.0**: 1 (33.3%)

---


## Table Profile: `suppliers`
Dimensions: 1 rows × 8 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `supplier_id` | str | 0 (0.0%) | 1 | 100.0% | 's1' | N/A | N/A | N/A |
| `name` | str | 0 (0.0%) | 1 | 100.0% | 'TechSupplier Ltd' | N/A | N/A | N/A |
| `contact_person` | str | 0 (0.0%) | 1 | 100.0% | 'John' | N/A | N/A | N/A |
| `contact_email` | str | 0 (0.0%) | 1 | 100.0% | 'john@tech.com' | N/A | N/A | N/A |
| `contact_phone` | str | 0 (0.0%) | 1 | 100.0% | '123' | N/A | N/A | N/A |
| `lead_time_days` | int64 | 0 (0.0%) | 1 | 100.0% | 5.00 | 5.00 | 5.00 | 0.00 |
| `rating` | float64 | 0 (0.0%) | 1 | 100.0% | 4.50 | 4.50 | 4.50 | 0.00 |
| `created_at` | datetime64[us, UTC] | 0 (0.0%) | 1 | 100.0% | 2026-06-01 | 2026-06-01 | N/A | N/A |

### Categorical Value Distributions
- **name**: **TechSupplier Ltd**: 1 (100.0%)
- **contact_person**: **John**: 1 (100.0%)
- **contact_email**: **john@tech.com**: 1 (100.0%)
- **contact_phone**: **123**: 1 (100.0%)
- **lead_time_days**: **5**: 1 (100.0%)
- **rating**: **4.5**: 1 (100.0%)
- **created_at**: **2026-06-01 12:00:00+00:00**: 1 (100.0%)

---

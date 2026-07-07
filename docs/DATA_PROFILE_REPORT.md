# Data Profile Report

**Execution Timestamp:** 2026-07-07 19:59:33

This document provides structural, statistical, and memory profiles of the operational datasets.

## 1. Executive Summary
High-level metrics across all tables:

| Table Name | Rows | Columns | Memory Usage (KB) | Duplicate % | Missing Values % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `audit_logs` | 28 | 9 | 7.08 KB | 0.00% | 12.70% |
| `forecasts` | 1 | 8 | 0.27 KB | 0.00% | 0.00% |
| `inventory` | 50 | 13 | 9.67 KB | 0.00% | 7.54% |
| `products` | 51 | 21 | 12.60 KB | 0.00% | 0.09% |
| `purchase_orders` | 105 | 18 | 32.65 KB | 0.00% | 1.06% |
| `sales` | 906 | 20 | 217.18 KB | 0.00% | 0.03% |
| `suppliers` | 10 | 8 | 1.81 KB | 0.00% | 0.00% |
| **Total / Summary** | **1,151** | **N/A** | **281.27 KB** | **N/A** | **N/A** |

---

## Table Profile: `audit_logs`
Dimensions: 28 rows × 9 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `log_id` | str | 0 (0.0%) | 28 | 100.0% | 'c6aa23c0-b16a-47e...' | N/A | N/A | N/A |
| `user_id` | str | 0 (0.0%) | 5 | 17.9% | '2e7baa97-6629-4cc...' | N/A | N/A | N/A |
| `action` | str | 0 (0.0%) | 5 | 17.9% | 'UPDATE' | N/A | N/A | N/A |
| `entity` | str | 0 (0.0%) | 6 | 21.4% | 'products' | N/A | N/A | N/A |
| `entity_id` | str | 0 (0.0%) | 25 | 89.3% | '53aebf1e-27db-427...' | N/A | N/A | N/A |
| `old_value` | str | 6 (21.4%) | 11 | 39.3% | '{"status": "old_v...' | N/A | N/A | N/A |
| `new_value` | str | 0 (0.0%) | 11 | 39.3% | '{"status": "new_v...' | N/A | N/A | N/A |
| `ip_address` | str | 13 (46.4%) | 13 | 46.4% | '192.168.1.61' | N/A | N/A | N/A |
| `timestamp` | datetime64[us] | 13 (46.4%) | 12 | 42.9% | 2026-06-01 | 2026-06-29 | N/A | N/A |

### Categorical Value Distributions
- **user_id**: **905ff118-4b04-4781-9ab3-1ec803c4652d**: 15 (53.6%), **0c579af2-e1f1-47bc-ad3d-11b1edb0a44e**: 4 (14.3%), **2e7baa97-6629-4cc6-be6e-d49e6083aad9**: 3 (10.7%), **86c5112d-74cb-4ba8-818b-bedb93b474e5**: 3 (10.7%), **31920732-5968-4185-9d95-1bdea258b492**: 3 (10.7%)
- **action**: **UPDATE**: 9 (32.1%), **CREATE**: 6 (21.4%), **CREATE_SALE**: 5 (17.9%), **PO_RECEIVED_STOCK_ADD**: 4 (14.3%), **UPDATE_PO_STATUS**: 4 (14.3%)
- **entity**: **inventory**: 10 (35.7%), **suppliers**: 5 (17.9%), **sales**: 5 (17.9%), **purchase_orders**: 4 (14.3%), **products**: 2 (7.1%), **users**: 2 (7.1%)

---


## Table Profile: `forecasts`
Dimensions: 1 rows × 8 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `forecast_id` | str | 0 (0.0%) | 1 | 100.0% | '6f7defb2-0a1c-4c6...' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 1 | 100.0% | 'decd0138-4c04-4f1...' | N/A | N/A | N/A |
| `forecast_date` | datetime64[us] | 0 (0.0%) | 1 | 100.0% | 2026-07-30 | 2026-07-30 | N/A | N/A |
| `predicted_qty` | int64 | 0 (0.0%) | 1 | 100.0% | 11.00 | 11.00 | 11.00 | 0.00 |
| `confidence_low` | int64 | 0 (0.0%) | 1 | 100.0% | 0.00 | 0.00 | 0.00 | 0.00 |
| `confidence_high` | int64 | 0 (0.0%) | 1 | 100.0% | 138.00 | 138.00 | 138.00 | 0.00 |
| `model_used` | str | 0 (0.0%) | 1 | 100.0% | 'ARIMA' | N/A | N/A | N/A |
| `generated_at` | datetime64[us, UTC] | 0 (0.0%) | 1 | 100.0% | 2026-06-30 | 2026-06-30 | N/A | N/A |

### Categorical Value Distributions
- **product_id**: **decd0138-4c04-4f18-8d2d-c85371011a15**: 1 (100.0%)
- **forecast_date**: **2026-07-30 00:00:00**: 1 (100.0%)
- **predicted_qty**: **11**: 1 (100.0%)
- **confidence_low**: **0**: 1 (100.0%)
- **confidence_high**: **138**: 1 (100.0%)
- **model_used**: **ARIMA**: 1 (100.0%)
- **generated_at**: **2026-06-30 13:04:09.032000+00:00**: 1 (100.0%)

---


## Table Profile: `inventory`
Dimensions: 50 rows × 13 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `inventory_id` | str | 0 (0.0%) | 50 | 100.0% | '4b6c0659-db6e-461...' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 50 | 100.0% | 'decd0138-4c04-4f1...' | N/A | N/A | N/A |
| `location` | str | 0 (0.0%) | 2 | 4.0% | 'Warehouse-A' | N/A | N/A | N/A |
| `quantity` | int64 | 0 (0.0%) | 45 | 90.0% | 19.00 | 299.00 | 180.96 | 89.15 |
| `last_updated` | datetime64[us, UTC] | 49 (98.0%) | 1 | 2.0% | 2026-06-30 | 2026-06-30 | N/A | N/A |
| `unit_cost` | float64 | 0 (0.0%) | 50 | 100.0% | 49.29 | 12594.31 | 1773.31 | 2893.64 |
| `reorder_point` | int64 | 0 (0.0%) | 5 | 10.0% | 5.00 | 30.00 | 16.10 | 7.78 |
| `inventory_value` | float64 | 0 (0.0%) | 50 | 100.0% | 6749.34 | 3118720.80 | 304863.51 | 577618.83 |
| `reorder_required` | int64 | 0 (0.0%) | 1 | 2.0% | 0.00 | 0.00 | 0.00 | 0.00 |
| `stock_status` | str | 0 (0.0%) | 1 | 2.0% | 'In Stock' | N/A | N/A | N/A |
| `avg_daily_demand` | float64 | 0 (0.0%) | 48 | 96.0% | 0.20 | 1.09 | 0.63 | 0.21 |
| `safety_stock` | float64 | 0 (0.0%) | 50 | 100.0% | 1.18 | 12.43 | 5.71 | 2.81 |
| `safety_stock_flag` | int64 | 0 (0.0%) | 1 | 2.0% | 0.00 | 0.00 | 0.00 | 0.00 |

### Categorical Value Distributions
- **location**: **Warehouse-A**: 27 (54.0%), **Warehouse-B**: 23 (46.0%)
- **last_updated**: **NaT**: 49 (98.0%), **2026-06-30 13:04:06.946000+00:00**: 1 (2.0%)
- **reorder_point**: **15**: 14 (28.0%), **20**: 11 (22.0%), **10**: 10 (20.0%), **30**: 8 (16.0%), **5**: 7 (14.0%)
- **reorder_required**: **0**: 50 (100.0%)
- **stock_status**: **In Stock**: 50 (100.0%)
- **safety_stock_flag**: **0**: 50 (100.0%)

---


## Table Profile: `products`
Dimensions: 51 rows × 21 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | str | 0 (0.0%) | 51 | 100.0% | 'decd0138-4c04-4f1...' | N/A | N/A | N/A |
| `sku` | str | 0 (0.0%) | 51 | 100.0% | 'ELE-101' | N/A | N/A | N/A |
| `name` | str | 0 (0.0%) | 51 | 100.0% | 'Smartphone X' | N/A | N/A | N/A |
| `category` | str | 0 (0.0%) | 5 | 9.8% | 'Electronics' | N/A | N/A | N/A |
| `unit_cost` | float64 | 0 (0.0%) | 51 | 100.0% | 49.29 | 12594.31 | 1740.50 | 2874.13 |
| `reorder_point` | int64 | 0 (0.0%) | 5 | 9.8% | 5.00 | 30.00 | 15.88 | 7.86 |
| `created_at` | datetime64[us] | 1 (2.0%) | 1 | 2.0% | 2025-06-30 | 2025-06-30 | N/A | N/A |
| `lead_time_days` | int64 | 0 (0.0%) | 9 | 17.6% | 5.00 | 14.00 | 8.90 | 2.90 |
| `supplier_rating` | float64 | 0 (0.0%) | 8 | 15.7% | 3.00 | 4.80 | 3.91 | 0.60 |
| `current_stock_quantity` | int64 | 0 (0.0%) | 46 | 90.2% | 0.00 | 299.00 | 177.41 | 91.82 |
| `inventory_value` | float64 | 0 (0.0%) | 51 | 100.0% | 0.00 | 3118720.80 | 298885.80 | 573404.77 |
| `avg_daily_demand` | float64 | 0 (0.0%) | 49 | 96.1% | 0.00 | 1.09 | 0.62 | 0.22 |
| `safety_stock` | float64 | 0 (0.0%) | 51 | 100.0% | 0.00 | 12.43 | 5.60 | 2.89 |
| `stock_status` | str | 0 (0.0%) | 2 | 3.9% | 'In Stock' | N/A | N/A | N/A |
| `reorder_required` | int64 | 0 (0.0%) | 2 | 3.9% | 0.00 | 1.00 | 0.02 | 0.14 |
| `safety_stock_flag` | int64 | 0 (0.0%) | 1 | 2.0% | 0.00 | 0.00 | 0.00 | 0.00 |
| `days_until_stockout` | float64 | 0 (0.0%) | 51 | 100.0% | 23.78 | 999.00 | 330.26 | 214.76 |
| `demand_category` | str | 0 (0.0%) | 4 | 7.8% | 'Low Demand' | N/A | N/A | N/A |
| `total_units_sold` | float64 | 0 (0.0%) | 49 | 96.1% | 0.00 | 397.62 | 226.80 | 81.67 |
| `cogs` | float64 | 0 (0.0%) | 51 | 100.0% | 0.00 | 2140700.90 | 349692.35 | 510660.67 |
| `inventory_turnover` | float64 | 0 (0.0%) | 51 | 100.0% | 0.00 | 15.35 | 2.08 | 2.56 |

### Categorical Value Distributions
- **category**: **Electronics**: 11 (21.6%), **Food**: 10 (19.6%), **Apparel**: 10 (19.6%), **Home**: 10 (19.6%), **Sports**: 10 (19.6%)
- **reorder_point**: **15**: 14 (27.5%), **20**: 11 (21.6%), **10**: 10 (19.6%), **5**: 8 (15.7%), **30**: 8 (15.7%)
- **created_at**: **2025-06-30 16:59:27.379356**: 50 (98.0%), **NaT**: 1 (2.0%)
- **lead_time_days**: **8**: 9 (17.6%), **7**: 9 (17.6%), **13**: 8 (15.7%), **5**: 7 (13.7%), **10**: 5 (9.8%), **12**: 5 (9.8%), **6**: 4 (7.8%), **9**: 2 (3.9%), **14**: 2 (3.9%)
- **supplier_rating**: **3.8**: 10 (19.6%), **3.0**: 9 (17.6%), **3.6**: 8 (15.7%), **4.6**: 7 (13.7%), **4.5**: 5 (9.8%), **4.8**: 4 (7.8%), **3.5**: 4 (7.8%), **4.4**: 4 (7.8%)
- **stock_status**: **In Stock**: 50 (98.0%), **Out Of Stock**: 1 (2.0%)
- **reorder_required**: **0**: 50 (98.0%), **1**: 1 (2.0%)
- **safety_stock_flag**: **0**: 51 (100.0%)
- **demand_category**: **Medium Demand**: 24 (47.1%), **Low Demand**: 13 (25.5%), **High Demand**: 13 (25.5%), **No Demand**: 1 (2.0%)

---


## Table Profile: `purchase_orders`
Dimensions: 105 rows × 18 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `po_id` | str | 0 (0.0%) | 105 | 100.0% | '986b52a5-70cc-489...' | N/A | N/A | N/A |
| `supplier_id` | str | 0 (0.0%) | 10 | 9.5% | '7b41de90-a439-4ce...' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 42 | 40.0% | 'f610623d-a4d4-477...' | N/A | N/A | N/A |
| `quantity` | int64 | 0 (0.0%) | 76 | 72.4% | 20.00 | 200.00 | 111.99 | 43.10 |
| `unit_cost` | float64 | 0 (0.0%) | 44 | 41.9% | 49.29 | 12594.31 | 1378.47 | 2258.14 |
| `order_date` | datetime64[us] | 0 (0.0%) | 88 | 83.8% | 2025-07-10 | 2026-06-30 | N/A | N/A |
| `expected_delivery` | datetime64[us] | 0 (0.0%) | 88 | 83.8% | 2025-07-17 | 2026-07-20 | N/A | N/A |
| `actual_delivery` | datetime64[us] | 15 (14.3%) | 76 | 72.4% | 2025-07-16 | 2026-07-10 | N/A | N/A |
| `status` | str | 0 (0.0%) | 4 | 3.8% | 'Received' | N/A | N/A | N/A |
| `notes` | str | 0 (0.0%) | 10 | 9.5% | 'Auto-generated re...' | N/A | N/A | N/A |
| `created_at` | datetime64[us] | 5 (4.8%) | 87 | 82.9% | 2025-07-10 | 2026-06-15 | N/A | N/A |
| `week` | int64 | 0 (0.0%) | 42 | 40.0% | 1.00 | 52.00 | 27.61 | 13.92 |
| `month` | int64 | 0 (0.0%) | 12 | 11.4% | 1.00 | 12.00 | 6.75 | 3.22 |
| `quarter` | int64 | 0 (0.0%) | 4 | 3.8% | 1.00 | 4.00 | 2.56 | 1.07 |
| `year` | int64 | 0 (0.0%) | 2 | 1.9% | 2025.00 | 2026.00 | 2025.49 | 0.50 |
| `day_of_week` | int64 | 0 (0.0%) | 7 | 6.7% | 0.00 | 6.00 | 2.81 | 1.91 |
| `weekend_indicator` | int64 | 0 (0.0%) | 2 | 1.9% | 0.00 | 1.00 | 0.27 | 0.44 |
| `season` | str | 0 (0.0%) | 4 | 3.8% | 'Autumn' | N/A | N/A | N/A |

### Categorical Value Distributions
- **status**: **Received**: 90 (85.7%), **Cancelled**: 13 (12.4%), **Sent**: 1 (1.0%), **Pending**: 1 (1.0%)
- **quarter**: **2**: 30 (28.6%), **3**: 28 (26.7%), **4**: 26 (24.8%), **1**: 21 (20.0%)
- **year**: **2025**: 54 (51.4%), **2026**: 51 (48.6%)
- **day_of_week**: **3**: 22 (21.0%), **1**: 22 (21.0%), **5**: 19 (18.1%), **0**: 13 (12.4%), **2**: 11 (10.5%), **4**: 9 (8.6%), **6**: 9 (8.6%)
- **weekend_indicator**: **0**: 77 (73.3%), **1**: 28 (26.7%)
- **season**: **Spring**: 32 (30.5%), **Autumn**: 30 (28.6%), **Summer**: 25 (23.8%), **Winter**: 18 (17.1%)

---


## Table Profile: `sales`
Dimensions: 906 rows × 20 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sale_id` | str | 0 (0.0%) | 906 | 100.0% | '5364d0fe-d5e3-436...' | N/A | N/A | N/A |
| `product_id` | str | 0 (0.0%) | 50 | 5.5% | 'decd0138-4c04-4f1...' | N/A | N/A | N/A |
| `sale_date` | datetime64[us] | 0 (0.0%) | 336 | 37.1% | 2025-07-01 | 2026-06-30 | N/A | N/A |
| `quantity` | float64 | 0 (0.0%) | 37 | 4.1% | 1.00 | 40.88 | 12.77 | 12.75 |
| `unit_price` | float64 | 0 (0.0%) | 101 | 11.1% | 56.11 | 16848.89 | 2305.32 | 3855.81 |
| `customer_type` | str | 0 (0.0%) | 2 | 0.2% | 'Retail' | N/A | N/A | N/A |
| `created_at` | datetime64[us] | 5 (0.6%) | 335 | 37.0% | 2025-07-01 | 2026-06-29 | N/A | N/A |
| `unit_cost` | float64 | 0 (0.0%) | 50 | 5.5% | 49.29 | 12594.31 | 1781.92 | 2860.24 |
| `revenue` | float64 | 0 (0.0%) | 570 | 62.9% | 66.01 | 565790.52 | 24331.70 | 54523.52 |
| `profit` | float64 | 0 (0.0%) | 570 | 62.9% | -6224.89 | 118500.30 | 4647.03 | 10973.76 |
| `profit_margin` | float64 | 0 (0.0%) | 318 | 35.1% | -4.15 | 0.33 | 0.19 | 0.30 |
| `week` | int64 | 0 (0.0%) | 52 | 5.7% | 1.00 | 52.00 | 25.74 | 14.94 |
| `month` | int64 | 0 (0.0%) | 12 | 1.3% | 1.00 | 12.00 | 6.32 | 3.45 |
| `quarter` | int64 | 0 (0.0%) | 4 | 0.4% | 1.00 | 4.00 | 2.44 | 1.11 |
| `year` | int64 | 0 (0.0%) | 2 | 0.2% | 2025.00 | 2026.00 | 2025.53 | 0.50 |
| `day_of_week` | int64 | 0 (0.0%) | 7 | 0.8% | 0.00 | 6.00 | 2.92 | 2.02 |
| `weekend_indicator` | int64 | 0 (0.0%) | 2 | 0.2% | 0.00 | 1.00 | 0.28 | 0.45 |
| `season` | str | 0 (0.0%) | 4 | 0.4% | 'Summer' | N/A | N/A | N/A |
| `rolling_sales_7d` | float64 | 0 (0.0%) | 78 | 8.6% | 1.00 | 98.88 | 16.83 | 16.56 |
| `rolling_sales_30d` | float64 | 0 (0.0%) | 146 | 16.1% | 1.00 | 170.75 | 29.93 | 25.19 |

### Categorical Value Distributions
- **customer_type**: **Retail**: 659 (72.7%), **Wholesale**: 247 (27.3%)
- **quarter**: **2**: 244 (26.9%), **1**: 235 (25.9%), **3**: 219 (24.2%), **4**: 208 (23.0%)
- **year**: **2026**: 479 (52.9%), **2025**: 427 (47.1%)
- **day_of_week**: **0**: 143 (15.8%), **2**: 140 (15.5%), **5**: 136 (15.0%), **1**: 129 (14.2%), **6**: 121 (13.4%), **4**: 119 (13.1%), **3**: 118 (13.0%)
- **weekend_indicator**: **0**: 649 (71.6%), **1**: 257 (28.4%)
- **season**: **Spring**: 253 (27.9%), **Winter**: 231 (25.5%), **Autumn**: 213 (23.5%), **Summer**: 209 (23.1%)

---


## Table Profile: `suppliers`
Dimensions: 10 rows × 8 columns.

| Column Name | Data Type | Nulls (%) | Unique Count | Cardinality % | Min Value | Max Value | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `supplier_id` | str | 0 (0.0%) | 10 | 100.0% | '7949e3c9-1cd5-4a5...' | N/A | N/A | N/A |
| `name` | str | 0 (0.0%) | 10 | 100.0% | 'Supplier 1 (Sports)' | N/A | N/A | N/A |
| `contact_person` | str | 0 (0.0%) | 10 | 100.0% | 'Contact Person 1' | N/A | N/A | N/A |
| `contact_email` | str | 0 (0.0%) | 10 | 100.0% | 'contact1@supplier...' | N/A | N/A | N/A |
| `contact_phone` | str | 0 (0.0%) | 10 | 100.0% | '+91 9876500001' | N/A | N/A | N/A |
| `lead_time_days` | int64 | 0 (0.0%) | 8 | 80.0% | 5.00 | 14.00 | 9.00 | 3.23 |
| `rating` | float64 | 0 (0.0%) | 7 | 70.0% | 3.50 | 4.80 | 4.20 | 0.47 |
| `created_at` | datetime64[us] | 0 (0.0%) | 1 | 10.0% | 2026-06-30 | 2026-06-30 | N/A | N/A |

### Categorical Value Distributions
- **lead_time_days**: **8**: 2 (20.0%), **5**: 2 (20.0%), **10**: 1 (10.0%), **9**: 1 (10.0%), **14**: 1 (10.0%), **6**: 1 (10.0%), **12**: 1 (10.0%), **13**: 1 (10.0%)
- **rating**: **4.6**: 2 (20.0%), **4.4**: 2 (20.0%), **3.8**: 2 (20.0%), **3.5**: 1 (10.0%), **4.8**: 1 (10.0%), **4.5**: 1 (10.0%), **3.6**: 1 (10.0%)
- **created_at**: **2026-06-30 16:59:27.379356**: 10 (100.0%)

---

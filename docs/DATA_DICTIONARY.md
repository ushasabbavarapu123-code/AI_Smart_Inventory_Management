# Data Dictionary

This document provides technical schemas, definitions, and business rules for the processed datasets in the inventory management system.

*Generated automatically by the ETL data pipeline.*

## Table: `audit_logs`
Contains 1 rows and 9 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `log_id` | String (UUID) | No | `l1m2n3o4-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for audit log entry. |
| `action` | String | No | `CREATE_SALE` | Action description. |
| `entity` | String | No | `sales` | Database entity/table name affected. |
| `entity_id` | String (UUID) | No | `a8b9c0d1...` | Record ID of the affected entity. |
| `user_id` | String (UUID) | No | `u1v2w3x4-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the user account. |
| `old_value` | String | Yes | `{'quantity': 50}` | Serialized values before change. |
| `new_value` | String | Yes | `{'quantity': 48}` | Serialized values after change. |
| `ip_address` | String | Yes | `127.0.0.1` | Client IP address. |
| `timestamp` | Datetime | No | `2026-07-07T18:00:00Z` | Log entry timestamp. |

---

## Table: `forecasts`
Contains 1 rows and 8 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `forecast_id` | String (UUID) | No | `d4e5f6a7-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the forecast record. |
| `product_id` | String (UUID) | No | `f3b20c91-d824-4fca-8600-0e12361254ff` | Unique identifier for the product record. |
| `forecast_date` | Date (YYYY-MM-DD) | No | `2026-08-01` | Target date of predicted demand. |
| `predicted_qty` | Float | No | `50.0` | Forecasted demand quantity. |
| `confidence_low` | Float | No | `35.0` | Lower boundary of forecast confidence interval. |
| `confidence_high` | Float | No | `65.0` | Upper boundary of forecast confidence interval. |
| `model_used` | String | No | `ARIMA` | Forecasting algorithm used (ARIMA, MovingAverage). |
| `generated_at` | Datetime | No | `2026-07-07T12:00:00Z` | Timestamp of forecast calculation. |

---

## Table: `inventory`
Contains 2 rows and 13 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `inventory_id` | String (UUID) | No | `d9c3b1a2-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the inventory record. |
| `product_id` | String (UUID) | No | `f3b20c91-d824-4fca-8600-0e12361254ff` | Unique identifier for the product record. |
| `quantity` | int64 | No | `15` | Self-explanatory operational or engineered feature column. |
| `location` | String | No | `Warehouse-A` | Physical storage location. |
| `last_updated` | Datetime | No | `2026-07-01T15:30:00Z` | Timestamp of last stock update. |
| `unit_cost` | Float | No | `750.00` | Cost price per unit from supplier. |
| `reorder_point` | Integer | No | `15` | Stock threshold to trigger reorder. |
| `inventory_value` | Float | No | `33750.00` | Calculated value of stock (quantity * unit_cost). |
| `reorder_required` | Integer (Binary) | No | `0` | Flag indicating if quantity <= reorder_point (1=Yes, 0=No). |
| `stock_status` | String | No | `In Stock` | Stock level status: In Stock, Low Stock, Out Of Stock. |
| `avg_daily_demand` | Float | No | `3.50` | Average quantity sold per day (including zero sales days). |
| `safety_stock` | Float | No | `24.5` | Calculated safety stock (avg_daily_demand * lead_time_days). |
| `safety_stock_flag` | Integer (Binary) | No | `0` | Flag indicating if current quantity < safety stock (1=Yes, 0=No). |

---

## Table: `products`
Contains 2 rows and 21 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `product_id` | String (UUID) | No | `f3b20c91-d824-4fca-8600-0e12361254ff` | Unique identifier for the product record. |
| `sku` | String | No | `ELEC-LAP-001` | Unique Stock Keeping Unit code. |
| `name` | String | No | `Pro Laptop 15-inch` | Descriptive title of the product. |
| `category` | String | No | `Electronics` | Business classification of the item. |
| `unit_cost` | Float | No | `750.00` | Cost price per unit from supplier. |
| `reorder_point` | Integer | No | `15` | Stock threshold to trigger reorder. |
| `created_at` | Datetime | No | `2026-06-01T12:00:00Z` | Timestamp of record creation. |
| `lead_time_days` | Integer | No | `7` | Supplier delivery lead time in days. |
| `supplier_rating` | Float | No | `4.5` | Mapped rating for reporting. |
| `current_stock_quantity` | Integer | No | `45` | Total current stock across warehouses (computed). |
| `inventory_value` | Float | No | `33750.00` | Calculated value of stock (quantity * unit_cost). |
| `avg_daily_demand` | Float | No | `3.50` | Average quantity sold per day (including zero sales days). |
| `safety_stock` | Float | No | `24.5` | Calculated safety stock (avg_daily_demand * lead_time_days). |
| `stock_status` | String | No | `In Stock` | Stock level status: In Stock, Low Stock, Out Of Stock. |
| `reorder_required` | Integer (Binary) | No | `0` | Flag indicating if quantity <= reorder_point (1=Yes, 0=No). |
| `safety_stock_flag` | Integer (Binary) | No | `0` | Flag indicating if current quantity < safety stock (1=Yes, 0=No). |
| `days_until_stockout` | Float | No | `12.8` | Estimated days before stock hits zero (quantity / avg_daily_demand). |
| `demand_category` | String | No | `High Demand` | Demand level percentile classification. |
| `total_units_sold` | Integer | No | `20` | Total quantities sold historically. |
| `cogs` | Float | No | `15000.00` | Cost of Goods Sold (total units sold * unit_cost). |
| `inventory_turnover` | Float | No | `4.2` | Turnover ratio (COGS / current inventory value). |

---

## Table: `purchase_orders`
Contains 1 rows and 18 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `po_id` | String (UUID) | No | `c8d9e0f1-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the purchase order. |
| `supplier_id` | String (UUID) | No | `b4a3c2d1-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the supplier record. |
| `product_id` | String (UUID) | No | `f3b20c91-d824-4fca-8600-0e12361254ff` | Unique identifier for the product record. |
| `quantity` | int64 | No | `20` | Self-explanatory operational or engineered feature column. |
| `unit_cost` | Float | No | `750.00` | Cost price per unit from supplier. |
| `order_date` | Date (YYYY-MM-DD) | No | `2026-06-15` | Date when the order was placed. |
| `expected_delivery` | Date (YYYY-MM-DD) | No | `2026-06-22` | Date order is expected to arrive. |
| `actual_delivery` | Date (YYYY-MM-DD) | Yes | `2026-06-21` | Date order was actually delivered. |
| `status` | String | No | `Received` | Purchase order status: Pending, Shipped, Received, Cancelled. |
| `notes` | String | Yes | `Urgent delivery requested.` | Internal notes for purchase order. |
| `created_at` | Datetime | No | `2026-06-01T12:00:00Z` | Timestamp of record creation. |
| `week` | Integer | No | `27` | ISO week number. |
| `month` | Integer | No | `7` | Calendar month of transaction. |
| `quarter` | Integer | No | `3` | Calendar quarter of transaction. |
| `year` | Integer | No | `2026` | Calendar year of transaction. |
| `day_of_week` | Integer | No | `3` | Day index of the week (0=Monday, 6=Sunday). |
| `weekend_indicator` | Integer (Binary) | No | `0` | Flag indicating if date is a weekend (1=Yes, 0=No). |
| `season` | String | No | `Summer` | Calendar season (Winter, Spring, Summer, Autumn). |

---

## Table: `sales`
Contains 3 rows and 20 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `sale_id` | String (UUID) | No | `a8b9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the sale transaction. |
| `product_id` | String (UUID) | No | `f3b20c91-d824-4fca-8600-0e12361254ff` | Unique identifier for the product record. |
| `sale_date` | Date (YYYY-MM-DD) | No | `2026-07-02` | Date of the sale transaction. |
| `quantity` | int64 | No | `2` | Self-explanatory operational or engineered feature column. |
| `unit_price` | Float | No | `999.99` | Selling price per unit. |
| `customer_type` | String | No | `Retail` | Segment of customer: Retail or Wholesale. |
| `created_at` | Datetime | No | `2026-06-01T12:00:00Z` | Timestamp of record creation. |
| `unit_cost` | Float | No | `750.00` | Cost price per unit from supplier. |
| `revenue` | Float | No | `1999.98` | Total sales revenue (quantity * unit_price). |
| `profit` | Float | No | `499.98` | Net profit generated (revenue - COGS). |
| `profit_margin` | Float | No | `0.25` | Net profit margin ratio (profit / revenue). |
| `week` | Integer | No | `27` | ISO week number. |
| `month` | Integer | No | `7` | Calendar month of transaction. |
| `quarter` | Integer | No | `3` | Calendar quarter of transaction. |
| `year` | Integer | No | `2026` | Calendar year of transaction. |
| `day_of_week` | Integer | No | `3` | Day index of the week (0=Monday, 6=Sunday). |
| `weekend_indicator` | Integer (Binary) | No | `0` | Flag indicating if date is a weekend (1=Yes, 0=No). |
| `season` | String | No | `Summer` | Calendar season (Winter, Spring, Summer, Autumn). |
| `rolling_sales_7d` | Float | No | `42.0` | 7-day rolling sum of quantities sold for this product. |
| `rolling_sales_30d` | Float | No | `150.0` | 30-day rolling sum of quantities sold for this product. |

---

## Table: `suppliers`
Contains 1 rows and 8 columns.

| Column Name | Data Type | Nullable | Example Value | Business Definition & Rules |
| :--- | :--- | :--- | :--- | :--- |
| `supplier_id` | String (UUID) | No | `b4a3c2d1-e3f4-4a5b-6c7d-8e9f0a1b2c3d` | Unique identifier for the supplier record. |
| `name` | String | No | `Pro Laptop 15-inch` | Descriptive title of the product. |
| `contact_person` | String | Yes | `John Doe` | Primary supplier contact person. |
| `contact_email` | String | No | `john@supplier.com` | Supplier email address. |
| `contact_phone` | String | Yes | `+1-555-0199` | Supplier telephone contact. |
| `lead_time_days` | Integer | No | `7` | Supplier delivery lead time in days. |
| `rating` | Float | No | `4.5` | Supplier performance rating (scale 0 to 5). |
| `created_at` | Datetime | No | `2026-06-01T12:00:00Z` | Timestamp of record creation. |

---

# Data Cleaning & Pipeline Report

**Execution Timestamp:** 2026-07-14 19:33:21

**Pipeline Status:** PASSED

## 1. Overview
This automated pipeline extracts relational datasets from the SQLite inventory database, analyzes data quality issues, performs programmatic cleaning, implements feature engineering, validates the output, and exports analytical datasets.

### Pipeline Phase Execution Times
| Pipeline Phase | Elapsed Time |
| :--- | :--- |
| Extraction | 0.0109 seconds |
| Profiling | 0.0203 seconds |
| Cleaning | 0.0618 seconds |
| Feature Engineering | 0.0554 seconds |
| Validation | 0.0000 seconds |
| Export | 0.0164 seconds |
| **Total Pipeline Time** | **0.1647 seconds** |

## 2. Extraction & Quality Profiling Summary
| Table Name | Raw Row Count | Duplicates Detected | Missing Fields Count | Anomalies Found |
| :--- | :--- | :--- | :--- | :--- |
| products | 2 | 0 | 0 | 0 |
| suppliers | 1 | 0 | 0 | 0 |
| inventory | 2 | 0 | 0 | 0 |
| sales | 3 | 0 | 0 | 0 |
| purchase_orders | 1 | 0 | 0 | 0 |
| forecasts | 1 | 0 | 0 | 0 |
| users | 1 | 0 | 0 | 0 |
| audit_logs | 1 | 0 | 2 | 0 |

## 3. Cleaning & Data Standardizations
The following data corrections were applied dynamically:
- **Duplicate Removal:** All exact duplicate records deleted.
- **Whitespace Trimming:** Leading and trailing white spaces stripped across all text fields.
- **Text Normalization:** Upper-cased SKUs; Title-cased categories, locations, and customer types.
- **Imputations & Logical Bounds:** Missing categories filled with 'Other'. Negative price/quantity entries removed.
- **Outlier Capping:** Applied Interquartile Range (IQR) capping on transaction volumes and lead times.

### Cleaning Execution Metrics
| Cleaning Metric / Table | Rows Modified / Removed | Details |
| :--- | :--- | :--- |

## 4. Feature Engineering Summary
The transformation engine appended the following calculated columns:
1. **Inventory Value:** `quantity` * `unit_cost` per inventory stock.
2. **Sales Finance:** `revenue` = `quantity` * `unit_price`, `profit` = `revenue` - `COGS`, and `profit_margin` = `profit` / `revenue` per sales invoice.
3. **Stock Health indicators:** `stock_status` ('In Stock', 'Low Stock', 'Out Of Stock'), `reorder_required` boolean, and `safety_stock` limit.
4. **Supply KPIs:** Mapped `lead_time_days` and `supplier_rating` to products to flag `safety_stock_flag` and calculate `days_until_stockout` (run-out rate).
5. **Temporal Attributes:** Calendric features derived from date fields: `week`, `month`, `quarter`, `year`, `day_of_week`, `weekend_indicator`, and `season` indicators.
6. **Time-series Lags:** Engineered `rolling_sales_7d`, `rolling_sales_30d`, and `avg_daily_demand` per product.

## 5. Data Validation & Integrity Checks
**Validation Status:** PASSED

| Table Name | Schema Valid | Key Uniqueness | Null Checks | Relational Integrity | Errors / Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- |
| products | Passed ✅ | Passed | Passed | Passed | None |
| inventory | Passed ✅ | Passed | Passed | Passed | None |
| sales | Passed ✅ | Passed | Passed | Passed | None |
| suppliers | Passed ✅ | Passed | Passed | Passed | None |
| purchase_orders | Passed ✅ | Passed | Passed | Passed | None |
| forecasts | Passed ✅ | Passed | Passed | Passed | None |
| **Referential Checks** | Passed ✅ | N/A | N/A | Passed ✅ | None |

## 6. Export Formats & Archival Paths
The finalized processed tables were exported:

| Export Type | Output Paths |
| :--- | :--- |
| .CSV | `products.csv`<br>`inventory.csv`<br>`sales.csv`<br>`suppliers.csv`<br>`purchase_orders.csv`<br>`forecasts.csv`<br>`audit_logs.csv` |
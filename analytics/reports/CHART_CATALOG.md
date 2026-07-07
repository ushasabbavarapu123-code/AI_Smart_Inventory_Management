# Chart Catalog
## AI Smart Inventory Management & Demand Forecasting System

**Project:** AI Smart Inventory Management & Demand Forecasting  
**Phase:** Phase 4 — EDA Visualizations  
**Day:** Day 8  
**Total Charts:** 36  
**Author:** Antigravity AI  
**Date:** 2026-07-07  

---

## Directory Structure

```
analytics/
├── visuals/
│   ├── sales/          — 10 charts
│   ├── products/       — 7 charts
│   ├── inventory/      — 6 charts
│   ├── suppliers/      — 4 charts
│   ├── forecasts/      — 2 charts
│   └── (root)          — 2 shared charts
└── charts/             — 16 charts (legacy copies for backward compat)
```

---

## Sales Charts (`analytics/visuals/sales/`)

| ID | Filename | Chart Type | Purpose | Dataset | Business Meaning |
|----|----------|------------|---------|---------|------------------|
| S01 | S01_monthly_revenue_profit.png | Bar + Line (dual axis) | Monthly Revenue, Profit & Units Sold trend | sales_processed.csv | Identifies revenue growth patterns and monthly unit volume changes |
| S02 | S02_weekly_heatmap.png | Heatmap | Week-number × Year revenue intensity | sales_processed.csv | Reveals week-level seasonality peaks across years |
| S03 | S03_quarterly_performance.png | Grouped Bar | Q1–Q4 Revenue and Units Sold | sales_processed.csv | Quarterly comparison to benchmark business performance |
| S04 | S04_rolling_average.png | Line (multi) | 7-day & 30-day rolling revenue averages | sales_processed.csv | Smooths noise to reveal true demand signal and trend direction |
| S05 | S05_customer_segment.png | Pie + Bar | Revenue share and avg transaction by customer type | sales_processed.csv | Quantifies wholesale vs retail revenue contribution and transaction size |
| S06 | S06_distribution_histograms.png | Histogram (×3) | Revenue, Profit, Quantity distributions | sales_processed.csv | Shows distributional shape, skewness, and outlier thresholds |
| S07 | S07_monthly_profit_margin.png | Bar + Line (dual axis) | Monthly Profit trend and Margin % | sales_processed.csv | Monitors pricing health and cost efficiency over time |
| S08 | S08_day_of_week_pattern.png | Bar + Line | Avg revenue and units by weekday | sales_processed.csv | Identifies weekend vs weekday demand patterns for staffing/logistics |
| M01 | M01_correlation_heatmap.png | Heatmap (annotated) | Pearson correlations between 9 key numeric variables | sales + products | Reveals which variables drive revenue and profit; identifies redundancies |
| M02 | M02_seasonal_heatmap.png | Heatmap | Month × Day-of-Week average revenue | sales_processed.csv | Pinpoints peak demand time slots for targeted safety stock and staffing |
| M04 | M04_customer_segment_analysis.png | 2×2 Bar grid | Total orders, revenue, avg qty, avg revenue by segment | sales_processed.csv | Deep dive into customer segment behavior to prioritize segment strategy |
| O01 | O01_outlier_boxplots.png | Box plots (×3) | Revenue, Profit, Quantity outlier detection | sales_processed.csv | Identifies statistically anomalous transactions using IQR method |
| O02 | O02_revenue_anomalies.png | Line + Scatter | Daily revenue with 2-sigma anomaly band | sales_processed.csv | Flags anomalous revenue days for investigation (demand spikes/drops) |

---

## Product Charts (`analytics/visuals/products/`)

| ID | Filename | Chart Type | Purpose | Dataset | Business Meaning |
|----|----------|------------|---------|---------|------------------|
| P01 | P01_top10_revenue.png | Horizontal Bar | Top 10 products by total revenue | sales + products | Identifies revenue-generating champion SKUs for prioritized stocking |
| P02 | P02_top10_profit.png | Horizontal Bar | Top 10 products by net profit | sales + products | Reveals true profit drivers — may differ from revenue leaders |
| P03 | P03_worst10_revenue.png | Horizontal Bar | Worst 10 products by revenue | sales + products | Identifies underperformers candidates for discontinuation or promotion |
| P04 | P04_category_analysis.png | Bar (×3) | Revenue, Profit, Margin by category | sales + products | Category-level business performance comparison |
| P05 | P05_category_pie.png | Pie (×2) | Revenue share and volume share by category | sales + products | Visualizes category mix vs volume mix — identifies margin dilution |
| P06 | P06_demand_category.png | Bar + Pie | SKU count by demand level (High/Medium/Low) | products_processed.csv | Shows demand concentration; informs safety stock policy by demand tier |
| P07 | P07_margin_boxplot.png | Box plots | Profit margin distribution by category | sales + products | Compares margin stability and spread across product categories |

---

## Inventory Charts (`analytics/visuals/inventory/`)

| ID | Filename | Chart Type | Purpose | Dataset | Business Meaning |
|----|----------|------------|---------|---------|------------------|
| I01 | I01_stock_status.png | Bar + Pie | SKU count and value by stock status | products_processed.csv | Overall inventory health snapshot — availability vs risk |
| I02 | I02_inventory_turnover.png | Bar with error bars | Avg/Min/Max inventory turnover by category | products_processed.csv | Identifies categories with dead stock (low turnover) vs efficient stock |
| I03 | I03_days_until_stockout.png | Histogram | Distribution of days until estimated stockout | products_processed.csv | Urgency map — shows how many SKUs are approaching stockout thresholds |
| I04 | I04_safety_stock_scatter.png | Scatter | Current stock vs required safety stock per SKU | products + inventory | Identifies which SKUs are below safety buffer — immediate reorder candidates |
| I05 | I05_reorder_alerts.png | Horizontal Bar | SKUs requiring reorder (current vs safety stock) | products_processed.csv | Operational reorder list — direct input for procurement team |
| M03 | M03_demand_vs_inventory.png | Scatter (color coded) | Total annual demand vs current stock level by category | sales + products | Reveals demand-inventory mismatches — stockout risk vs overstock positions |
| O03 | O03_inventory_anomalies.png | Horizontal Bar | SKUs at critical stockout risk (<30 days) | products_processed.csv | Emergency action list — red = <7 days, yellow = 7–30 days |

---

## Supplier Charts (`analytics/visuals/suppliers/`)

| ID | Filename | Chart Type | Purpose | Dataset | Business Meaning |
|----|----------|------------|---------|---------|------------------|
| SU01 | SU01_lead_times.png | Horizontal Bar | Lead time per supplier with 7-day benchmark line | suppliers_processed.csv | Benchmarks each supplier's delivery speed — highlights procurement risk |
| SU02 | SU02_ratings.png | Horizontal Bar | Official rating per supplier with 4.0 minimum line | suppliers_processed.csv | Identifies underperforming suppliers for review or replacement |
| SU03 | SU03_performance_matrix.png | Bubble Scatter | Lead time vs OTD rate (size=spend, color=rating) | suppliers + po | 2D performance matrix — ideal suppliers = top-left quadrant |
| SU04 | SU04_po_status.png | Bar + Pie | PO count and distribution by status | purchase_orders_processed.csv | Procurement cycle health — tracks Received/Pending/Cancelled ratio |

---

## Forecast Charts (`analytics/visuals/forecasts/`)

| ID | Filename | Chart Type | Purpose | Dataset | Business Meaning |
|----|----------|------------|---------|---------|------------------|
| F01 | F01_forecast_confidence.png | Horizontal Bar with error | 30-day demand forecast with confidence intervals | forecasts + products | Shows predicted demand bounds — drives safety stock and PO quantity decisions |
| F02 | F02_actual_vs_expected.png | Grouped Bar | Actual annual sales vs expected (avg rate × 365) | sales + products | Forecast accuracy proxy — identifies over/underperforming products vs baseline |

---

## Legacy Charts (`analytics/charts/`)

These files are copies maintained for backward compatibility with existing notebook references:

| Filename | Source | Notes |
|----------|--------|-------|
| sales_trends.png | S01 equivalent (original) | Original Day 8 chart — replaced by S01 |
| product_performance.png | P01 equivalent (original) | Original Day 8 chart — replaced by P01 |
| inventory_health.png | I01 equivalent (original) | Original Day 8 chart — replaced by I01 |
| supplier_performance.png | SU03 equivalent (original) | Original Day 8 chart — replaced by SU03 |
| category_margins.png | P07 equivalent (original) | Original Day 8 chart — replaced by P07 |
| seasonality_patterns.png | S02/S08 equivalent (original) | Original Day 8 chart — replaced by S02/S08 |
| S01_monthly_revenue_profit.png | Copy | Current version |
| M01_correlation_heatmap.png | Copy | Current version |
| O01_outlier_boxplots.png | Copy | Current version |
| O02_revenue_anomalies.png | Copy | Current version |
| P01_top10_revenue.png | Copy | Current version |
| P07_margin_boxplot.png | Copy | Current version |
| SU01_lead_times.png | Copy | Current version |
| SU03_performance_matrix.png | Copy | Current version |
| I01_stock_status.png | Copy | Current version |
| I05_reorder_alerts.png | Copy | Current version |

---

## Visualization Standards Compliance

| Standard | Compliance |
|----------|------------|
| Professional title on every chart | ✅ |
| Axis labels on all axes | ✅ |
| Legend present where multiple series | ✅ |
| Business caption / subtitle on charts | ✅ |
| Curated color palette (not default Matplotlib) | ✅ |
| High DPI (150 dpi) for print quality | ✅ |
| Saved as PNG | ✅ |
| Matplotlib used | ✅ |
| Seaborn-style grid applied | ✅ |

---

## How to Regenerate All Charts

```bash
# From project root
python analytics/scripts/run_eda_complete.py
```

This script regenerates all 36 charts and prints the 10 executive insights.

---

*Chart Catalog — Phase 4 Day 8 — 2026-07-07 — Antigravity AI*

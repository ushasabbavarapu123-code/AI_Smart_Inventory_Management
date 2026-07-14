# USER_MANUAL.md

# AI Smart Inventory Management & Demand Forecasting System
# User Manual — Version 1.0

**Prepared By:** Antigravity AI
**Date:** 2026-07-14
**Target Audience:** Inventory Managers, Procurement Staff, Business Analysts

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Requirements](#2-system-requirements)
3. [Getting Started — Login](#3-getting-started--login)
4. [Dashboard Page](#4-dashboard-page)
5. [Products Page](#5-products-page)
6. [Inventory Page](#6-inventory-page)
7. [Sales Page](#7-sales-page)
8. [Suppliers Page](#8-suppliers-page)
9. [Purchase Orders Page](#9-purchase-orders-page)
10. [Forecasts Page](#10-forecasts-page)
11. [Reports Page](#11-reports-page)
12. [Logout & Session Management](#12-logout--session-management)
13. [Keyboard Shortcuts](#13-keyboard-shortcuts)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Overview

The AI Smart Inventory Management System is a web-based enterprise application that helps businesses:

- Track real-time inventory levels across warehouse locations
- Manage product catalog, supplier directory, and purchase orders
- Record and review sales transactions
- Generate AI-powered demand forecasts using Random Forest ML models
- Produce tabular reports and export them to CSV, Excel, or PDF

The application runs entirely in your browser. The backend API and database run on the local Node.js server.

---

## 2. System Requirements

| Component | Requirement |
|-----------|-------------|
| Browser | Chrome 110+, Firefox 115+, Edge 110+, Safari 16+ |
| Screen Resolution | 1280 × 720 minimum (1920 × 1080 recommended) |
| JavaScript | Must be enabled |
| Network | Backend server must be running on `http://localhost:5000` |

---

## 3. Getting Started — Login

### Opening the Application
1. Ensure the backend server is running (`npm start` from the `app/` directory).
2. Open your browser and navigate to: `http://localhost:5000`
3. You will see the Login page.

### Logging In
1. Enter your **Email** and **Password**.
2. Click the **Sign In** button.
3. On successful authentication, you are redirected to the **Dashboard**.

### Default Credentials (Seeded Users)

| Email | Password | Role |
|-------|----------|------|
| admin@smartinventory.com | securepassword | Admin |
| manager@smartinventory.com | securepassword | Manager |
| planner@smartinventory.com | securepassword | Planner |
| analyst@smartinventory.com | securepassword | Analyst |
| staff@smartinventory.com | securepassword | Planner |

> **Note:** The JWT token is valid for 8 hours. After expiry, you will be automatically redirected to the Login page.

---

## 4. Dashboard Page

The Dashboard is your central command center. It displays live KPIs and interactive charts computed directly from the database.

### KPI Cards (top row)
| KPI | Description |
|-----|-------------|
| Total Products | Count of all SKUs in the system |
| Total Suppliers | Number of active supplier records |
| Low Stock Alerts | Products below their reorder point |
| Inventory Value | Total value = Σ(quantity × unit_cost) |
| Pending Orders | Purchase orders awaiting fulfillment |
| Stockout Rate | Percentage of SKUs with zero stock |
| Monthly Sales | Revenue generated in the current calendar month |
| Transactions | Total count of all recorded sales |

### Charts
- **Revenue Trend** — Monthly sales revenue over time (line chart)
- **Category Distribution** — Inventory value by category (pie/doughnut)
- **Top Products** — Highest-value inventory items (bar chart)
- **Monthly Sales Volume** — Units sold per month (bar chart)
- **Inventory Heatmap** — Stock levels across warehouse locations
- **Supplier Metrics** — Lead time and rating comparison

---

## 5. Products Page

Manage your complete product catalog including SKU, category, cost, and reorder point.

### Viewing Products
- The product table loads automatically on page open.
- Use the **Search** bar to filter by name or SKU.
- Use the **Category** dropdown to filter by product category.

### Adding a New Product
1. Click the **+ Add Product** button.
2. Fill in the modal form:
   - **SKU** — Unique identifier (e.g., `ELE-101`)
   - **Product Name** — Descriptive name
   - **Category** — Select from Electronics, Food, Apparel, Home, Sports
   - **Unit Cost** — Cost price in dollars
   - **Reorder Point** — Minimum quantity threshold before triggering a reorder alert
3. Click **Save Product**.

### Editing a Product
1. Click the **✏️ Edit** button on the product row.
2. Modify the form fields in the modal.
3. Click **Update Product** to save.

### Deleting a Product
1. Click the **🗑️ Delete** button on the product row.
2. Confirm the deletion in the confirmation prompt.

> **Note:** Products with linked inventory, sales, or forecast records cannot be deleted until those dependent records are removed first (FK constraint).

---

## 6. Inventory Page

Track real-time stock levels across warehouse locations and receive reorder alerts.

### Viewing Inventory
- The inventory grid displays all SKUs with their current stock quantity and warehouse location.
- **Red badge** — Stockout (quantity = 0)
- **Orange badge** — Low stock (quantity < reorder point)
- **Green badge** — Healthy stock

### Adjusting Stock
1. Click **Adjust Stock** on any inventory row.
2. Enter the **New Quantity** and a mandatory **Reason** note (e.g., "Stock received from PO-2024-001").
3. Click **Save Adjustment**.

> All stock adjustments are logged to the audit trail for traceability.

---

## 7. Sales Page

Record individual sales transactions and browse the complete transaction history.

### Recording a Sale
1. Click **+ Record Sale**.
2. Fill in:
   - **Product** — Select from dropdown
   - **Sale Date** — Date picker
   - **Quantity** — Units sold
   - **Unit Price** — Price per unit at time of sale
   - **Customer Type** — Retail, Wholesale, or Online
3. Click **Save Sale**.

### Browsing Sales History
- Sort by date, product, or quantity using column headers.
- Use the date range picker to filter a specific time window.

---

## 8. Suppliers Page

Manage your supplier directory with contact details, lead times, and performance ratings.

### Adding a Supplier
1. Click **+ Add Supplier**.
2. Fill in supplier name, contact person, email, phone, lead time (days), and rating (1–5 stars).
3. Click **Save Supplier**.

### Understanding Lead Time & Rating
- **Lead Time** — Average days from order placed to delivery. Lower is better.
- **Rating** — Supplier performance score (1–5 stars). Target: > 4.0.

---

## 9. Purchase Orders Page

Create and manage purchase orders from placement to delivery receipt.

### Creating a Purchase Order
1. Click **+ Create PO**.
2. Select **Supplier** and **Product**.
3. Enter **Quantity**, **Unit Cost**, **Order Date**, and **Expected Delivery** date.
4. Add optional **Notes**.
5. Click **Submit Order**.

### Purchase Order Lifecycle
| Status | Meaning |
|--------|---------|
| Pending | Order created, not yet sent to supplier |
| Sent | Order dispatched to supplier |
| Received | Goods received and stock updated |
| Cancelled | Order cancelled before delivery |

### Receiving a Shipment
1. Find the PO in the table.
2. Click **Mark Received**.
3. The system records the actual delivery date and updates inventory stock levels.

---

## 10. Forecasts Page

Use the AI-powered demand forecasting engine to predict future product demand.

### Viewing Existing Forecasts
- The forecast table shows all historical forecast runs with:
  - Product SKU and name
  - Forecast date
  - Predicted quantity (units)
  - Confidence interval [Low – High]
  - Model used (ARIMA / Random Forest)
  - Generation timestamp

### Filtering Forecasts by Product
- Use the **Product Selector** dropdown at the top.
- The chart and metrics cards update instantly to show per-product predictions.
- Switch between **All Products** (aggregate bar chart) and individual product (timeline line chart with confidence bands).

### Model Performance Metrics
| Metric | Description |
|--------|-------------|
| RF MAE | Random Forest Mean Absolute Error |
| MA MAE | Moving Average Mean Absolute Error |
| Accuracy | Overall model accuracy percentage |
| Safety Stock | Recommended safety stock buffer |
| Reorder Point | Dynamically computed ROP for selected product |

### Triggering a New Forecast
1. Click **Generate Forecast**.
2. Select the **Target Product** from the dropdown.
3. Set the **Horizon Days** (default: 30 days).
4. Click **Run Model Pipeline**.
5. The system invokes the Python ML script (`analytics/scripts/forecast.py`) as a background process, saves the results to the database, and refreshes the table automatically.

---

## 11. Reports Page

Generate, preview, and export business reports in multiple formats.

### Available Report Types
| Report | Data Source | Columns |
|--------|-------------|---------|
| Inventory Balance | Inventory + Products | SKU, Product, Location, Qty, Reorder Point, Status |
| Sales Performance | Sales + Products | Date, SKU, Product, Qty, Unit Price, Total, Customer Type |
| Demand Forecast | Forecasts + Products | SKU, Product, Forecast Date, Predicted Qty, Confidence Range, Model |
| Supplier Analysis | Suppliers | Name, Contact, Email, Phone, Lead Time, Rating |

### Generating a Report
1. Click the desired report button (e.g., **Inventory Report**, **Sales Report**).
2. The report table renders immediately in the preview pane.
3. Click one of the export buttons:
   - **Export CSV** — Downloads a `.csv` file for spreadsheet use
   - **Export Excel** — Downloads a `.xlsx` file (requires SheetJS library to load)
   - **Export PDF** — Downloads a formatted `.pdf` document

### Viewing Documentation Files
- Click any file name in the **Documentation Browser** sidebar to load the markdown file directly in the viewer panel.

---

## 12. Logout & Session Management

- Click the **Logout** button at the bottom of the sidebar or in the top-right profile menu.
- Your JWT token is removed from browser storage.
- You are redirected to the Login page.

> Sessions expire automatically after 8 hours. Any API request after expiry returns a `401 Unauthorized` and triggers an automatic redirect to the Login page.

---

## 13. Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Close open modal | `Escape` |
| Open browser console (debug) | `F12` |

---

## 14. Troubleshooting

| Issue | Solution |
|-------|----------|
| Page shows blank / spinner stuck | Verify the backend server is running: `cd app && npm start` |
| "Session expired" message | Re-login with your credentials |
| Forecast button shows error | Ensure Python virtual environment is active and `analytics/venv` exists |
| Charts not rendering | Ensure internet connection (Chart.js loads from CDN) or switch to offline mode |
| Excel export fails | Wait 2–3 seconds for SheetJS library to finish loading from CDN |
| Database empty after restart | Run seed script: `analytics/venv/Scripts/python.exe analytics/scripts/seed_data.py` |

---

*User Manual v1.0 — AI Smart Inventory Management & Demand Forecasting System*
*Prepared by Antigravity AI — 2026-07-14*

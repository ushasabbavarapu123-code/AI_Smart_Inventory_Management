# Database Design Document

**Project:** AI Smart Inventory Management & Demand Forecasting System
**Version:** 1.0
**Phase:** Phase 1 – Database Design
**Day:** Day 2
**Database Engine:** SQLite 3
**Normalization:** 3rd Normal Form (3NF)
**Status:** COMPLETED
**Date:** 2026-06-29

---

## 1. Overview

The database stores all operational data for the AI Smart Inventory Management system. It is a single-file SQLite database stored at `data/inventory.db`. All tables are normalized to 3NF to eliminate redundancy and ensure data integrity.

---

## 2. ER Diagram (Text Representation)

```
products (product_id PK)
    |
    |--< inventory (product_id FK)
    |
    |--< sales (product_id FK)
    |
    |--< forecasts (product_id FK)
    |
    |--< purchase_orders (product_id FK)

suppliers (supplier_id PK)
    |
    |--< purchase_orders (supplier_id FK)

users (user_id PK)
    |
    |--< audit_logs (user_id FK)
```

---

## 3. Table Definitions

### Table: products
**Purpose:** Master catalog of all inventory items (SKUs).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| sku | TEXT | UNIQUE, NOT NULL | Stock Keeping Unit code |
| name | TEXT | NOT NULL | Product display name |
| category | TEXT | | Product category (e.g., Electronics, Food) |
| unit_cost | REAL | NOT NULL, CHECK >= 0 | Cost per unit in INR/USD |
| reorder_point | INTEGER | NOT NULL, DEFAULT 10 | Minimum stock before reorder alert triggers |
| created_at | TEXT | NOT NULL | ISO8601 timestamp of record creation |

**Indexes:**
- `idx_products_sku` ON `sku` (for fast SKU lookup)
- `idx_products_category` ON `category` (for category filtering)

---

### Table: inventory
**Purpose:** Tracks real-time stock quantity per product and warehouse location.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| inventory_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| product_id | TEXT | FOREIGN KEY → products.product_id, NOT NULL | Product reference |
| location | TEXT | NOT NULL, DEFAULT 'Warehouse-A' | Storage location identifier |
| quantity | INTEGER | NOT NULL, CHECK >= 0 | Current available stock |
| last_updated | TEXT | NOT NULL | ISO8601 timestamp of last stock update |

**Indexes:**
- `idx_inventory_product_id` ON `product_id`
- `idx_inventory_location` ON `location`

**Constraints:**
- ON DELETE RESTRICT on product_id FK (cannot delete a product with inventory records)

---

### Table: sales
**Purpose:** Records every individual sales transaction for demand planning and forecasting.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| product_id | TEXT | FOREIGN KEY → products.product_id, NOT NULL | Product sold |
| sale_date | TEXT | NOT NULL | ISO8601 date of the sale (YYYY-MM-DD) |
| quantity | INTEGER | NOT NULL, CHECK > 0 | Units sold |
| unit_price | REAL | NOT NULL, CHECK > 0 | Sale price per unit at time of sale |
| customer_type | TEXT | DEFAULT 'Retail' | Customer segment (Retail, Wholesale) |
| created_at | TEXT | NOT NULL | Record creation timestamp |

**Indexes:**
- `idx_sales_product_id` ON `product_id`
- `idx_sales_sale_date` ON `sale_date` (for time-series queries)
- `idx_sales_product_date` ON `(product_id, sale_date)` (composite for forecasting queries)

---

### Table: forecasts
**Purpose:** Stores the latest AI-generated demand forecast per product.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| forecast_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| product_id | TEXT | FOREIGN KEY → products.product_id, NOT NULL | Product forecasted |
| forecast_date | TEXT | NOT NULL | Future date for which demand is predicted |
| predicted_qty | INTEGER | NOT NULL, CHECK >= 0 | Predicted units demand |
| confidence_low | INTEGER | NOT NULL | Lower bound of prediction interval |
| confidence_high | INTEGER | NOT NULL | Upper bound of prediction interval |
| model_used | TEXT | NOT NULL, DEFAULT 'ARIMA' | ML model used (ARIMA, Linear Regression, etc.) |
| generated_at | TEXT | NOT NULL | Timestamp when forecast was generated |

**Indexes:**
- `idx_forecasts_product_id` ON `product_id`
- `idx_forecasts_forecast_date` ON `forecast_date`

---

### Table: suppliers
**Purpose:** Supplier master data for purchase order management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| supplier_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| name | TEXT | NOT NULL | Supplier company name |
| contact_person | TEXT | | Primary contact name |
| contact_email | TEXT | | Contact email address |
| contact_phone | TEXT | | Contact phone number |
| lead_time_days | INTEGER | NOT NULL, CHECK > 0 | Average delivery lead time in days |
| rating | REAL | CHECK >= 1.0 AND <= 5.0 | Supplier performance rating |
| created_at | TEXT | NOT NULL | Record creation timestamp |

---

### Table: purchase_orders
**Purpose:** Tracks stock replenishment purchase orders raised by the system or users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| po_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| supplier_id | TEXT | FOREIGN KEY → suppliers.supplier_id, NOT NULL | Supplier fulfilling the order |
| product_id | TEXT | FOREIGN KEY → products.product_id, NOT NULL | Product being ordered |
| quantity | INTEGER | NOT NULL, CHECK > 0 | Units ordered |
| unit_cost | REAL | NOT NULL | Unit cost at time of order |
| order_date | TEXT | NOT NULL | Date the PO was raised |
| expected_delivery | TEXT | | Anticipated delivery date |
| actual_delivery | TEXT | | Actual date received |
| status | TEXT | NOT NULL, CHECK IN ('Pending','Sent','Received','Cancelled') | Current PO status |
| notes | TEXT | | Optional remarks |
| created_at | TEXT | NOT NULL | Record creation timestamp |

**Indexes:**
- `idx_po_supplier_id` ON `supplier_id`
- `idx_po_product_id` ON `product_id`
- `idx_po_status` ON `status`

---

### Table: users
**Purpose:** System user accounts for authentication and role-based access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| email | TEXT | UNIQUE, NOT NULL | Login email address |
| password_hash | TEXT | NOT NULL | bcrypt-hashed password |
| full_name | TEXT | NOT NULL | User's full name |
| role | TEXT | NOT NULL, CHECK IN ('Manager','Planner','Analyst','Admin') | Access role |
| is_active | INTEGER | NOT NULL, DEFAULT 1 | 1=Active, 0=Deactivated |
| created_at | TEXT | NOT NULL | Account creation timestamp |
| last_login | TEXT | | Timestamp of most recent login |

**Indexes:**
- `idx_users_email` ON `email`
- `idx_users_role` ON `role`

---

### Table: audit_logs
**Purpose:** Immutable audit trail for all data-mutating operations (compliance requirement).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| log_id | TEXT | PRIMARY KEY | UUID-format unique identifier |
| user_id | TEXT | FOREIGN KEY → users.user_id | User who performed the action |
| action | TEXT | NOT NULL | Action type (CREATE, UPDATE, DELETE) |
| entity | TEXT | NOT NULL | Table/entity affected (e.g., 'products') |
| entity_id | TEXT | | ID of the affected record |
| old_value | TEXT | | JSON snapshot of data before change |
| new_value | TEXT | | JSON snapshot of data after change |
| ip_address | TEXT | | Client IP address |
| timestamp | TEXT | NOT NULL | ISO8601 timestamp of the action |

> Note: Audit log records must never be updated or deleted. Only INSERT is permitted.

---

## 4. Relationships Summary

| Relationship | Type | Parent Table | Child Table | FK Column |
|-------------|------|-------------|-------------|-----------|
| Product → Inventory | One-to-Many | products | inventory | product_id |
| Product → Sales | One-to-Many | products | sales | product_id |
| Product → Forecasts | One-to-Many | products | forecasts | product_id |
| Product → Purchase Orders | One-to-Many | products | purchase_orders | product_id |
| Supplier → Purchase Orders | One-to-Many | suppliers | purchase_orders | supplier_id |
| User → Audit Logs | One-to-Many | users | audit_logs | user_id |

---

## 5. Normalization Review

- **1NF:** All columns contain atomic values. No repeating groups.
- **2NF:** All non-key columns depend entirely on the full primary key. No partial dependencies.
- **3NF:** No transitive dependencies. Each non-key column depends directly on the primary key only.

---

## 6. Data Volume Estimates (Day 5 Seed Data)

| Table | Estimated Records |
|-------|------------------|
| products | 50 |
| inventory | 50 |
| sales | 500+ (12 months historical) |
| forecasts | 50 (one per product) |
| suppliers | 10 |
| purchase_orders | 100 |
| users | 5 |
| audit_logs | Auto-generated during testing |

---

*Database design completed on Day 2 – 2026-06-29.*

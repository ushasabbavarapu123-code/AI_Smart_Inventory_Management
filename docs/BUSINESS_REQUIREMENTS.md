# Business Requirements Document (BRD)

**Project:** AI Smart Inventory Management & Demand Forecasting System
**Version:** 1.0
**Phase:** Phase 1 – Business Understanding
**Day:** Day 2
**Status:** COMPLETED
**Prepared By:** Antigravity AI
**Date:** 2026-06-29

---

## 1. Business Problem

Retail and warehouse businesses frequently suffer from inventory-related challenges that directly impact profitability and customer satisfaction.

Core problems include:

- **Overstocking** – Excess inventory tied up as working capital, leading to storage costs and product expiry.
- **Understocking (Stock-outs)** – Missed sales, poor customer satisfaction, and urgent re-ordering costs.
- **Manual Inventory Tracking** – Prone to human error, slow, and unable to scale.
- **Poor Demand Forecasting** – Reactive purchasing decisions lead to inefficient supply chain operations.
- **Lack of Real-Time Visibility** – Decision-makers cannot see live stock positions.
- **Fragmented Reporting** – No single view of inventory performance KPIs.

---

## 2. Business Objectives

1. Develop a web-based inventory management system for real-time stock tracking.
2. Automate demand forecasting using historical sales data and machine learning.
3. Generate data-driven reorder recommendations to prevent stock-outs.
4. Build interactive business dashboards exposing inventory KPIs.
5. Store all transactional data in a structured SQLite relational database.
6. Deliver analytics insights through a Python-based data pipeline.
7. Reduce inventory carrying costs and increase service levels.

---

## 3. Scope

### In Scope

- Product catalog management (CRUD)
- Real-time inventory tracking
- Supplier management
- Purchase order management
- Historical sales data recording
- Demand forecasting (Python analytics pipeline)
- Interactive KPI dashboard
- Business insight reporting

### Out of Scope

- Mobile applications
- Cloud deployment (local deployment only)
- Payment gateway integration
- Multi-tenant architecture
- OAuth-based authentication (basic auth only)
- Distributed database architecture

---

## 4. Stakeholders

| Role | Responsibilities |
|------|------------------|
| Warehouse Manager | View inventory levels, approve purchase orders |
| Demand Planner | Review demand forecasts, adjust planning parameters |
| Business Analyst | Create analytical reports, export data |
| System Administrator | Deploy and maintain the system |
| Supplier | Receive purchase orders, provide stock updates |

---

## 5. User Personas

### Persona 1: Warehouse Manager
- **Name:** Ravi (Operations Head)
- **Goal:** Keep shelves stocked and minimize dead stock
- **Pain Point:** No real-time visibility into what is running low
- **Tech Comfort:** Medium

### Persona 2: Demand Planner
- **Name:** Priya (Analytics Lead)
- **Goal:** Predict future demand and plan procurement in advance
- **Pain Point:** Forecasts are based on gut feeling, not data
- **Tech Comfort:** High

### Persona 3: Business Analyst
- **Name:** Karthik (Finance Analyst)
- **Goal:** Track inventory costs, stockout rates, and turnover ratios
- **Pain Point:** Data lives in spreadsheets, not a dashboard
- **Tech Comfort:** Medium

---

## 6. Functional Requirements

| # | Requirement | Priority |
|---|-------------|----------|
| FR01 | User login and role-based access control | High |
| FR02 | Add, edit, delete, and view products | High |
| FR03 | Track real-time inventory levels per location | High |
| FR04 | Record sales transactions | High |
| FR05 | Record and manage purchase orders | High |
| FR06 | Manage supplier information and lead times | High |
| FR07 | Generate 30-day demand forecasts per product | High |
| FR08 | Display KPI dashboard with key metrics | High |
| FR09 | Generate low-stock alerts | Medium |
| FR10 | Export data to CSV for offline analysis | Medium |
| FR11 | View audit log of all data changes | Medium |
| FR12 | Reorder quantity recommendation per SKU | High |

---

## 7. Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NFR01 | API response time for CRUD operations | ≤ 200 ms |
| NFR02 | Forecast latency | ≤ 2 seconds |
| NFR03 | Dashboard page load time | ≤ 3 seconds |
| NFR04 | System availability (local) | 99.5% |
| NFR05 | Forecast MAPE accuracy | ≤ 10% |
| NFR06 | Code test coverage | ≥ 70% |
| NFR07 | Input validation on all API endpoints | 100% |
| NFR08 | Audit logging for all data-mutating actions | 100% |

---

## 8. Business Rules

- A product cannot have a negative inventory quantity.
- A purchase order cannot be deleted after its status reaches "Sent" or "Received".
- A forecast must always be generated from at least 30 days of historical sales data.
- A low-stock alert must trigger when inventory falls below the defined reorder point.
- Audit logs are immutable – no update or delete is permitted.

---

## 9. User Stories

### US01 – Inventory Manager
*As a Warehouse Manager, I want to view current stock levels for all products so that I can identify items that need reordering.*

**Acceptance Criteria:**
- Dashboard displays live quantity for all SKUs.
- Quantities are refreshed when the page is loaded.

### US02 – Demand Planner
*As a Demand Planner, I want to view a 30-day demand forecast per SKU so that I can raise purchase orders in advance.*

**Acceptance Criteria:**
- Forecast is available per product via API and dashboard.
- Confidence intervals are shown alongside predicted quantities.

### US03 – Business Analyst
*As a Business Analyst, I want to see KPIs like forecast accuracy, stock-out rate, and inventory turnover so that I can identify areas for operational improvement.*

**Acceptance Criteria:**
- KPI dashboard shows all core metrics.
- Each KPI links to its source data.

### US04 – Administrator
*As an Admin, I want to manage user accounts and roles so that I can control access to sensitive data.*

**Acceptance Criteria:**
- Admin can create, edit, and deactivate user accounts.
- Roles restrict which API endpoints each user can access.

---

## 10. Business Questions for Analytics

| # | Business Question |
|---|-------------------|
| Q1 | Which products are likely to run out of stock in the next 30 days? |
| Q2 | Which products are consistently overstocked? |
| Q3 | Which product categories generate the highest revenue? |
| Q4 | Which suppliers have the longest lead times? |
| Q5 | How accurate are the demand forecasts for each SKU? |
| Q6 | Which products exhibit seasonal demand patterns? |
| Q7 | What reorder quantity should be recommended for each SKU? |
| Q8 | Which products have declining sales trends over the past 6 months? |

---

## 11. Key Performance Indicators (KPIs)

| KPI | Definition | Target |
|-----|------------|--------|
| Forecast MAPE | Mean Absolute Percentage Error of demand forecasts | ≤ 10% |
| Stock-out Rate | % of SKUs experiencing zero stock on any day | < 5% |
| Inventory Turnover | COGS / Average Inventory Value (monthly) | > 4x per year |
| Carrying Cost | Average Inventory Value × Carrying Cost Rate | Reduce by 15% |
| Forecast Latency | API response time for /api/forecasts | ≤ 2 seconds |
| API Error Rate | % of API calls returning 5xx errors | < 1% |
| Data Freshness | Age of latest sales record used in forecasting | ≤ 24 hours |

---

## 12. Success Criteria

- Forecast MAPE ≤ 10% after 30 days of operation.
- Stock-out incidents reduced by 30% within 6 months.
- Inventory carrying costs reduced by 15%.
- Dashboard available and functional locally with all KPIs visible.
- Complete documentation for handoff and portfolio.

---

*Document prepared on Day 2 – 2026-06-29.*

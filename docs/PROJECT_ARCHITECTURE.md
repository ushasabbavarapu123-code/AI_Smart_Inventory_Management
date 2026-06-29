# Project Architecture Document

**Project:** AI Smart Inventory Management & Demand Forecasting System
**Version:** 1.0
**Phase:** Phase 1 – Architecture Design
**Day:** Day 2
**Status:** COMPLETED
**Date:** 2026-06-29

---

## 1. Overall Architecture Overview

The AI Smart Inventory Management System follows a **Three-Tier Architecture** with an additional **Python Analytics Layer** for AI/ML demand forecasting. The system is designed for local deployment, following clean separation of concerns across four distinct layers.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
│                    HTML5 + CSS3 + JavaScript ES6                    │
│            (app/public/ – Browser-rendered, Chart.js)               │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP/REST (fetch API)
┌───────────────────────────▼─────────────────────────────────────────┐
│                         APPLICATION LAYER                           │
│                      Node.js + Express.js                           │
│            (app/src/ – Routing, Auth, Business Logic)               │
└──────────┬───────────────────────────────────┬──────────────────────┘
           │ SQL (sqlite3 npm)                 │ Child Process Spawn
           │                                  │ (python forecast.py)
┌──────────▼──────────────────┐   ┌───────────▼──────────────────────┐
│       DATA LAYER            │   │        ANALYTICS LAYER           │
│       SQLite 3              │   │     Python 3.12 + ML libs        │
│   (data/inventory.db)       │   │   (analytics/scripts/ + venv)    │
│                             │◄──┤  Reads: sales, inventory         │
│                             │   │  Writes: forecasts table         │
└─────────────────────────────┘   └──────────────────────────────────┘
```

---

## 2. Frontend Architecture

**Technology:** Vanilla HTML5, CSS3, JavaScript ES6
**Location:** `app/public/`
**Pattern:** Multi-page application (MPA) with shared CSS and JS utilities

### Page Structure
```
app/public/
├── index.html              # Login page
├── dashboard.html          # KPI overview dashboard
├── products.html           # Product catalog management
├── inventory.html          # Live inventory management
├── sales.html              # Sales transaction management
├── suppliers.html          # Supplier directory
├── purchase-orders.html    # PO tracking
├── forecasts.html          # Demand forecast display
├── reports.html            # Analytics reports
│
├── css/
│   ├── main.css            # Global styles, CSS variables, layout
│   ├── dashboard.css       # Dashboard specific styles
│   └── components.css      # Reusable component styles
│
└── js/
    ├── api.js              # Central API call utility (auth headers)
    ├── auth.js             # Login/logout logic
    ├── dashboard.js        # Dashboard data loading
    ├── products.js         # Product CRUD UI
    ├── inventory.js        # Inventory management UI
    ├── sales.js            # Sales transaction UI
    ├── suppliers.js        # Supplier management UI
    ├── purchase-orders.js  # PO management UI
    ├── forecasts.js        # Forecast trigger and display
    └── charts.js           # Chart.js configuration and rendering
```

---

## 3. Backend Architecture

**Technology:** Node.js 18+, Express.js 4.x
**Location:** `app/src/`
**Pattern:** MVC (Model–View–Controller) with middleware layer

### Request Lifecycle
```
Incoming Request
       ↓
CORS Middleware
       ↓
Body Parser Middleware (JSON)
       ↓
Auth Middleware (JWT Verify)
       ↓
Role Check Middleware (if required)
       ↓
Input Validation Middleware
       ↓
Route Handler → Controller → Model → SQLite
       ↓
Audit Logger (on mutations)
       ↓
Error Handler Middleware
       ↓
JSON Response
```

### Directory Structure
```
app/
├── src/
│   ├── server.js           # Express app setup and port binding
│   ├── database.js         # SQLite connection pool, schema init
│   └── logger.js           # Audit log utility
│
├── routes/
│   ├── auth.routes.js
│   ├── products.routes.js
│   ├── inventory.routes.js
│   ├── sales.routes.js
│   ├── suppliers.routes.js
│   ├── forecast.routes.js
│   ├── purchaseOrders.routes.js
│   └── dashboard.routes.js
│
├── controllers/            # Business logic handlers
├── models/                 # Database query functions
├── middleware/             # Auth, validation, error handlers
├── config/                 # App config and DB config
└── package.json
```

---

## 4. Analytics Architecture

**Technology:** Python 3.12, Pandas, NumPy, Scikit-Learn, Statsmodels
**Location:** `analytics/`
**Pattern:** Script-based pipeline invoked on demand

### Analytics Pipeline
```
1. extract.py
   → Connect to SQLite (data/inventory.db)
   → Query sales, inventory, products tables
   → Export to Pandas DataFrames

2. clean.py
   → Handle missing values
   → Correct data types
   → Remove outliers (IQR method)
   → Feature engineering (month, day_of_week, rolling averages)
   → Export clean dataset to analytics/datasets/clean/

3. forecast.py
   → Load clean dataset
   → Select forecasting model (ARIMA for time series, Linear Regression for sparse data)
   → Generate 30-day demand forecast per product
   → Compute confidence intervals
   → Write results to SQLite forecasts table

4. eda.py (Phase 4 – Days 8-9)
   → Univariate, bivariate, correlation analysis
   → Business question answering with visualizations
   → Export HTML reports and charts
```

---

## 5. Database Architecture

**Technology:** SQLite 3
**Location:** `data/inventory.db`
**Pattern:** Relational, 3NF-normalized, single-file

```
data/
└── inventory.db            # Main SQLite database (excluded from Git via .gitignore)
```

### Schema Overview
```
products ───┬──► inventory
            ├──► sales
            ├──► forecasts
            └──► purchase_orders ◄── suppliers

users ──────► audit_logs
```

---

## 6. Security Architecture

| Security Layer | Implementation |
|---------------|---------------|
| Authentication | JWT issued on login, validated on every request |
| Authorization | Role check middleware (Manager, Planner, Analyst, Admin) |
| Input Sanitization | Validation middleware on all POST/PUT/PATCH body fields |
| SQL Injection Prevention | All DB queries use parameterized statements via sqlite3 |
| Audit Logging | All mutations logged to `audit_logs` table |
| Environment Variables | Port, DB path, JWT secret stored in `.env` (excluded from Git) |
| CORS Policy | Configured to allow only localhost origins in development |

---

## 7. Folder Structure (Complete)

```
AI_Smart_Inventory_Management/
│
├── app/                        # Backend (Node.js Express)
│   ├── src/                    # Core server and database
│   ├── routes/                 # API route definitions
│   ├── controllers/            # Request handlers
│   ├── models/                 # Database query layer
│   ├── middleware/             # Auth, validation, error handling
│   ├── config/                 # Configuration files
│   ├── public/                 # Frontend (HTML, CSS, JS)
│   ├── package.json
│   └── .env                    # Environment variables (gitignored)
│
├── analytics/                  # Python analytics pipeline
│   ├── scripts/                # Python scripts
│   ├── notebooks/              # Jupyter notebooks
│   ├── datasets/               # Raw and cleaned datasets
│   ├── venv/                   # Python virtual environment (gitignored)
│   └── requirements.txt
│
├── data/                       # SQLite database file
│   └── inventory.db            # (gitignored)
│
├── docs/                       # Project documentation
│   ├── BUSINESS_REQUIREMENTS.md
│   ├── SYSTEM_DESIGN.md
│   ├── DATABASE_DESIGN.md
│   ├── API_SPECIFICATION.md
│   ├── PROJECT_ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md      # (Day 6-7)
│   ├── TEST_PLAN.md            # (Day 12)
│   ├── DEPLOYMENT_GUIDE.md     # (Day 15)
│   └── USER_MANUAL.md          # (Final)
│
├── DAILY_REPORTS/              # Daily progress reports (.txt)
│   └── email_drafts/
│       └── DAILY_EMAIL_DRAFTS.txt
│
├── PROJECT_GUIDE.md            # Master operating guide
├── PROJECT_TRACKER.md          # Day-wise progress tracker
├── CURRENT_DAY.md              # Current execution controller
├── DAILY_REPORT_TEMPLATE.md    # Report template
├── README.md                   # Project overview
└── .gitignore
```

---

## 8. Communication Flow Diagram

```
[User Browser]
      |
      | HTTPS (local: HTTP)
      |
[Frontend - HTML/JS]
      |
      | fetch() REST calls
      |
[Express Backend :5000]
      |
      |─── Auth/Validate/Route ──► [Controller]
      |                                  |
      |                                  |─── [SQLite Query via Model]
      |                                  |         |
      |                                  |         └─► [data/inventory.db]
      |                                  |
      |                         (on forecast request)
      |                                  |
      |                                  └─► [spawn python forecast.py]
      |                                              |
      |                                              └─► [SQLite forecasts table]
      |
      | JSON response
      |
[Frontend renders Chart.js / table]
```

---

## 9. Development Milestones Summary

| Day | Architecture Component Delivered |
|-----|----------------------------------|
| Day 1 | Repository, folder structure, backend skeleton, Python venv |
| Day 2 | Full system design, DB schema, API spec, architecture docs |
| Day 3 | SQLite schema creation, migration scripts, seed data |
| Day 4 | REST API CRUD routes for products, inventory, sales |
| Day 5 | Complete backend with 500+ seed records, Postman tests |
| Day 6-7 | Python data extraction and cleaning pipeline |
| Day 8-9 | EDA notebooks and business insight generation |
| Day 10-11 | Frontend HTML/CSS/JS dashboard with Chart.js |
| Day 12 | Testing, security audit, validation |
| Day 13-14 | Documentation, README, presentation |
| Day 15 | Final demo and deployment guide |

---

*Architecture document completed on Day 2 – 2026-06-29.*

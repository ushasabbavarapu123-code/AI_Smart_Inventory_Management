# System Design Document

**Project:** AI Smart Inventory Management & Demand Forecasting System
**Version:** 1.0
**Phase:** Phase 1 – System Design
**Day:** Day 2
**Status:** COMPLETED
**Date:** 2026-06-29

---

## 1. High-Level Architecture

The system is structured as a three-tier architecture:

```
+--------------------+      HTTP/REST     +---------------------+      SQL       +-------------------+
|   Frontend         |  <------------>   |   Backend            |  <-------->   |   SQLite Database  |
|   (HTML/CSS/JS)    |                   |   (Node.js Express)  |               |   (inventory.db)   |
+--------------------+                   +---------------------+               +-------------------+
                                                  |
                                         Python Script Call
                                                  |
                                         +-------------------+
                                         |  Analytics Layer  |
                                         |  (Python / ML)    |
                                         +-------------------+
```

---

## 2. Layer Descriptions

### Presentation Layer (Frontend)
- Built with plain HTML5, CSS3, and vanilla JavaScript (ES6).
- Consumes the REST API via `fetch()` calls.
- Renders data using Chart.js for interactive charts.
- Responsive layout for desktop browsers.
- Single-page dashboard with multiple panels.
- Located in `app/public/`.

### Application Layer (Backend)
- Built with **Node.js** and **Express.js**.
- Handles REST API routes, request validation, business logic, and JWT-based auth.
- Connects to SQLite database via the `sqlite3` Node.js package.
- Writes audit logs on every data-mutating operation.
- Calls Python scripts via child process when demand forecast is requested.
- Located in `app/src/`.

### Data Layer (Database)
- **SQLite** single-file relational database.
- File stored at `data/inventory.db`.
- All tables in 3rd Normal Form (3NF).
- Full referential integrity enforced with foreign keys.

### Analytics Layer (Python)
- Python 3.12 virtual environment in `analytics/venv/`.
- Scripts connect directly to the SQLite database.
- Performs data extraction, cleaning, and ML-based demand forecasting.
- Forecast results are written back to the `forecasts` table in the database.
- Located in `analytics/scripts/` and `analytics/notebooks/`.

---

## 3. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | HTML5, CSS3, JavaScript ES6 | Latest |
| Frontend Charts | Chart.js | Latest |
| Backend Runtime | Node.js | 18+ |
| Backend Framework | Express.js | 4.x |
| Database | SQLite | 3.x |
| ORM/Driver | sqlite3 (npm) | 5.x |
| Authentication | JWT (jsonwebtoken) | 9.x |
| Analytics | Python | 3.12 |
| Data Processing | Pandas, NumPy | Latest |
| Visualization | Matplotlib, Plotly | Latest |
| Machine Learning | Scikit-Learn, Statsmodels | Latest |
| ML Models | XGBoost | Latest |
| Version Control | Git | Latest |

---

## 4. Module Breakdown

### Backend Modules

```
app/
├── src/
│   ├── server.js             # Express app initialization, middleware, port
│   ├── database.js           # SQLite connection and initialization
│   └── logger.js             # Audit logging utility
│
├── routes/
│   ├── auth.routes.js        # POST /api/auth/login, POST /api/auth/logout
│   ├── products.routes.js    # CRUD /api/products
│   ├── inventory.routes.js   # GET, PATCH /api/inventory/:id
│   ├── sales.routes.js       # CRUD /api/sales
│   ├── suppliers.routes.js   # CRUD /api/suppliers
│   ├── forecast.routes.js    # POST, GET /api/forecasts
│   └── purchaseOrders.routes.js  # CRUD /api/purchase-orders
│
├── controllers/
│   ├── authController.js     # Login, logout logic
│   ├── productController.js  # Product CRUD
│   ├── inventoryController.js # Inventory read & update
│   ├── salesController.js    # Sales record management
│   ├── supplierController.js # Supplier CRUD
│   ├── forecastController.js # Trigger forecast, retrieve forecast
│   └── purchaseOrderController.js  # PO management
│
├── models/
│   ├── Product.js            # Product DB query functions
│   ├── Inventory.js          # Inventory DB query functions
│   ├── Sale.js               # Sales DB query functions
│   ├── Supplier.js           # Supplier DB query functions
│   ├── Forecast.js           # Forecast DB query functions
│   ├── PurchaseOrder.js      # PO DB query functions
│   └── User.js               # User auth DB query functions
│
├── middleware/
│   ├── auth.middleware.js    # JWT verification middleware
│   ├── validate.middleware.js # Input validation middleware
│   └── error.middleware.js   # Global error handler
│
└── config/
    ├── db.config.js          # Database file path configuration
    └── app.config.js         # App-level configuration (port, env)
```

### Analytics Modules

```
analytics/
├── scripts/
│   ├── verify.py             # Environment verification
│   ├── extract.py            # Extract data from SQLite
│   ├── clean.py              # Data cleaning pipeline
│   ├── eda.py                # Exploratory data analysis
│   ├── forecast.py           # Demand forecasting model
│   └── seed_data.py          # Generate historical seed records
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   └── 03_demand_forecasting.ipynb
│
└── datasets/
    ├── raw/
    └── clean/
```

---

## 5. Data Flow

### Standard Inventory Query Flow
```
Browser → GET /api/inventory/:product_id
       → Auth Middleware (verify JWT)
       → inventoryController.getInventory()
       → Inventory.findByProductId(id) (SQLite query)
       → JSON response → Browser renders data
```

### Demand Forecast Flow
```
Browser → POST /api/forecasts
       → Auth Middleware
       → forecastController.runForecast()
       → Spawn Python child process: python forecast.py --product_id <id>
       → forecast.py: reads SQLite sales data → cleans → runs ARIMA/sklearn → writes to forecasts table
       → forecastController reads result from forecasts table
       → JSON response → Browser renders chart
```

---

## 6. Authentication & Security

- **JWT Authentication:** Login endpoint returns a signed JWT token.
- **Middleware:** All protected routes validate the JWT header.
- **Role-Based Access:** Each route checks user role before executing.
- **Input Validation:** All request bodies are validated for type and range.
- **Parameterized Queries:** All SQLite queries use parameterized statements to prevent SQL injection.
- **Audit Logging:** All POST/PUT/PATCH/DELETE operations write to `audit_logs`.

---

## 7. Frontend Pages

| Page | Purpose |
|------|---------|
| `index.html` | Login page |
| `dashboard.html` | KPI overview dashboard |
| `products.html` | Product catalog management |
| `inventory.html` | Real-time inventory view and update |
| `sales.html` | Sales transaction entry |
| `suppliers.html` | Supplier management |
| `purchase-orders.html` | Purchase order tracking |
| `forecasts.html` | Demand forecast display |
| `reports.html` | Analytics report viewer |

---

## 8. Workflow Sequence

```
Day Login → Dashboard → View Inventory
         → Low-stock alert → Create Purchase Order
         → Supplier fulfills → Receive inventory → Update stock
         → Sales recorded → Demand forecast triggered → Forecast updated
         → Dashboard updated with new KPIs
```

---

*System design completed on Day 2 – 2026-06-29.*

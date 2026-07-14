# DEPLOYMENT_GUIDE.md

# AI Smart Inventory Management & Demand Forecasting System
# Deployment Guide — Version 1.0

**Prepared By:** Antigravity AI
**Date:** 2026-07-14
**Target Audience:** Developers, System Administrators

---

## Table of Contents

1. [Local Development Setup](#1-local-development-setup)
2. [Environment Variables](#2-environment-variables)
3. [Database Setup & Seeding](#3-database-setup--seeding)
4. [Python ML Environment](#4-python-ml-environment)
5. [Running the Backend Server](#5-running-the-backend-server)
6. [Running Automated Tests](#6-running-automated-tests)
7. [Production Deployment Checklist](#7-production-deployment-checklist)
8. [Production Environment (Linux/VPS)](#8-production-environment-linuxvps)
9. [Docker Deployment (Optional)](#9-docker-deployment-optional)
10. [Monitoring & Maintenance](#10-monitoring--maintenance)

---

## 1. Local Development Setup

### Prerequisites

| Tool | Minimum Version | Download |
|------|----------------|---------|
| Git | 2.40+ | https://git-scm.com |
| Node.js | 18.x LTS | https://nodejs.org |
| npm | 9.x+ | Bundled with Node.js |
| Python | 3.11+ | https://python.org |
| SQLite | 3.39+ | https://sqlite.org |

### Clone Repository

```bash
git clone https://github.com/<your-username>/AI_Smart_Inventory_Management.git
cd AI_Smart_Inventory_Management
```

### Install Backend Dependencies

```bash
cd app
npm install
```

---

## 2. Environment Variables

The backend reads from `app/.env`. Create or verify this file:

```env
PORT=5000
NODE_ENV=development
DB_PATH=../data/inventory.db
JWT_SECRET=your_secure_random_secret_here
```

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | HTTP server port |
| `NODE_ENV` | development | Environment mode (`development` or `production`) |
| `DB_PATH` | `../data/inventory.db` | Path to SQLite DB file (relative to `app/`) |
| `JWT_SECRET` | `supersecretkey` | Secret key for JWT signing — **change this in production** |

> **Security Note:** Never commit `.env` files to version control. Add them to `.gitignore`.

---

## 3. Database Setup & Seeding

### Automatic Schema Initialization
The database schema (tables, indexes, foreign keys) is **automatically created** when the server starts for the first time. No manual migration steps are required.

```bash
cd app
npm start
# Console output: "Database tables and indexes created/verified."
```

### Seed Historical Data

To populate the database with 50 products, 10 suppliers, 913+ sales, and 50 forecasts:

```bash
# From the project root
analytics\venv\Scripts\python.exe analytics\scripts\seed_data.py   # Windows
# OR
analytics/venv/bin/python analytics/scripts/seed_data.py            # macOS/Linux
```

### Verify Database Contents

```bash
cd app
node src/verify_db.js
```

Expected output:
```
✅ Table "products"        exists. Record count: 51
✅ Table "inventory"       exists. Record count: 50
✅ Table "sales"           exists. Record count: 913
✅ Table "forecasts"       exists. Record count: 50
✅ Table "suppliers"       exists. Record count: 10
✅ Table "purchase_orders" exists. Record count: 112
✅ Table "users"           exists. Record count: 5
✅ Table "audit_logs"      exists. Record count: 49
```

---

## 4. Python ML Environment

### Create Virtual Environment

```bash
cd analytics
python -m venv venv
```

### Activate Virtual Environment

```bash
# Windows (PowerShell or CMD)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:
- `pandas>=2.0.0` — Data manipulation
- `numpy>=1.24.0` — Numerical computing
- `scikit-learn>=1.2.0` — Machine learning models
- `statsmodels>=0.14.0` — Time series (ARIMA)
- `xgboost>=1.7.0` — Gradient boosting
- `matplotlib>=3.7.0` — Charting (EDA notebooks)
- `plotly>=5.13.0` — Interactive visualizations
- `PyYAML>=6.0` — Configuration engine
- `python-dotenv>=1.0.0` — Environment variable loading
- `pytest>=7.0.0` — Test framework

### Verify Python Environment

```bash
analytics\venv\Scripts\python.exe analytics\scripts\verify.py
```

---

## 5. Running the Backend Server

### Development Mode (with file watching)

```bash
cd app
npm run dev
```

### Production Mode

```bash
cd app
npm start
```

The server starts on `http://localhost:5000` (or the port specified in `.env`).

### Verify Health

```bash
curl http://localhost:5000/api/health
# Expected: {"status":"ok","message":"Smart Inventory API is running"}
```

### Access the Application

Open your browser at: **http://localhost:5000**

---

## 6. Running Automated Tests

### Backend Tests (Jest + Supertest)

```bash
cd app
npm test
```

Expected output:
```
PASS tests/errorHandler.test.js
PASS tests/validation.test.js
PASS tests/api.test.js (5.59s)

Test Suites: 3 passed, 3 total
Tests:       40 passed, 40 total
Time:        ~6s
```

### Python Pipeline Tests (pytest)

```bash
# From project root
analytics\venv\Scripts\python.exe -m pytest
```

Expected output:
```
10 passed, 20 warnings in 3.25s
```

> The 20 warnings are non-breaking Pandas 4.x deprecation notices.

---

## 7. Production Deployment Checklist

Before deploying to any production or staging environment, verify:

- [ ] `JWT_SECRET` is set to a cryptographically secure random string (min 32 chars)
- [ ] `NODE_ENV` is set to `production`
- [ ] `.env` file is excluded from version control (`.gitignore`)
- [ ] Database file is backed up to a secure location
- [ ] All 40 Jest tests pass
- [ ] All 10 pytest tests pass
- [ ] Health endpoint returns `200 OK`
- [ ] HTTPS configured (via reverse proxy such as nginx or Caddy)
- [ ] Rate limiting enabled on authentication endpoints
- [ ] Error messages do not expose internal stack traces in `production` mode

---

## 8. Production Environment (Linux/VPS)

### Install Node.js (Ubuntu/Debian)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Install Python

```bash
sudo apt-get install python3.11 python3.11-venv python3-pip -y
```

### Clone & Install

```bash
git clone https://github.com/<your-username>/AI_Smart_Inventory_Management.git
cd AI_Smart_Inventory_Management/app
npm install --production
```

### Run with PM2 (Process Manager)

```bash
npm install -g pm2
pm2 start src/server.js --name "smart-inventory-api"
pm2 save
pm2 startup
```

### nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 9. Docker Deployment (Optional)

### Dockerfile (Backend)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY app/package*.json ./
RUN npm install --production
COPY app/ .
EXPOSE 5000
CMD ["node", "src/server.js"]
```

### Build & Run

```bash
docker build -t smart-inventory-api .
docker run -d -p 5000:5000 \
  -e JWT_SECRET=your_secret_here \
  -e NODE_ENV=production \
  -v $(pwd)/data:/data \
  smart-inventory-api
```

---

## 10. Monitoring & Maintenance

### Log Files

Server logs are written to `logs/` directory (if configured) and to stdout/stderr when running with PM2.

View live logs:
```bash
pm2 logs smart-inventory-api
```

### Database Backup

```bash
# Copy the SQLite file
cp data/inventory.db data/inventory_backup_$(date +%Y%m%d).db
```

### Model Retraining (Weekly Recommended)

```bash
analytics\venv\Scripts\python.exe analytics\scripts\model_optimization.py
```

This script retrains and re-evaluates all 5 ML models on fresh data and updates the champion model.

### Health Check Endpoint

```
GET /api/health
Response: {"status":"ok","message":"Smart Inventory API is running"}
```

Use this endpoint with an external uptime monitoring service (e.g., UptimeRobot, Better Uptime) to receive alerts on server downtime.

---

*Deployment Guide v1.0 — AI Smart Inventory Management & Demand Forecasting System*
*Prepared by Antigravity AI — 2026-07-14*

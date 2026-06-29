# API Specification

**Project:** AI Smart Inventory Management & Demand Forecasting System
**Version:** 1.0
**Phase:** Phase 1 – API Design
**Day:** Day 2
**Status:** COMPLETED
**Date:** 2026-06-29

---

## 1. Base URL

```
http://localhost:5000/api
```

---

## 2. Authentication

All endpoints (except login) require a JWT Bearer token in the request header.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

**Token Validity:** 8 hours from login.

---

## 3. Global Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "statusCode": 400
}
```

---

## 4. HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK – Request succeeded |
| 201 | Created – Resource created successfully |
| 204 | No Content – Delete succeeded |
| 400 | Bad Request – Validation failed |
| 401 | Unauthorized – Missing or invalid token |
| 403 | Forbidden – Insufficient role permissions |
| 404 | Not Found – Resource does not exist |
| 500 | Internal Server Error – Unexpected server error |

---

## 5. Authentication Endpoints

### POST /api/auth/login
Login and receive a JWT access token.

**Request Body:**
```json
{
  "email": "manager@inventory.com",
  "password": "securepassword"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
    "token_type": "Bearer",
    "user": {
      "user_id": "uuid",
      "email": "manager@inventory.com",
      "full_name": "Ravi Kumar",
      "role": "Manager"
    }
  },
  "message": "Login successful"
}
```

**Validation Rules:**
- `email` must be a valid email format.
- `password` must be at least 8 characters.

---

### POST /api/auth/logout
Invalidate current session.

**Headers:** `Authorization: Bearer <token>`

**Success Response (204):** No content.

---

## 6. Product Endpoints

### GET /api/products
Retrieve all products.

**Query Parameters (optional):**
- `category=Electronics` – Filter by category
- `search=laptop` – Search by name or SKU

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "product_id": "uuid",
      "sku": "ELEC-001",
      "name": "Laptop Pro 15",
      "category": "Electronics",
      "unit_cost": 45000.00,
      "reorder_point": 10,
      "created_at": "2026-06-01T10:00:00Z"
    }
  ]
}
```

---

### POST /api/products
Create a new product.

**Request Body:**
```json
{
  "sku": "ELEC-002",
  "name": "Wireless Mouse",
  "category": "Accessories",
  "unit_cost": 850.00,
  "reorder_point": 20
}
```

**Validation Rules:**
- `sku` – required, unique, string, max 50 chars.
- `name` – required, string, max 200 chars.
- `unit_cost` – required, number >= 0.
- `reorder_point` – optional, integer >= 0, default 10.

**Success Response (201):** Created product object.

---

### GET /api/products/:id
Get a single product by ID.

**Success Response (200):** Single product object.

**Error Response (404):** Product not found.

---

### PUT /api/products/:id
Update an existing product.

**Request Body:** Same as POST (all fields optional for partial update).

**Success Response (200):** Updated product object.

---

### DELETE /api/products/:id
Delete a product. *Admin role required.*

**Success Response (204):** No content.

**Error:** Cannot delete if inventory, sales, or purchase orders reference this product.

---

## 7. Inventory Endpoints

### GET /api/inventory
Retrieve all inventory records.

**Success Response (200):** List of inventory objects with product details joined.

---

### GET /api/inventory/:product_id
Get current stock for a specific product.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "inventory_id": "uuid",
    "product_id": "uuid",
    "product_name": "Laptop Pro 15",
    "sku": "ELEC-001",
    "location": "Warehouse-A",
    "quantity": 45,
    "last_updated": "2026-06-29T10:00:00Z",
    "low_stock": false
  }
}
```

---

### PATCH /api/inventory/:product_id
Update stock quantity for a product.

**Request Body:**
```json
{
  "quantity": 60,
  "location": "Warehouse-A",
  "reason": "Physical stock count adjustment"
}
```

**Validation Rules:**
- `quantity` – required, integer >= 0.
- `reason` – required string for audit log.

**Success Response (200):** Updated inventory object.

*Writes audit log entry automatically.*

---

## 8. Sales Endpoints

### GET /api/sales
Retrieve all sales records.

**Query Parameters:**
- `product_id=uuid` – Filter by product
- `from=2026-01-01&to=2026-06-30` – Date range filter

**Success Response (200):** List of sales records.

---

### POST /api/sales
Record a new sales transaction.

**Request Body:**
```json
{
  "product_id": "uuid",
  "sale_date": "2026-06-29",
  "quantity": 3,
  "unit_price": 45000.00,
  "customer_type": "Retail"
}
```

**Validation Rules:**
- `product_id` – required, must exist in products.
- `sale_date` – required, ISO8601 date format.
- `quantity` – required, integer > 0.
- `unit_price` – required, number > 0.
- Stock is automatically decremented in the inventory table.

**Success Response (201):** Created sale object.

---

## 9. Supplier Endpoints

### GET /api/suppliers
Retrieve all suppliers.

**Success Response (200):** List of supplier objects.

---

### POST /api/suppliers
Create a new supplier.

**Request Body:**
```json
{
  "name": "TechDistributor Ltd",
  "contact_person": "Anand Sharma",
  "contact_email": "anand@techdist.com",
  "contact_phone": "+91-9876543210",
  "lead_time_days": 7,
  "rating": 4.2
}
```

**Success Response (201):** Created supplier object.

---

### PUT /api/suppliers/:id
Update supplier information.

**Success Response (200):** Updated supplier object.

---

### DELETE /api/suppliers/:id
Delete a supplier. *Admin role required.*

**Error:** Cannot delete if active purchase orders reference this supplier.

---

## 10. Purchase Order Endpoints

### GET /api/purchase-orders
Retrieve all purchase orders.

**Query Parameters:**
- `status=Pending` – Filter by status
- `supplier_id=uuid` – Filter by supplier

---

### POST /api/purchase-orders
Create a new purchase order.

**Request Body:**
```json
{
  "supplier_id": "uuid",
  "product_id": "uuid",
  "quantity": 50,
  "unit_cost": 42000.00,
  "expected_delivery": "2026-07-10",
  "notes": "Urgent reorder due to low stock"
}
```

**Success Response (201):** Created PO object with status "Pending".

---

### GET /api/purchase-orders/:id
Retrieve a specific purchase order.

**Success Response (200):** Single PO object.

---

### PATCH /api/purchase-orders/:id
Update PO status.

**Request Body:**
```json
{
  "status": "Received",
  "actual_delivery": "2026-07-08"
}
```

**Business Logic:**
- When status changes to "Received", inventory is automatically incremented by the PO quantity.

**Success Response (200):** Updated PO object.

---

## 11. Forecast Endpoints

### POST /api/forecasts
Trigger demand forecast for a product.

**Request Body:**
```json
{
  "product_id": "uuid",
  "horizon_days": 30
}
```

**Processing:**
- Invokes Python script `analytics/scripts/forecast.py`.
- Reads historical sales data from SQLite.
- Runs ARIMA or Linear Regression model.
- Writes forecast results to the `forecasts` table.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "product_id": "uuid",
    "forecast_date": "2026-07-29",
    "predicted_qty": 120,
    "confidence_low": 95,
    "confidence_high": 145,
    "model_used": "ARIMA",
    "generated_at": "2026-06-29T22:30:00Z"
  }
}
```

---

### GET /api/forecasts/:product_id
Retrieve the most recent forecast for a product.

**Success Response (200):** Latest forecast object.

---

## 12. Dashboard / KPI Endpoints

### GET /api/dashboard/summary
Returns aggregated KPI metrics for the dashboard.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_products": 50,
    "low_stock_count": 7,
    "total_inventory_value": 2350000.00,
    "pending_orders": 5,
    "stockout_rate": 4.2,
    "monthly_sales_total": 1200000.00
  }
}
```

---

## 13. Validation Rules Summary

| Field Type | Rule |
|-----------|------|
| UUID fields | Valid UUID string format |
| Date fields | ISO8601 format (YYYY-MM-DD) |
| Timestamp fields | ISO8601 format with time zone |
| Numeric fields | Non-negative where applicable |
| Email fields | Valid email address format |
| String fields | Max length enforced (varies per field) |
| Status enums | Must be one of the defined allowed values |

---

*API specification completed on Day 2 – 2026-06-29.*

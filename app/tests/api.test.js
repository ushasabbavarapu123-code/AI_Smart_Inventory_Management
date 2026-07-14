// app/tests/api.test.js

const request = require('supertest');
const app = require('../src/server');
const { closeDatabase, getDatabase } = require('../src/database');

let token;
let testProductId;
let testSupplierId;
let testPoId;

beforeAll(async () => {
  // Wait a small bit for DB to initialize (done in server.js when imported)
  await new Promise((resolve) => setTimeout(resolve, 1000));
});

afterAll(async () => {
  await closeDatabase();
});

describe('Smart Inventory API Tests', () => {

  // --- HEALTH CHECK ---
  describe('GET /api/health', () => {
    it('should return 200 and status ok', async () => {
      const res = await request(app).get('/api/health');
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('status', 'ok');
    });
  });

  // --- AUTHENTICATION ---
  describe('POST /api/auth/login', () => {
    it('should fail with invalid credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ email: 'manager@smartinventory.com', password: 'wrongpassword' });
      expect(res.statusCode).toBe(401);
      expect(res.body.success).toBe(false);
    });

    it('should succeed with valid credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ email: 'manager@smartinventory.com', password: 'securepassword' });
      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('access_token');
      token = res.body.data.access_token;
    });
  });

  // --- ROUTE SECURITY ---
  describe('Protected Route Check', () => {
    it('should block requests to /api/products without a token', async () => {
      const res = await request(app).get('/api/products');
      expect(res.statusCode).toBe(401);
      expect(res.body.success).toBe(false);
    });
  });

  // --- PRODUCTS & SUPPLIERS DATA GATHERING ---
  describe('Data Setup Verification', () => {
    it('should retrieve products and suppliers using token', async () => {
      const prodRes = await request(app)
        .get('/api/products')
        .set('Authorization', `Bearer ${token}`);
      expect(prodRes.statusCode).toBe(200);
      expect(prodRes.body.data.length).toBeGreaterThan(0);
      testProductId = prodRes.body.data[0].product_id;

      const supRes = await request(app)
        .get('/api/suppliers')
        .set('Authorization', `Bearer ${token}`);
      expect(supRes.statusCode).toBe(200);
      expect(supRes.body.data.length).toBeGreaterThan(0);
      testSupplierId = supRes.body.data[0].supplier_id;
    });
  });

  // --- SALES RESOURCE & INVENTORY DECREMENT ---
  describe('POST /api/sales', () => {
    it('should fail validation when payload is incomplete or invalid', async () => {
      const res = await request(app)
        .post('/api/sales')
        .set('Authorization', `Bearer ${token}`)
        .send({ product_id: testProductId, sale_date: 'invalid-date', quantity: -5 });
      expect(res.statusCode).toBe(400);
      expect(res.body.success).toBe(false);
    });

    it('should successfully record sale and decrement inventory', async () => {
      // First, get starting quantity from DB
      const db = getDatabase();
      const getQty = () => new Promise((resolve) => {
        db.get('SELECT quantity FROM inventory WHERE product_id = ?', [testProductId], (err, row) => {
          resolve(row ? row.quantity : 0);
        });
      });

      const startingQty = await getQty();

      const res = await request(app)
        .post('/api/sales')
        .set('Authorization', `Bearer ${token}`)
        .send({
          product_id: testProductId,
          sale_date: new Date().toISOString().split('T')[0],
          quantity: 1,
          unit_price: 1500.00,
          customer_type: 'Retail'
        });

      expect(res.statusCode).toBe(201);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('sale_id');

      const endingQty = await getQty();
      expect(endingQty).toBe(startingQty - 1);
    });
  });

  // --- PURCHASE ORDERS & INVENTORY INCREMENT ---
  describe('Purchase Orders CRUD & Automatic Increment', () => {
    it('should successfully create a new PO with Pending status', async () => {
      const res = await request(app)
        .post('/api/purchase-orders')
        .set('Authorization', `Bearer ${token}`)
        .send({
          supplier_id: testSupplierId,
          product_id: testProductId,
          quantity: 20,
          unit_cost: 900.00,
          expected_delivery: '2026-07-20',
          notes: 'Test PO from automated test suite'
        });

      expect(res.statusCode).toBe(201);
      expect(res.body.success).toBe(true);
      expect(res.body.data.status).toBe('Pending');
      testPoId = res.body.data.po_id;
    });

    it('should transition status to Received and increment product inventory', async () => {
      const db = getDatabase();
      const getQty = () => new Promise((resolve) => {
        db.get('SELECT quantity FROM inventory WHERE product_id = ?', [testProductId], (err, row) => {
          resolve(row ? row.quantity : 0);
        });
      });

      const startingQty = await getQty();

      const res = await request(app)
        .patch(`/api/purchase-orders/${testPoId}`)
        .set('Authorization', `Bearer ${token}`)
        .send({
          status: 'Received',
          actual_delivery: new Date().toISOString().split('T')[0]
        });

      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data.status).toBe('Received');

      const endingQty = await getQty();
      expect(endingQty).toBe(startingQty + 20);
    });
  });

  // --- FORECASTING ---
  describe('POST /api/forecasts', () => {
    it('should successfully trigger a demand forecast', async () => {
      const res = await request(app)
        .post('/api/forecasts')
        .set('Authorization', `Bearer ${token}`)
        .send({
          product_id: testProductId,
          horizon_days: 30
        });

      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('predicted_qty');
      expect(res.body.data).toHaveProperty('model_used');
    }, 30000);

    it('should successfully fetch the latest forecast for the product', async () => {
      const res = await request(app)
        .get(`/api/forecasts/${testProductId}`)
        .set('Authorization', `Bearer ${token}`);

      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data.product_id).toBe(testProductId);
    });
  });

  // --- DASHBOARD SUMMARY ---
  describe('GET /api/dashboard/summary', () => {
    it('should successfully fetch KPI metrics', async () => {
      const res = await request(app)
        .get('/api/dashboard/summary')
        .set('Authorization', `Bearer ${token}`);

      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('total_products');
      expect(res.body.data).toHaveProperty('low_stock_count');
      expect(res.body.data).toHaveProperty('total_inventory_value');
    });
  });

});

// app/tests/validation.test.js

const {
  validateProduct,
  validateSupplier,
  validateInventoryUpdate,
  validateLogin,
  validateSale,
  validatePurchaseOrder,
  validatePOStatusUpdate,
  validateForecastTrigger
} = require('../middleware/validation');

describe('Validation Middleware Unit Tests', () => {
  let mockReq;
  let mockRes;
  let nextFunction;

  beforeEach(() => {
    mockReq = {
      body: {},
      method: 'POST'
    };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis()
    };
    nextFunction = jest.fn();
  });

  // --- validateProduct Tests ---
  describe('validateProduct', () => {
    it('should pass validation for a valid POST product', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        sku: 'TEST-SKU-1',
        name: 'Test Product',
        category: 'Electronics',
        unit_cost: 99.99,
        reorder_point: 10
      };

      validateProduct(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
      expect(mockRes.status).not.toHaveBeenCalled();
    });

    it('should fail validation for POST when sku is missing', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        name: 'Test Product',
        unit_cost: 99.99
      };

      validateProduct(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        error: expect.stringContaining('sku')
      }));
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should fail validation for POST when unit_cost is negative', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        sku: 'TEST-SKU-1',
        name: 'Test Product',
        unit_cost: -5
      };

      validateProduct(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should pass validation for PUT when only modifying name', () => {
      mockReq.method = 'PUT';
      mockReq.body = {
        name: 'Updated Name'
      };

      validateProduct(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail validation for PUT when sku is empty', () => {
      mockReq.method = 'PUT';
      mockReq.body = {
        sku: ''
      };

      validateProduct(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(nextFunction).not.toHaveBeenCalled();
    });
  });

  // --- validateSupplier Tests ---
  describe('validateSupplier', () => {
    it('should pass validation for a valid POST supplier', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        name: 'Global Supplier Inc.',
        contact_email: 'contact@globalsupplier.com',
        lead_time_days: 7,
        rating: 4.5
      };

      validateSupplier(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail validation for POST if lead_time_days is non-integer or <= 0', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        name: 'Global Supplier Inc.',
        lead_time_days: 0
      };

      validateSupplier(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should fail validation if contact_email is invalid format', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        name: 'Global Supplier Inc.',
        lead_time_days: 7,
        contact_email: 'invalid-email-address'
      };

      validateSupplier(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should fail validation if rating is out of bounds (e.g. 5.5)', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        name: 'Global Supplier Inc.',
        lead_time_days: 7,
        rating: 5.5
      };

      validateSupplier(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });

  // --- validateInventoryUpdate Tests ---
  describe('validateInventoryUpdate', () => {
    it('should pass validation for a valid inventory update', () => {
      mockReq.body = {
        quantity: 50,
        reason: 'Restocking'
      };

      validateInventoryUpdate(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail if quantity is negative', () => {
      mockReq.body = {
        quantity: -10,
        reason: 'Correction'
      };

      validateInventoryUpdate(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });

    it('should fail if reason is empty', () => {
      mockReq.body = {
        quantity: 10,
        reason: ''
      };

      validateInventoryUpdate(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });

  // --- validateLogin Tests ---
  describe('validateLogin', () => {
    it('should pass validation for valid email and password', () => {
      mockReq.body = {
        email: 'user@example.com',
        password: 'securepassword123'
      };

      validateLogin(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail validation for invalid email', () => {
      mockReq.body = {
        email: 'invalidemail',
        password: 'securepassword123'
      };

      validateLogin(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });

    it('should fail validation for too short password', () => {
      mockReq.body = {
        email: 'user@example.com',
        password: '123'
      };

      validateLogin(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });

  // --- validateSale Tests ---
  describe('validateSale', () => {
    it('should pass validation for valid sale details', () => {
      mockReq.body = {
        product_id: 'prod-uuid-123',
        sale_date: '2026-07-14',
        quantity: 5,
        unit_price: 15.50
      };

      validateSale(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail if product_id is missing', () => {
      mockReq.body = {
        sale_date: '2026-07-14',
        quantity: 5,
        unit_price: 15.50
      };

      validateSale(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });

    it('should fail if sale_date format is incorrect', () => {
      mockReq.body = {
        product_id: 'prod-uuid-123',
        sale_date: '14-07-2026',
        quantity: 5,
        unit_price: 15.50
      };

      validateSale(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });

    it('should fail if quantity is 0 or negative', () => {
      mockReq.body = {
        product_id: 'prod-uuid-123',
        sale_date: '2026-07-14',
        quantity: 0,
        unit_price: 15.50
      };

      validateSale(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });

  // --- validatePurchaseOrder Tests ---
  describe('validatePurchaseOrder', () => {
    it('should pass validation for a valid purchase order', () => {
      mockReq.body = {
        supplier_id: 'sup-uuid-123',
        product_id: 'prod-uuid-123',
        quantity: 100,
        unit_cost: 12.00,
        expected_delivery: '2026-08-01'
      };

      validatePurchaseOrder(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail if expected_delivery is not YYYY-MM-DD', () => {
      mockReq.body = {
        supplier_id: 'sup-uuid-123',
        product_id: 'prod-uuid-123',
        quantity: 100,
        unit_cost: 12.00,
        expected_delivery: '2026/08/01'
      };

      validatePurchaseOrder(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });

  // --- validatePOStatusUpdate Tests ---
  describe('validatePOStatusUpdate', () => {
    it('should pass validation for a valid status update', () => {
      mockReq.body = {
        status: 'Shipped'
      };

      validatePOStatusUpdate(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail for an invalid status update', () => {
      mockReq.body = {
        status: 'Delivered' // not in valid list
      };

      validatePOStatusUpdate(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });

  // --- validateForecastTrigger Tests ---
  describe('validateForecastTrigger', () => {
    it('should pass validation for a valid product and horizon', () => {
      mockReq.body = {
        product_id: 'prod-uuid-123',
        horizon_days: 90
      };

      validateForecastTrigger(mockReq, mockRes, nextFunction);
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should fail if horizon_days is out of range', () => {
      mockReq.body = {
        product_id: 'prod-uuid-123',
        horizon_days: 400
      };

      validateForecastTrigger(mockReq, mockRes, nextFunction);
      expect(mockRes.status).toHaveBeenCalledWith(400);
    });
  });
});

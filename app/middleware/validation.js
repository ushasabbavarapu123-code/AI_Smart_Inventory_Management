const validateProduct = (req, res, next) => {
  const isPost = req.method === 'POST';
  const { sku, name, category, unit_cost, reorder_point } = req.body;

  if (isPost) {
    if (!sku || typeof sku !== 'string' || sku.trim() === '') {
      return res.status(400).json({ success: false, error: 'Validation failed: sku is required and must be a non-empty string', statusCode: 400 });
    }
    if (!name || typeof name !== 'string' || name.trim() === '') {
      return res.status(400).json({ success: false, error: 'Validation failed: name is required and must be a non-empty string', statusCode: 400 });
    }
    if (unit_cost === undefined || typeof unit_cost !== 'number' || unit_cost < 0) {
      return res.status(400).json({ success: false, error: 'Validation failed: unit_cost is required and must be a non-negative number', statusCode: 400 });
    }
  } else {
    // For PUT, if fields are provided, they must validate
    if (sku !== undefined && (typeof sku !== 'string' || sku.trim() === '')) {
      return res.status(400).json({ success: false, error: 'Validation failed: sku must be a non-empty string', statusCode: 400 });
    }
    if (name !== undefined && (typeof name !== 'string' || name.trim() === '')) {
      return res.status(400).json({ success: false, error: 'Validation failed: name must be a non-empty string', statusCode: 400 });
    }
    if (unit_cost !== undefined && (typeof unit_cost !== 'number' || unit_cost < 0)) {
      return res.status(400).json({ success: false, error: 'Validation failed: unit_cost must be a non-negative number', statusCode: 400 });
    }
  }

  if (reorder_point !== undefined && (!Number.isInteger(reorder_point) || reorder_point < 0)) {
    return res.status(400).json({ success: false, error: 'Validation failed: reorder_point must be a non-negative integer', statusCode: 400 });
  }

  next();
};

const validateSupplier = (req, res, next) => {
  const isPost = req.method === 'POST';
  const { name, contact_email, lead_time_days, rating } = req.body;

  if (isPost) {
    if (!name || typeof name !== 'string' || name.trim() === '') {
      return res.status(400).json({ success: false, error: 'Validation failed: name is required and must be a non-empty string', statusCode: 400 });
    }
    if (lead_time_days === undefined || !Number.isInteger(lead_time_days) || lead_time_days <= 0) {
      return res.status(400).json({ success: false, error: 'Validation failed: lead_time_days is required and must be a positive integer', statusCode: 400 });
    }
  } else {
    if (name !== undefined && (typeof name !== 'string' || name.trim() === '')) {
      return res.status(400).json({ success: false, error: 'Validation failed: name must be a non-empty string', statusCode: 400 });
    }
    if (lead_time_days !== undefined && (!Number.isInteger(lead_time_days) || lead_time_days <= 0)) {
      return res.status(400).json({ success: false, error: 'Validation failed: lead_time_days must be a positive integer', statusCode: 400 });
    }
  }

  if (contact_email !== undefined && contact_email !== null && contact_email !== '') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(contact_email)) {
      return res.status(400).json({ success: false, error: 'Validation failed: contact_email must be a valid email address', statusCode: 400 });
    }
  }

  if (rating !== undefined && rating !== null) {
    if (typeof rating !== 'number' || rating < 1.0 || rating > 5.0) {
      return res.status(400).json({ success: false, error: 'Validation failed: rating must be a number between 1.0 and 5.0', statusCode: 400 });
    }
  }

  next();
};

const validateInventoryUpdate = (req, res, next) => {
  const { quantity, reason } = req.body;

  if (quantity === undefined || !Number.isInteger(quantity) || quantity < 0) {
    return res.status(400).json({ success: false, error: 'Validation failed: quantity is required and must be a non-negative integer', statusCode: 400 });
  }

  if (!reason || typeof reason !== 'string' || reason.trim() === '') {
    return res.status(400).json({ success: false, error: 'Validation failed: reason is required and must be a non-empty string', statusCode: 400 });
  }

  next();
};

// ---- Login Validator ----
const validateLogin = (req, res, next) => {
  const { email, password } = req.body;

  if (!email || typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ success: false, error: 'Validation failed: email must be a valid email address', statusCode: 400 });
  }
  if (!password || typeof password !== 'string' || password.length < 6) {
    return res.status(400).json({ success: false, error: 'Validation failed: password is required and must be at least 6 characters', statusCode: 400 });
  }

  next();
};

// ---- Sale Validator ----
const validateSale = (req, res, next) => {
  const { product_id, sale_date, quantity, unit_price } = req.body;

  if (!product_id || typeof product_id !== 'string' || product_id.trim() === '') {
    return res.status(400).json({ success: false, error: 'Validation failed: product_id is required', statusCode: 400 });
  }
  if (!sale_date || !/^\d{4}-\d{2}-\d{2}$/.test(sale_date)) {
    return res.status(400).json({ success: false, error: 'Validation failed: sale_date is required in YYYY-MM-DD format', statusCode: 400 });
  }
  if (quantity === undefined || !Number.isInteger(quantity) || quantity <= 0) {
    return res.status(400).json({ success: false, error: 'Validation failed: quantity is required and must be a positive integer', statusCode: 400 });
  }
  if (unit_price === undefined || typeof unit_price !== 'number' || unit_price <= 0) {
    return res.status(400).json({ success: false, error: 'Validation failed: unit_price is required and must be a positive number', statusCode: 400 });
  }

  next();
};

// ---- Purchase Order Validator ----
const VALID_PO_STATUSES = ['Pending', 'Confirmed', 'Shipped', 'Received', 'Cancelled'];

const validatePurchaseOrder = (req, res, next) => {
  const { supplier_id, product_id, quantity, unit_cost, expected_delivery } = req.body;

  if (!supplier_id || typeof supplier_id !== 'string' || supplier_id.trim() === '') {
    return res.status(400).json({ success: false, error: 'Validation failed: supplier_id is required', statusCode: 400 });
  }
  if (!product_id || typeof product_id !== 'string' || product_id.trim() === '') {
    return res.status(400).json({ success: false, error: 'Validation failed: product_id is required', statusCode: 400 });
  }
  if (quantity === undefined || !Number.isInteger(quantity) || quantity <= 0) {
    return res.status(400).json({ success: false, error: 'Validation failed: quantity is required and must be a positive integer', statusCode: 400 });
  }
  if (unit_cost === undefined || typeof unit_cost !== 'number' || unit_cost <= 0) {
    return res.status(400).json({ success: false, error: 'Validation failed: unit_cost is required and must be a positive number', statusCode: 400 });
  }
  if (!expected_delivery || !/^\d{4}-\d{2}-\d{2}$/.test(expected_delivery)) {
    return res.status(400).json({ success: false, error: 'Validation failed: expected_delivery is required in YYYY-MM-DD format', statusCode: 400 });
  }

  next();
};

// ---- PO Status Update Validator ----
const validatePOStatusUpdate = (req, res, next) => {
  const { status } = req.body;

  if (!status || !VALID_PO_STATUSES.includes(status)) {
    return res.status(400).json({
      success: false,
      error: `Validation failed: status must be one of: ${VALID_PO_STATUSES.join(', ')}`,
      statusCode: 400
    });
  }

  next();
};

// ---- Forecast Trigger Validator ----
const validateForecastTrigger = (req, res, next) => {
  const { product_id, horizon_days } = req.body;

  if (!product_id || typeof product_id !== 'string' || product_id.trim() === '') {
    return res.status(400).json({ success: false, error: 'Validation failed: product_id is required', statusCode: 400 });
  }
  if (horizon_days !== undefined && (!Number.isInteger(horizon_days) || horizon_days < 1 || horizon_days > 365)) {
    return res.status(400).json({ success: false, error: 'Validation failed: horizon_days must be an integer between 1 and 365', statusCode: 400 });
  }

  next();
};

module.exports = {
  validateProduct,
  validateSupplier,
  validateInventoryUpdate,
  validateLogin,
  validateSale,
  validatePurchaseOrder,
  validatePOStatusUpdate,
  validateForecastTrigger
};

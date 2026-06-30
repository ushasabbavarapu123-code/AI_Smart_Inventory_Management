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

module.exports = {
  validateProduct,
  validateSupplier,
  validateInventoryUpdate
};

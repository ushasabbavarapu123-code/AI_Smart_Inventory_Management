// app/src/controllers/supplier.controller.js

const {
  createSupplier,
  getAllSuppliers,
  getSupplierById,
  updateSupplier,
  deleteSupplier,
} = require('../models/supplier.model');

// GET /api/suppliers
async function getAll(req, res, next) {
  try {
    const suppliers = await getAllSuppliers();
    res.json({ success: true, data: suppliers });
  } catch (err) {
    next(err);
  }
}

// GET /api/suppliers/:id
async function getById(req, res, next) {
  try {
    const supplier = await getSupplierById(req.params.id);
    if (!supplier) return res.status(404).json({ success: false, error: 'Supplier not found', statusCode: 404 });
    res.json({ success: true, data: supplier });
  } catch (err) {
    next(err);
  }
}

// POST /api/suppliers
async function create(req, res, next) {
  try {
    const newSupplier = await createSupplier(req.body);
    res.status(201).json({ success: true, data: newSupplier });
  } catch (err) {
    next(err);
  }
}

// PUT /api/suppliers/:id
async function update(req, res, next) {
  try {
    const updated = await updateSupplier(req.params.id, req.body);
    res.json({ success: true, data: updated });
  } catch (err) {
    next(err);
  }
}

// DELETE /api/suppliers/:id
async function remove(req, res, next) {
  try {
    await deleteSupplier(req.params.id);
    res.json({ success: true, message: 'Supplier deleted' });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  getAll,
  getById,
  create,
  update,
  remove,
};

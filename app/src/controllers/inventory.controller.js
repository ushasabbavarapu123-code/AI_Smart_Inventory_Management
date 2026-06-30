// app/src/controllers/inventory.controller.js

const {
  createInventory,
  getAllInventory,
  getInventoryById,
  updateInventory,
  deleteInventory,
} = require('../models/inventory.model');

// GET /api/inventory
async function getAll(req, res, next) {
  try {
    const items = await getAllInventory();
    res.json({ success: true, data: items });
  } catch (err) {
    next(err);
  }
}

// GET /api/inventory/:id
async function getById(req, res, next) {
  try {
    const item = await getInventoryById(req.params.id);
    if (!item) return res.status(404).json({ success: false, error: 'Inventory record not found', statusCode: 404 });
    res.json({ success: true, data: item });
  } catch (err) {
    next(err);
  }
}

// POST /api/inventory
async function create(req, res, next) {
  try {
    const newItem = await createInventory(req.body);
    res.status(201).json({ success: true, data: newItem });
  } catch (err) {
    next(err);
  }
}

// PUT /api/inventory/:id
async function update(req, res, next) {
  try {
    const updated = await updateInventory(req.params.id, req.body);
    res.json({ success: true, data: updated });
  } catch (err) {
    next(err);
  }
}

// DELETE /api/inventory/:id
async function remove(req, res, next) {
  try {
    await deleteInventory(req.params.id);
    res.json({ success: true, message: 'Inventory record deleted' });
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

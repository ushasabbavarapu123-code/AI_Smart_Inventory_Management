// app/src/controllers/purchaseOrder.controller.js

const poModel = require('../models/purchaseOrder.model');

async function getAll(req, res, next) {
  try {
    const filters = {
      status: req.query.status,
      supplier_id: req.query.supplier_id
    };
    const pos = await poModel.getAllPurchaseOrders(filters);
    res.json({ success: true, data: pos });
  } catch (err) {
    next(err);
  }
}

async function getById(req, res, next) {
  try {
    const po = await poModel.getPurchaseOrderById(req.params.id);
    if (!po) return res.status(404).json({ success: false, error: 'Purchase order not found', statusCode: 404 });
    res.json({ success: true, data: po });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const newPO = await poModel.createPurchaseOrder(req.body);
    res.status(201).json({ success: true, data: newPO, message: 'Purchase order created successfully' });
  } catch (err) {
    next(err);
  }
}

async function updateStatus(req, res, next) {
  try {
    const user_id = req.user ? req.user.user_id : 'system';
    const { status, actual_delivery } = req.body;
    const updated = await poModel.updatePurchaseOrderStatus(req.params.id, status, actual_delivery, user_id);
    res.json({ success: true, data: updated, message: 'Purchase order status updated successfully' });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  getAll,
  getById,
  create,
  updateStatus
};

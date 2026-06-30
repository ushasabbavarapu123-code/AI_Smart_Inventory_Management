// app/src/controllers/sales.controller.js

const salesModel = require('../models/sales.model');

async function getAll(req, res, next) {
  try {
    const filters = {
      product_id: req.query.product_id,
      from: req.query.from,
      to: req.query.to
    };
    const sales = await salesModel.getAllSales(filters);
    res.json({ success: true, data: sales });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const user_id = req.user ? req.user.user_id : 'system';
    const sale = await salesModel.createSale(req.body, user_id);
    res.status(201).json({ success: true, data: sale, message: 'Sale recorded successfully' });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  getAll,
  create
};

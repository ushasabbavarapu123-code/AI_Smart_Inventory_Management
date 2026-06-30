// app/src/controllers/product.controller.js

const {
  createProduct,
  getAllProducts,
  getProductById,
  updateProduct,
  deleteProduct,
} = require('../models/product.model');

// GET /api/products
async function getAll(req, res, next) {
  try {
    const products = await getAllProducts();
    res.json({ success: true, data: products });
  } catch (err) {
    next(err);
  }
}

// GET /api/products/:id
async function getById(req, res, next) {
  try {
    const product = await getProductById(req.params.id);
    if (!product) return res.status(404).json({ success: false, error: 'Product not found', statusCode: 404 });
    res.json({ success: true, data: product });
  } catch (err) {
    next(err);
  }
}

// POST /api/products
async function create(req, res, next) {
  try {
    const newProduct = await createProduct(req.body);
    res.status(201).json({ success: true, data: newProduct });
  } catch (err) {
    next(err);
  }
}

// PUT /api/products/:id
async function update(req, res, next) {
  try {
    const updated = await updateProduct(req.params.id, req.body);
    res.json({ success: true, data: updated });
  } catch (err) {
    next(err);
  }
}

// DELETE /api/products/:id
async function remove(req, res, next) {
  try {
    await deleteProduct(req.params.id);
    res.json({ success: true, message: 'Product deleted' });
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

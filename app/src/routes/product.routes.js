// app/src/routes/product.routes.js

const express = require('express');
const router = express.Router();

const productController = require('../controllers/product.controller');
const auth = require('../../middleware/auth');
const validation = require('../../middleware/validation');

// Apply auth to all routes (mock parser as per Day 4)
router.use(auth);

// Validation middleware using existing custom validation.js
router.post('/', validation.validateProduct, productController.create);
router.put('/:id', validation.validateProduct, productController.update);

router.get('/', productController.getAll);
router.get('/:id', productController.getById);
router.delete('/:id', productController.remove);

module.exports = router;

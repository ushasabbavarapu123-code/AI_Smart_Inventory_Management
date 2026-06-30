// app/src/routes/supplier.routes.js

const express = require('express');
const router = express.Router();

const supplierController = require('../controllers/supplier.controller');
const auth = require('../../middleware/auth');
const { validateSupplier } = require('../../middleware/validation');

// Apply authentication middleware to all supplier routes
router.use(auth);

// Route definitions with validation middleware
router.get('/', supplierController.getAll);
router.get('/:id', supplierController.getById);
router.post('/', validateSupplier, supplierController.create);
router.put('/:id', validateSupplier, supplierController.update);
router.delete('/:id', supplierController.remove);

module.exports = router;

// app/src/routes/purchaseOrder.routes.js

const express = require('express');
const router = express.Router();
const poController = require('../controllers/purchaseOrder.controller');
const auth = require('../../middleware/auth');
const { validatePurchaseOrder, validatePOStatusUpdate } = require('../../middleware/validation');

// Secure all purchase order routes with JWT
router.use(auth);

router.get('/', poController.getAll);
router.get('/:id', poController.getById);
router.post('/', validatePurchaseOrder, poController.create);
router.patch('/:id', validatePOStatusUpdate, poController.updateStatus);

module.exports = router;

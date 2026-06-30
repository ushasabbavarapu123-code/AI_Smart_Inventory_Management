// app/src/routes/sales.routes.js

const express = require('express');
const router = express.Router();
const salesController = require('../controllers/sales.controller');
const auth = require('../../middleware/auth');
const { validateSale } = require('../../middleware/validation');

// Secure all sales routes with JWT
router.use(auth);

router.get('/', salesController.getAll);
router.post('/', validateSale, salesController.create);

module.exports = router;

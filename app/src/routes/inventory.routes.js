const express = require('express');
const router = express.Router();
const inventoryController = require('../controllers/inventory.controller');
const auth = require('../../middleware/auth');
const { validateInventoryUpdate } = require('../../middleware/validation');

// Apply authentication middleware to all inventory routes
router.use(auth);

// Route definitions with validation middleware
router.get('/', inventoryController.getAll);
router.get('/:id', inventoryController.getById);
router.post('/', validateInventoryUpdate, inventoryController.create);
router.put('/:id', validateInventoryUpdate, inventoryController.update);
router.delete('/:id', inventoryController.remove);

module.exports = router;

// app/src/routes/dashboard.routes.js

const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboard.controller');
const auth = require('../../middleware/auth');

// Secure dashboard routes with JWT
router.use(auth);

router.get('/summary', dashboardController.getSummary);

module.exports = router;

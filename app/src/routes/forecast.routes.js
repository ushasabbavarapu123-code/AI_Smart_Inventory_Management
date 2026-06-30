// app/src/routes/forecast.routes.js

const express = require('express');
const router = express.Router();
const forecastController = require('../controllers/forecast.controller');
const auth = require('../../middleware/auth');
const { validateForecastTrigger } = require('../../middleware/validation');

// Secure all forecast routes with JWT
router.use(auth);

router.get('/', forecastController.getAllForecasts);
router.get('/:product_id', forecastController.getForecast);
router.post('/', validateForecastTrigger, forecastController.triggerForecast);

module.exports = router;

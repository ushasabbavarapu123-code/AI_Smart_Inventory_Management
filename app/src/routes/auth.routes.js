// app/src/routes/auth.routes.js

const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');
const { validateLogin } = require('../../middleware/validation');

router.post('/login', validateLogin, authController.login);
router.post('/logout', authController.logout);

module.exports = router;

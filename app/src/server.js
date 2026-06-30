const express = require('express');
const cors = require('cors');
require('dotenv').config();
const { initDatabase } = require('./database');

// Import route modules (paths relative to app/src/server.js)
const productRoutes = require('./routes/product.routes');
const inventoryRoutes = require('./routes/inventory.routes');
const supplierRoutes = require('./routes/supplier.routes');
const errorHandler = require('../middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Basic health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Smart Inventory API is running' });
});

// Mount API routes
app.use('/api/products', productRoutes);
app.use('/api/inventory', inventoryRoutes);
app.use('/api/suppliers', supplierRoutes);

// Central error handling middleware
app.use(errorHandler);

// Initialize database and start server
async function startServer() {
  try {
    await initDatabase();
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to initialize database, shutting down server:', error);
    process.exit(1);
  }
}

startServer();

module.exports = app;


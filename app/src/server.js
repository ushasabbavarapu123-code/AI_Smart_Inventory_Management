const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();
const { initDatabase } = require('./database');

// Import route modules (paths relative to app/src/server.js)
const authRoutes = require('./routes/auth.routes');
const productRoutes = require('./routes/product.routes');
const inventoryRoutes = require('./routes/inventory.routes');
const supplierRoutes = require('./routes/supplier.routes');
const salesRoutes = require('./routes/sales.routes');
const purchaseOrderRoutes = require('./routes/purchaseOrder.routes');
const forecastRoutes = require('./routes/forecast.routes');
const dashboardRoutes = require('./routes/dashboard.routes');
const errorHandler = require('../middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Serve static files from public folder
app.use(express.static(path.join(__dirname, '../public')));
app.use('/docs', express.static(path.join(__dirname, '../../docs')));

// Basic health check endpoint (public)
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Smart Inventory API is running' });
});

// Public authentication routes (no JWT required)
app.use('/api/auth', authRoutes);

// Protected API routes (JWT required - enforced inside each router)
app.use('/api/products', productRoutes);
app.use('/api/inventory', inventoryRoutes);
app.use('/api/suppliers', supplierRoutes);
app.use('/api/sales', salesRoutes);
app.use('/api/purchase-orders', purchaseOrderRoutes);
app.use('/api/forecasts', forecastRoutes);
app.use('/api/dashboard', dashboardRoutes);

// Central error handling middleware (must be last)
app.use(errorHandler);

// Initialize database and start server
async function startServer() {
  try {
    await initDatabase();
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
      console.log(`Health check: http://localhost:${PORT}/api/health`);
    });
  } catch (error) {
    console.error('Failed to initialize database, shutting down server:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  startServer();
} else {
  // For testing, make sure DB is initialized
  initDatabase().catch(err => {
    console.error('Failed to initialize DB in test mode:', err);
  });
}

module.exports = app;

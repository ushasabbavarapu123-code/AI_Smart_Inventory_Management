const express = require('express');
const cors = require('cors');
require('dotenv').config();
const { initDatabase } = require('./database');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Basic health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Smart Inventory API is running' });
});

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


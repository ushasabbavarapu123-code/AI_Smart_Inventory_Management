// app/src/models/forecast.model.js

const { getDatabase } = require('../database');
const crypto = require('crypto');
const uuidv4 = () => crypto.randomUUID();

async function saveForecast(forecastData) {
  const db = getDatabase();
  const { product_id, forecast_date, predicted_qty, confidence_low, confidence_high, model_used, horizon_days } = forecastData;
  const forecast_id = uuidv4();
  const generated_at = new Date().toISOString();

  // Delete old forecast for same product+date to avoid duplicates
  await new Promise((resolve, reject) => {
    db.run(`DELETE FROM forecasts WHERE product_id = ?`, [product_id], (err) => {
      if (err) reject(err);
      else resolve();
    });
  });

  const sql = `INSERT INTO forecasts (forecast_id, product_id, forecast_date, predicted_qty, confidence_low, confidence_high, model_used, generated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
  return new Promise((resolve, reject) => {
    db.run(sql, [forecast_id, product_id, forecast_date, predicted_qty, confidence_low, confidence_high, model_used, generated_at], function (err) {
      if (err) reject(err);
      else resolve({ forecast_id, product_id, forecast_date, predicted_qty, confidence_low, confidence_high, model_used, generated_at });
    });
  });
}

async function getLatestForecast(product_id) {
  const db = getDatabase();
  const sql = `SELECT f.*, p.name as product_name, p.sku FROM forecasts f
               JOIN products p ON f.product_id = p.product_id
               WHERE f.product_id = ?
               ORDER BY f.generated_at DESC LIMIT 1`;
  return new Promise((resolve, reject) => {
    db.get(sql, [product_id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

async function getAllForecasts() {
  const db = getDatabase();
  const sql = `SELECT f.*, p.name as product_name, p.sku FROM forecasts f
               JOIN products p ON f.product_id = p.product_id
               ORDER BY f.generated_at DESC`;
  return new Promise((resolve, reject) => {
    db.all(sql, [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

module.exports = {
  saveForecast,
  getLatestForecast,
  getAllForecasts
};

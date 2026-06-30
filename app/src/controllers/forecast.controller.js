// app/src/controllers/forecast.controller.js

const { spawn } = require('child_process');
const path = require('path');
const forecastModel = require('../models/forecast.model');

const PYTHON_PATH = path.resolve(__dirname, '../../../analytics/venv/Scripts/python.exe');
const FORECAST_SCRIPT = path.resolve(__dirname, '../../../analytics/scripts/forecast.py');

async function triggerForecast(req, res, next) {
  try {
    const { product_id, horizon_days = 30 } = req.body;

    // Run Python forecasting script as a child process
    const result = await new Promise((resolve, reject) => {
      const args = ['--product_id', product_id, '--horizon_days', String(horizon_days)];
      const process = spawn(PYTHON_PATH, [FORECAST_SCRIPT, ...args]);

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => { stdout += data.toString(); });
      process.stderr.on('data', (data) => { stderr += data.toString(); });

      process.on('close', (code) => {
        if (code !== 0) {
          return reject(new Error(`Forecast script failed: ${stderr || stdout}`));
        }
        try {
          const parsed = JSON.parse(stdout.trim());
          resolve(parsed);
        } catch (e) {
          reject(new Error(`Failed to parse forecast output: ${stdout}`));
        }
      });

      process.on('error', (err) => {
        reject(new Error(`Failed to start forecast process: ${err.message}`));
      });
    });

    // Save forecast to database
    const saved = await forecastModel.saveForecast({
      product_id,
      forecast_date: result.forecast_date,
      predicted_qty: result.predicted_qty,
      confidence_low: result.confidence_low,
      confidence_high: result.confidence_high,
      model_used: result.model_used,
      horizon_days
    });

    res.json({ success: true, data: saved, message: 'Forecast generated successfully' });
  } catch (err) {
    next(err);
  }
}

async function getForecast(req, res, next) {
  try {
    const forecast = await forecastModel.getLatestForecast(req.params.product_id);
    if (!forecast) {
      return res.status(404).json({ success: false, error: 'No forecast found for this product', statusCode: 404 });
    }
    res.json({ success: true, data: forecast });
  } catch (err) {
    next(err);
  }
}

async function getAllForecasts(req, res, next) {
  try {
    const forecasts = await forecastModel.getAllForecasts();
    res.json({ success: true, data: forecasts });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  triggerForecast,
  getForecast,
  getAllForecasts
};

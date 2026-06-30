#!/usr/bin/env python3
"""
forecast.py - Demand Forecasting Script
AI Smart Inventory Management & Demand Forecasting System
Day 5 - Analytics Pipeline Entry Point

Usage:
    python forecast.py --product_id <uuid> --horizon_days <int>

Output:
    JSON string written to stdout with forecast result.
"""

import sys
import os
import json
import argparse
import sqlite3
from datetime import datetime, timedelta

def get_db_path():
    """Resolve the database path from project structure."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(script_dir))  # Up 2 levels to project root

    env_path = os.path.join(project_dir, 'app', '.env')
    db_path = None

    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('DB_PATH='):
                        val = line.strip().split('=', 1)[1]
                        db_path = os.path.abspath(os.path.join(project_dir, 'app', val))
                        break
        except Exception:
            pass

    if not db_path:
        db_path = os.path.abspath(os.path.join(project_dir, 'data', 'inventory.db'))

    return db_path


def get_sales_history(conn, product_id, days_back=365):
    """Fetch recent sales history for a product."""
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sale_date, SUM(quantity) as qty
        FROM sales
        WHERE product_id = ? AND sale_date >= ?
        GROUP BY sale_date
        ORDER BY sale_date ASC
    """, (product_id, from_date))
    rows = cursor.fetchall()
    return rows


def moving_average_forecast(sales_rows, horizon_days):
    """
    Simple moving average with trend adjustment as the default forecast method.
    Uses last 30 days average as baseline, applies 7-day trend factor.
    Falls back to global average if insufficient data.
    """
    if not sales_rows:
        return {
            'predicted_qty': 10,
            'confidence_low': 5,
            'confidence_high': 20,
            'model_used': 'MovingAverage_Fallback'
        }

    quantities = [row[1] for row in sales_rows]

    # Use last 30 data points (or all if fewer)
    window = min(30, len(quantities))
    recent = quantities[-window:]
    avg = sum(recent) / len(recent)

    # Simple trend: compare last 7 points vs prior 7 points
    if len(quantities) >= 14:
        last7 = sum(quantities[-7:]) / 7
        prev7 = sum(quantities[-14:-7]) / 7
        trend_factor = (last7 - prev7) / max(prev7, 1)
    else:
        trend_factor = 0.0

    # Scale avg by horizon (default is 30-day prediction, scale proportionally)
    scale = horizon_days / 30.0
    predicted = max(1, round((avg * scale) * (1 + trend_factor)))
    confidence_range = max(2, round(predicted * 0.2))

    return {
        'predicted_qty': predicted,
        'confidence_low': max(0, predicted - confidence_range),
        'confidence_high': predicted + confidence_range,
        'model_used': 'MovingAverage_Trend'
    }


def arima_forecast(sales_rows, horizon_days):
    """
    ARIMA-based forecasting using statsmodels.
    Falls back to moving average if ARIMA fails or data insufficient.
    """
    try:
        import pandas as pd
        import numpy as np
        from statsmodels.tsa.arima.model import ARIMA
        import warnings
        warnings.filterwarnings('ignore')

        if len(sales_rows) < 14:
            return None  # Not enough data for ARIMA

        dates = [row[0] for row in sales_rows]
        quantities = [row[1] for row in sales_rows]

        # Create time series with daily frequency, filling gaps with 0
        df = pd.DataFrame({'date': pd.to_datetime(dates), 'qty': quantities})
        df.set_index('date', inplace=True)
        df = df.resample('D').sum().fillna(0)

        if len(df) < 14:
            return None

        # Fit ARIMA(2,1,2) model
        model = ARIMA(df['qty'], order=(2, 1, 2))
        fit = model.fit()

        # Forecast
        forecast_result = fit.forecast(steps=horizon_days)
        predicted_sum = max(1, int(forecast_result.sum()))
        conf_int = fit.get_forecast(steps=horizon_days).conf_int()
        low_sum = max(0, int(conf_int.iloc[:, 0].sum()))
        high_sum = max(predicted_sum, int(conf_int.iloc[:, 1].sum()))

        return {
            'predicted_qty': predicted_sum,
            'confidence_low': low_sum,
            'confidence_high': high_sum,
            'model_used': 'ARIMA'
        }
    except Exception as e:
        return None  # Will fall back to moving average


def main():
    parser = argparse.ArgumentParser(description='Demand Forecasting Script')
    parser.add_argument('--product_id', required=True, help='Product UUID to forecast')
    parser.add_argument('--horizon_days', type=int, default=30, help='Forecast horizon in days')
    args = parser.parse_args()

    product_id = args.product_id
    horizon_days = args.horizon_days

    db_path = get_db_path()

    if not os.path.exists(db_path):
        result = {
            'error': f'Database not found: {db_path}',
            'product_id': product_id,
            'forecast_date': (datetime.now() + timedelta(days=horizon_days)).strftime('%Y-%m-%d'),
            'predicted_qty': 0,
            'confidence_low': 0,
            'confidence_high': 0,
            'model_used': 'None'
        }
        print(json.dumps(result))
        sys.exit(1)

    conn = sqlite3.connect(db_path)

    try:
        # Validate product exists
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, name FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            result = {
                'error': f'Product not found: {product_id}',
                'product_id': product_id,
                'forecast_date': (datetime.now() + timedelta(days=horizon_days)).strftime('%Y-%m-%d'),
                'predicted_qty': 0,
                'confidence_low': 0,
                'confidence_high': 0,
                'model_used': 'None'
            }
            print(json.dumps(result))
            sys.exit(1)

        # Fetch historical sales
        sales_rows = get_sales_history(conn, product_id, days_back=365)

        # Try ARIMA first, fall back to moving average
        forecast_result = arima_forecast(sales_rows, horizon_days)
        if forecast_result is None:
            forecast_result = moving_average_forecast(sales_rows, horizon_days)

        # Build final forecast date
        forecast_date = (datetime.now() + timedelta(days=horizon_days)).strftime('%Y-%m-%d')
        generated_at = datetime.now().isoformat()

        output = {
            'product_id': product_id,
            'forecast_date': forecast_date,
            'predicted_qty': forecast_result['predicted_qty'],
            'confidence_low': forecast_result['confidence_low'],
            'confidence_high': forecast_result['confidence_high'],
            'model_used': forecast_result['model_used'],
            'generated_at': generated_at
        }

        print(json.dumps(output))

    except Exception as e:
        result = {
            'error': str(e),
            'product_id': product_id,
            'forecast_date': (datetime.now() + timedelta(days=horizon_days)).strftime('%Y-%m-%d'),
            'predicted_qty': 0,
            'confidence_low': 0,
            'confidence_high': 0,
            'model_used': 'Error'
        }
        print(json.dumps(result))
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()

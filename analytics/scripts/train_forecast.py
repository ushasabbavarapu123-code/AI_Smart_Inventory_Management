#!/usr/bin/env python3
"""
train_forecast.py — Demand Forecasting Training & Prediction Pipeline
======================================================================
AI Smart Inventory Management & Demand Forecasting System
Day 9 — Phase 5: Model Building & Forecasting

This script:
  1. Loads processed sales + products data
  2. Engineers lag / rolling / calendar features per SKU
  3. Performs temporal train/validation split (last 60 days = validation)
  4. Trains a Baseline model (30-day Simple Moving Average)
  5. Trains a Champion model (Random Forest Regressor)
  6. Evaluates both with MAE & RMSE, selects the champion
  7. Generates 30-day future demand forecasts for every SKU
  8. Computes safety stock & recommended reorder points
  9. Persists forecasts to SQLite `forecasts` table
  10. Exports forecasts to data/processed/forecasts_processed.csv

Usage:
    python train_forecast.py
"""

import os
import sys
import uuid
import json
import sqlite3
import warnings
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ---------------------------------------------------------------------------
# Suppress non-critical warnings
# ---------------------------------------------------------------------------
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inventory.db")

# Also check app/.env for DB_PATH override
_env_file = os.path.join(PROJECT_ROOT, "app", ".env")
if os.path.exists(_env_file):
    with open(_env_file, "r") as _f:
        for _line in _f:
            if _line.startswith("DB_PATH="):
                _val = _line.strip().split("=", 1)[1]
                DB_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, "app", _val))
                break

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
VALIDATION_DAYS = 60          # last N days held out for validation
FORECAST_HORIZON = 30         # days to forecast into the future
SMA_WINDOW = 30               # Simple Moving Average window
Z_SCORE = 1.645               # 95% service-level Z value for safety stock
RF_N_ESTIMATORS = 200         # Random Forest number of trees
RF_MAX_DEPTH = 12             # Random Forest max tree depth
RF_RANDOM_STATE = 42          # Reproducibility seed

LAG_FEATURES = [1, 7, 14, 30]                     # lag days
ROLLING_WINDOWS = [7, 14, 30]                      # rolling-avg windows

FEATURE_COLS = (
    [f"lag_{d}" for d in LAG_FEATURES]
    + [f"rolling_mean_{w}" for w in ROLLING_WINDOWS]
    + [f"rolling_std_{w}" for w in ROLLING_WINDOWS]
    + ["day_of_week", "month", "quarter", "is_weekend"]
)


# =========================================================================
# 1. DATA LOADING
# =========================================================================
def load_data():
    """Load processed sales and products CSVs."""
    sales_path = os.path.join(DATA_PROCESSED, "sales_processed.csv")
    products_path = os.path.join(DATA_PROCESSED, "products_processed.csv")

    sales = pd.read_csv(sales_path, parse_dates=["sale_date"])
    products = pd.read_csv(products_path)

    print(f"[INFO] Loaded sales:    {sales.shape[0]:,} rows × {sales.shape[1]} cols")
    print(f"[INFO] Loaded products: {products.shape[0]:,} rows × {products.shape[1]} cols")

    return sales, products


# =========================================================================
# 2. FEATURE ENGINEERING (per SKU daily time series)
# =========================================================================
def build_daily_series(sales: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sales to daily demand per product_id, then fill calendar
    gaps with 0-demand days so that every product has a contiguous series.
    """
    daily = (
        sales
        .groupby(["product_id", "sale_date"])
        .agg(daily_qty=("quantity", "sum"))
        .reset_index()
    )

    # Create a contiguous date range per product
    date_min = daily["sale_date"].min()
    date_max = daily["sale_date"].max()
    all_dates = pd.date_range(date_min, date_max, freq="D")

    product_ids = daily["product_id"].unique()
    idx = pd.MultiIndex.from_product([product_ids, all_dates],
                                      names=["product_id", "sale_date"])
    full = pd.DataFrame(index=idx).reset_index()
    full = full.merge(daily, on=["product_id", "sale_date"], how="left")
    full["daily_qty"] = full["daily_qty"].fillna(0).astype(float)

    return full


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag, rolling, and calendar features to a daily time series."""
    df = df.sort_values(["product_id", "sale_date"]).copy()

    # --- lag features ---
    for lag in LAG_FEATURES:
        df[f"lag_{lag}"] = df.groupby("product_id")["daily_qty"].shift(lag)

    # --- rolling statistics ---
    for window in ROLLING_WINDOWS:
        rolling = df.groupby("product_id")["daily_qty"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).mean()
        )
        df[f"rolling_mean_{window}"] = rolling

        rolling_std = df.groupby("product_id")["daily_qty"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).std()
        )
        df[f"rolling_std_{window}"] = rolling_std.fillna(0)

    # --- calendar features ---
    df["day_of_week"] = df["sale_date"].dt.dayofweek
    df["month"] = df["sale_date"].dt.month
    df["quarter"] = df["sale_date"].dt.quarter
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    return df


# =========================================================================
# 3. TRAIN / VALIDATION SPLIT (temporal)
# =========================================================================
def temporal_split(df: pd.DataFrame, val_days: int = VALIDATION_DAYS):
    """
    Split into train / validation sets using a calendar-based cutoff.
    Last `val_days` days become the validation set.
    """
    cutoff = df["sale_date"].max() - pd.Timedelta(days=val_days)

    # Drop rows where any lag feature is NaN (only affects earliest days)
    required = [c for c in FEATURE_COLS if c in df.columns]
    ready = df.dropna(subset=required)

    train = ready[ready["sale_date"] <= cutoff].copy()
    val = ready[ready["sale_date"] > cutoff].copy()

    print(f"[INFO] Temporal split — cutoff {cutoff.date()}")
    print(f"       Train: {train.shape[0]:,} rows   |   Validation: {val.shape[0]:,} rows")

    return train, val


# =========================================================================
# 4. BASELINE MODEL — Simple Moving Average
# =========================================================================
def sma_predict(train: pd.DataFrame, val: pd.DataFrame, window: int = SMA_WINDOW):
    """
    For each (product_id, date) in validation, predict daily demand as
    the trailing `window`-day average from training data.
    """
    # Build per-product SMA from the last `window` training days
    latest_train = train.sort_values("sale_date").groupby("product_id").tail(window)
    sma = latest_train.groupby("product_id")["daily_qty"].mean().rename("sma_pred")

    preds = val[["product_id", "sale_date", "daily_qty"]].copy()
    preds = preds.merge(sma, on="product_id", how="left")
    preds["sma_pred"] = preds["sma_pred"].fillna(0)

    return preds


# =========================================================================
# 5. CHAMPION MODEL — Random Forest Regressor
# =========================================================================
def train_random_forest(train: pd.DataFrame, val: pd.DataFrame):
    """Train RF on training data, predict on validation set."""
    X_train = train[FEATURE_COLS].values
    y_train = train["daily_qty"].values
    X_val = val[FEATURE_COLS].values

    rf = RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        random_state=RF_RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_val)
    y_pred = np.clip(y_pred, 0, None)  # demand ≥ 0

    return rf, y_pred


# =========================================================================
# 6. EVALUATION
# =========================================================================
def evaluate(y_true, y_pred, model_name: str):
    """Compute MAE and RMSE, print results."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"[EVAL] {model_name:30s}  MAE = {mae:.4f}   RMSE = {rmse:.4f}")
    return {"model": model_name, "MAE": round(mae, 4), "RMSE": round(rmse, 4)}


# =========================================================================
# 7. FUTURE FORECAST (30 days per SKU)
# =========================================================================
def forecast_future(rf_model, daily_df: pd.DataFrame, products: pd.DataFrame,
                     horizon: int = FORECAST_HORIZON):
    """
    Generate `horizon`-day ahead forecasts for every SKU using the
    trained Random Forest model.  Uses recursive multi-step approach:
    predict day t+1, feed prediction back as a feature for day t+2, etc.
    """
    product_ids = daily_df["product_id"].unique()
    last_date = daily_df["sale_date"].max()
    forecast_rows = []

    for pid in product_ids:
        prod_data = daily_df[daily_df["product_id"] == pid].sort_values("sale_date").copy()
        history = prod_data["daily_qty"].values.tolist()

        # We will need the last 30 values (worst case for lag_30)
        recent = history[-max(LAG_FEATURES + ROLLING_WINDOWS):]

        for step in range(1, horizon + 1):
            fdate = last_date + pd.Timedelta(days=step)

            # Build features from accumulated `recent`
            features = {}
            for lag in LAG_FEATURES:
                features[f"lag_{lag}"] = recent[-lag] if len(recent) >= lag else 0
            for w in ROLLING_WINDOWS:
                window_vals = recent[-w:] if len(recent) >= w else recent
                features[f"rolling_mean_{w}"] = np.mean(window_vals) if window_vals else 0
                features[f"rolling_std_{w}"] = np.std(window_vals) if len(window_vals) > 1 else 0

            features["day_of_week"] = fdate.dayofweek
            features["month"] = fdate.month
            features["quarter"] = fdate.quarter
            features["is_weekend"] = int(fdate.dayofweek >= 5)

            X_row = np.array([[features[c] for c in FEATURE_COLS]])
            pred = max(0, rf_model.predict(X_row)[0])
            recent.append(pred)

            forecast_rows.append({
                "product_id": pid,
                "forecast_date": fdate.strftime("%Y-%m-%d"),
                "predicted_daily_qty": round(pred, 4),
            })

    forecasts_df = pd.DataFrame(forecast_rows)

    # Aggregate daily forecasts into a 30-day total per SKU
    agg = (
        forecasts_df
        .groupby("product_id")
        .agg(
            predicted_qty=("predicted_daily_qty", "sum"),
            avg_daily_forecast=("predicted_daily_qty", "mean"),
            std_daily_forecast=("predicted_daily_qty", "std"),
        )
        .reset_index()
    )
    agg["predicted_qty"] = agg["predicted_qty"].round(0).astype(int)
    agg["avg_daily_forecast"] = agg["avg_daily_forecast"].round(4)
    agg["std_daily_forecast"] = agg["std_daily_forecast"].fillna(0).round(4)

    # Merge product info
    prod_cols = ["product_id", "sku", "name", "category", "lead_time_days",
                 "current_stock_quantity", "reorder_point"]
    available = [c for c in prod_cols if c in products.columns]
    agg = agg.merge(products[available], on="product_id", how="left")

    return agg, forecasts_df


# =========================================================================
# 8. SAFETY STOCK & REORDER POINTS
# =========================================================================
def compute_safety_and_reorder(agg: pd.DataFrame, z: float = Z_SCORE):
    """
    safety_stock  = Z × σ_daily × √lead_time
    reorder_point = avg_daily_demand × lead_time + safety_stock
    """
    lead = agg["lead_time_days"].fillna(7).astype(float)
    sigma = agg["std_daily_forecast"].fillna(0).astype(float)
    avg_demand = agg["avg_daily_forecast"].fillna(0).astype(float)

    agg["safety_stock"] = (z * sigma * np.sqrt(lead)).round(0).astype(int)
    agg["rec_reorder_point"] = (avg_demand * lead + agg["safety_stock"]).round(0).astype(int)
    agg["rec_reorder_qty"] = (avg_demand * lead * 2 + agg["safety_stock"]).round(0).astype(int)

    return agg


# =========================================================================
# 9. DATABASE PERSISTENCE
# =========================================================================
def save_to_database(agg: pd.DataFrame, db_path: str = DB_PATH):
    """Insert forecast rows into the SQLite `forecasts` table."""
    if not os.path.exists(db_path):
        print(f"[WARN] Database not found at {db_path}. Skipping DB write.")
        return 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear old forecasts
    cursor.execute("DELETE FROM forecasts")

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    forecast_date = (datetime.now(timezone.utc) + timedelta(days=FORECAST_HORIZON)).strftime("%Y-%m-%d")

    inserted = 0
    for _, row in agg.iterrows():
        forecast_id = str(uuid.uuid4())
        predicted = int(row["predicted_qty"])
        std_val = float(row.get("std_daily_forecast", 0))
        conf_range = max(1, int(std_val * FORECAST_HORIZON * 0.5))
        conf_low = max(0, predicted - conf_range)
        conf_high = predicted + conf_range

        cursor.execute("""
            INSERT INTO forecasts
                (forecast_id, product_id, forecast_date, predicted_qty,
                 confidence_low, confidence_high, model_used, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            forecast_id,
            row["product_id"],
            forecast_date,
            predicted,
            conf_low,
            conf_high,
            "RandomForest",
            generated_at,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Inserted {inserted} forecast records into SQLite.")
    return inserted


# =========================================================================
# 10. CSV EXPORT
# =========================================================================
def export_csv(agg: pd.DataFrame, daily_forecasts: pd.DataFrame):
    """Export forecasts to data/processed/forecasts_processed.csv."""
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    forecast_date = (datetime.now(timezone.utc) + timedelta(days=FORECAST_HORIZON)).strftime("%Y-%m-%d")

    export = agg.copy()
    export["forecast_id"] = [str(uuid.uuid4()) for _ in range(len(export))]
    export["forecast_date"] = forecast_date
    export["model_used"] = "RandomForest"
    export["generated_at"] = generated_at

    # Confidence interval
    export["confidence_low"] = (
        export["predicted_qty"] - (export["std_daily_forecast"] * FORECAST_HORIZON * 0.5).clip(lower=1)
    ).clip(lower=0).astype(int)
    export["confidence_high"] = (
        export["predicted_qty"] + (export["std_daily_forecast"] * FORECAST_HORIZON * 0.5).clip(lower=1)
    ).astype(int)

    # Select and order columns for CSV
    col_order = [
        "forecast_id", "product_id", "sku", "name", "category",
        "forecast_date", "predicted_qty", "confidence_low", "confidence_high",
        "avg_daily_forecast", "std_daily_forecast",
        "safety_stock", "rec_reorder_point", "rec_reorder_qty",
        "current_stock_quantity", "lead_time_days",
        "model_used", "generated_at",
    ]
    out_cols = [c for c in col_order if c in export.columns]
    export = export[out_cols]

    out_path = os.path.join(DATA_PROCESSED, "forecasts_processed.csv")
    export.to_csv(out_path, index=False)
    print(f"[INFO] Exported {len(export)} rows to {out_path}")

    # Also save daily granularity forecast (for notebooks / dashboards)
    daily_path = os.path.join(DATA_PROCESSED, "daily_forecasts.csv")
    daily_forecasts.to_csv(daily_path, index=False)
    print(f"[INFO] Exported {len(daily_forecasts)} daily rows to {daily_path}")

    return out_path


# =========================================================================
# 11. MAIN PIPELINE
# =========================================================================
def main():
    print("=" * 72)
    print("  AI Smart Inventory — Demand Forecasting Pipeline")
    print("  Day 9 · Phase 5 · Model Building & Forecasting")
    print("=" * 72)
    print()

    # --- Step 1: Load data ---
    print("[STEP 1] Loading processed data …")
    sales, products = load_data()
    print()

    # --- Step 2: Build daily time series ---
    print("[STEP 2] Building daily demand time series …")
    daily = build_daily_series(sales)
    n_products = daily["product_id"].nunique()
    n_days = (daily["sale_date"].max() - daily["sale_date"].min()).days + 1
    print(f"[INFO] {n_products} products × {n_days} days = {daily.shape[0]:,} rows")
    print()

    # --- Step 3: Feature engineering ---
    print("[STEP 3] Engineering lag / rolling / calendar features …")
    daily = engineer_features(daily)
    print(f"[INFO] Feature columns: {len(FEATURE_COLS)}")
    print(f"       {FEATURE_COLS}")
    print()

    # --- Step 4: Train / Validation split ---
    print("[STEP 4] Temporal train/validation split …")
    train, val = temporal_split(daily)
    print()

    # --- Step 5: Baseline Model (SMA) ---
    print("[STEP 5] Training Baseline Model (Simple Moving Average) …")
    sma_preds = sma_predict(train, val)
    sma_metrics = evaluate(sma_preds["daily_qty"], sma_preds["sma_pred"],
                           "Baseline (SMA-30)")
    print()

    # --- Step 6: Random Forest Model ---
    print("[STEP 6] Training Champion Model (Random Forest) …")
    rf_model, rf_preds = train_random_forest(train, val)
    rf_metrics = evaluate(val["daily_qty"].values, rf_preds,
                          "Random Forest Regressor")
    print()

    # --- Step 7: Champion selection ---
    print("[STEP 7] Model Comparison & Champion Selection …")
    comparison = pd.DataFrame([sma_metrics, rf_metrics])
    print(comparison.to_string(index=False))
    print()

    champion = "Random Forest" if rf_metrics["RMSE"] <= sma_metrics["RMSE"] else "SMA"
    print(f"[RESULT] ** Champion Model: {champion} **")
    if champion == "Random Forest":
        # Feature importances
        importances = pd.Series(
            rf_model.feature_importances_, index=FEATURE_COLS
        ).sort_values(ascending=False)
        print("\n[INFO] Top 5 Feature Importances:")
        for feat, imp in importances.head(5).items():
            print(f"       {feat:25s}  {imp:.4f}")
    print()

    # --- Step 8: Generate 30-day forecasts ---
    print(f"[STEP 8] Generating {FORECAST_HORIZON}-day future forecasts for {n_products} SKUs …")
    agg, daily_forecasts = forecast_future(rf_model, daily, products, FORECAST_HORIZON)
    print(f"[INFO] Total predicted demand (all SKUs): {agg['predicted_qty'].sum():,} units")
    print()

    # --- Step 9: Safety stock & reorder points ---
    print("[STEP 9] Computing safety stock & reorder points (Z=1.645, 95% SL) …")
    agg = compute_safety_and_reorder(agg)
    print(f"[INFO] Average safety stock: {agg['safety_stock'].mean():.1f} units")
    print(f"[INFO] Average reorder point: {agg['rec_reorder_point'].mean():.1f} units")
    print()

    # --- Step 10: Save to database ---
    print("[STEP 10] Persisting forecasts to SQLite …")
    save_to_database(agg)
    print()

    # --- Step 11: Export CSV ---
    print("[STEP 11] Exporting forecasts to CSV …")
    export_csv(agg, daily_forecasts)
    print()

    # --- Summary ---
    print("=" * 72)
    print("  PIPELINE COMPLETE — Summary")
    print("=" * 72)
    print(f"  Products forecasted :  {n_products}")
    print(f"  Forecast horizon    :  {FORECAST_HORIZON} days")
    print(f"  Champion model      :  {champion}")
    print(f"  Baseline MAE / RMSE :  {sma_metrics['MAE']} / {sma_metrics['RMSE']}")
    print(f"  Champion MAE / RMSE :  {rf_metrics['MAE']} / {rf_metrics['RMSE']}")
    print(f"  Total predicted qty :  {agg['predicted_qty'].sum():,} units")
    print(f"  DB records inserted :  {n_products}")
    print(f"  CSV exported        :  forecasts_processed.csv")
    print("=" * 72)

    # Return metrics for programmatic use
    return {
        "n_products": n_products,
        "champion": champion,
        "sma_metrics": sma_metrics,
        "rf_metrics": rf_metrics,
        "total_predicted": int(agg["predicted_qty"].sum()),
        "comparison_df": comparison,
        "forecast_agg": agg,
    }


if __name__ == "__main__":
    main()

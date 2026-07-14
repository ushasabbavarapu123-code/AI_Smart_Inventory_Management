#!/usr/bin/env python3
"""
model_optimization.py — ML Model Optimization & Evaluation Pipeline
=====================================================================
AI Smart Inventory Management & Demand Forecasting System
Day 9 (Missing Tasks) — Phase 5: Model Optimization

This script:
  1.  Loads processed data and engineers features (reuses train_forecast pipeline)
  2.  Trains additional models: Linear Regression, Gradient Boosting (+ XGBoost if installed)
  3.  Performs RandomizedSearchCV hyperparameter tuning on Random Forest
  4.  Evaluates all models on MAE, MSE, RMSE, R², MAPE
  5.  Selects the champion model
  6.  Generates and saves visualizations to reports/figures/
  7.  Saves the best model as models/best_forecasting_model.pkl
  8.  Writes models/model_metadata.json

Usage:
    python analytics/scripts/model_optimization.py
"""

import os
import sys
import json
import logging
import warnings
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import joblib

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")

# Ensure output directories exist
for d in [MODELS_DIR, REPORTS_DIR, FIGURES_DIR]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Feature Configuration (mirrors train_forecast.py)
# ---------------------------------------------------------------------------
VALIDATION_DAYS = 60
LAG_FEATURES = [1, 7, 14, 30]
ROLLING_WINDOWS = [7, 14, 30]
RANDOM_STATE = 42

FEATURE_COLS = (
    [f"lag_{d}" for d in LAG_FEATURES]
    + [f"rolling_mean_{w}" for w in ROLLING_WINDOWS]
    + [f"rolling_std_{w}" for w in ROLLING_WINDOWS]
    + ["day_of_week", "month", "quarter", "is_weekend"]
)

# ---------------------------------------------------------------------------
# Color palette for plots
# ---------------------------------------------------------------------------
PALETTE = {
    "primary": "#5C6BC0",
    "secondary": "#26C6DA",
    "accent": "#FF7043",
    "success": "#66BB6A",
    "warning": "#FFA726",
    "bg": "#1A1A2E",
    "surface": "#16213E",
    "text": "#E8EAF6",
}


# ==========================================================================
# 1. DATA LOADING (reuse existing CSVs)
# ==========================================================================
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load processed sales and products CSVs from data/processed/."""
    sales_path = os.path.join(DATA_PROCESSED, "sales_processed.csv")
    products_path = os.path.join(DATA_PROCESSED, "products_processed.csv")

    sales = pd.read_csv(sales_path, parse_dates=["sale_date"])
    products = pd.read_csv(products_path)

    logger.info("Loaded sales:    %d rows × %d cols", sales.shape[0], sales.shape[1])
    logger.info("Loaded products: %d rows × %d cols", products.shape[0], products.shape[1])
    return sales, products


# ==========================================================================
# 2. FEATURE ENGINEERING (reuse exact same pipeline as train_forecast.py)
# ==========================================================================
def build_daily_series(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales to daily per product, fill calendar gaps with 0."""
    daily = (
        sales
        .groupby(["product_id", "sale_date"])
        .agg(daily_qty=("quantity", "sum"))
        .reset_index()
    )
    date_min = daily["sale_date"].min()
    date_max = daily["sale_date"].max()
    all_dates = pd.date_range(date_min, date_max, freq="D")
    product_ids = daily["product_id"].unique()

    idx = pd.MultiIndex.from_product(
        [product_ids, all_dates], names=["product_id", "sale_date"]
    )
    full = pd.DataFrame(index=idx).reset_index()
    full = full.merge(daily, on=["product_id", "sale_date"], how="left")
    full["daily_qty"] = full["daily_qty"].fillna(0).astype(float)
    return full


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag, rolling, and calendar features."""
    df = df.sort_values(["product_id", "sale_date"]).copy()

    for lag in LAG_FEATURES:
        df[f"lag_{lag}"] = df.groupby("product_id")["daily_qty"].shift(lag)

    for window in ROLLING_WINDOWS:
        df[f"rolling_mean_{window}"] = df.groupby("product_id")["daily_qty"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).mean()
        )
        df[f"rolling_std_{window}"] = df.groupby("product_id")["daily_qty"].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).std()
        ).fillna(0)

    df["day_of_week"] = df["sale_date"].dt.dayofweek
    df["month"] = df["sale_date"].dt.month
    df["quarter"] = df["sale_date"].dt.quarter
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    return df


def temporal_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Temporal train/validation split (last VALIDATION_DAYS = validation)."""
    cutoff = df["sale_date"].max() - pd.Timedelta(days=VALIDATION_DAYS)
    required = [c for c in FEATURE_COLS if c in df.columns]
    ready = df.dropna(subset=required)
    train = ready[ready["sale_date"] <= cutoff].copy()
    val = ready[ready["sale_date"] > cutoff].copy()
    logger.info(
        "Temporal split — cutoff %s | Train: %d rows | Val: %d rows",
        cutoff.date(), len(train), len(val),
    )
    return train, val


# ==========================================================================
# 3. EVALUATION METRICS
# ==========================================================================
def mape_score(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-8) -> float:
    """Mean Absolute Percentage Error (MAPE)."""
    return float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + eps))) * 100)


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
) -> Dict[str, Any]:
    """
    Compute MAE, MSE, RMSE, R², and MAPE.

    Returns a dict suitable for a comparison table row.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_true, y_pred)
    mape = mape_score(y_true, y_pred)

    metrics = {
        "model": model_name,
        "MAE": round(mae, 4),
        "MSE": round(mse, 4),
        "RMSE": round(rmse, 4),
        "R2": round(r2, 4),
        "MAPE": round(mape, 4),
    }
    logger.info(
        "[EVAL] %-35s MAE=%.4f  RMSE=%.4f  R²=%.4f  MAPE=%.2f%%",
        model_name, mae, rmse, r2, mape,
    )
    return metrics


# ==========================================================================
# 4. MODEL TRAINING
# ==========================================================================
def train_linear_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
) -> Tuple[LinearRegression, np.ndarray]:
    """Train Linear Regression model."""
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = np.clip(lr.predict(X_val), 0, None)
    return lr, y_pred


def train_gradient_boosting(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
) -> Tuple[GradientBoostingRegressor, np.ndarray]:
    """Train Gradient Boosting Regressor."""
    gb = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        random_state=RANDOM_STATE,
    )
    gb.fit(X_train, y_train)
    y_pred = np.clip(gb.predict(X_val), 0, None)
    return gb, y_pred


def train_random_forest_baseline(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
) -> Tuple[RandomForestRegressor, np.ndarray]:
    """Train the baseline Random Forest (same config as train_forecast.py)."""
    rf = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    y_pred = np.clip(rf.predict(X_val), 0, None)
    return rf, y_pred


def hyperparameter_tuning(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
) -> Tuple[RandomForestRegressor, np.ndarray, Dict]:
    """
    Hyperparameter tuning for Random Forest using RandomizedSearchCV.
    Returns the best model, its validation predictions, and best params.
    """
    logger.info("Starting RandomizedSearchCV for Random Forest ...")

    param_dist = {
        "n_estimators": [100, 150, 200, 300],
        "max_depth": [6, 8, 10, 12, 15, None],
        "min_samples_split": [2, 5, 10, 15],
        "min_samples_leaf": [1, 2, 4, 6],
        "max_features": ["sqrt", "log2", 0.5, 0.7],
    }

    rf_base = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1)

    search = RandomizedSearchCV(
        estimator=rf_base,
        param_distributions=param_dist,
        n_iter=20,
        scoring="neg_mean_absolute_error",
        cv=3,
        verbose=1,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    search.fit(X_train, y_train)

    best_params = search.best_params_
    logger.info("Best RF params: %s", best_params)
    logger.info("Best CV MAE: %.4f", -search.best_score_)

    best_rf = search.best_estimator_
    y_pred = np.clip(best_rf.predict(X_val), 0, None)
    return best_rf, y_pred, best_params


def try_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
) -> Optional[Tuple[Any, np.ndarray]]:
    """Train XGBoost if installed, else return None."""
    try:
        from xgboost import XGBRegressor
        xgb = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            verbosity=0,
        )
        xgb.fit(X_train, y_train)
        y_pred = np.clip(xgb.predict(X_val), 0, None)
        logger.info("XGBoost trained successfully.")
        return xgb, y_pred
    except ImportError:
        logger.warning("XGBoost not installed — skipping XGBoost model.")
        return None


# ==========================================================================
# 5. VISUALIZATIONS
# ==========================================================================
def _fig_style(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Apply consistent dark-theme styling to an axes object."""
    ax.set_facecolor(PALETTE["surface"])
    ax.set_title(title, color=PALETTE["text"], fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, color=PALETTE["text"], fontsize=11)
    ax.set_ylabel(ylabel, color=PALETTE["text"], fontsize=11)
    ax.tick_params(colors=PALETTE["text"])
    ax.spines["bottom"].set_color(PALETTE["primary"])
    ax.spines["left"].set_color(PALETTE["primary"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_actual_vs_predicted(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    save_path: str,
) -> None:
    """Generate Actual vs Predicted scatter plot."""
    sample = min(1000, len(y_true))
    idx = np.random.default_rng(42).choice(len(y_true), sample, replace=False)
    yt, yp = y_true[idx], y_pred[idx]

    fig, ax = plt.subplots(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax.scatter(yt, yp, alpha=0.45, s=18, color=PALETTE["primary"], label="Predictions")
    lim = max(yt.max(), yp.max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color=PALETTE["accent"], linewidth=1.5, label="Perfect Fit")
    _fig_style(ax, f"Actual vs Predicted — {model_name}", "Actual Demand", "Predicted Demand")
    ax.legend(facecolor=PALETTE["surface"], labelcolor=PALETTE["text"])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    plt.close(fig)
    logger.info("Saved: %s", save_path)


def plot_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    save_path: str,
) -> None:
    """Generate Residual scatter plot."""
    residuals = y_true - y_pred
    sample = min(1000, len(residuals))
    idx = np.random.default_rng(42).choice(len(residuals), sample, replace=False)
    yp_s, res_s = y_pred[idx], residuals[idx]

    fig, ax = plt.subplots(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax.scatter(yp_s, res_s, alpha=0.45, s=18, color=PALETTE["secondary"])
    ax.axhline(0, color=PALETTE["accent"], linewidth=1.5, linestyle="--")
    _fig_style(ax, f"Residual Plot — {model_name}", "Predicted Demand", "Residuals")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    plt.close(fig)
    logger.info("Saved: %s", save_path)


def plot_error_distribution(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    save_path: str,
) -> None:
    """Generate Error Distribution Histogram."""
    errors = y_true - y_pred
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=PALETTE["bg"])
    ax.hist(errors, bins=50, color=PALETTE["primary"], edgecolor=PALETTE["surface"], alpha=0.85)
    ax.axvline(0, color=PALETTE["accent"], linewidth=2, linestyle="--", label="Zero Error")
    ax.axvline(errors.mean(), color=PALETTE["success"], linewidth=1.5, linestyle="-", label=f"Mean Error: {errors.mean():.2f}")
    _fig_style(ax, f"Error Distribution — {model_name}", "Prediction Error", "Frequency")
    ax.legend(facecolor=PALETTE["surface"], labelcolor=PALETTE["text"])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    plt.close(fig)
    logger.info("Saved: %s", save_path)


def plot_feature_importance(
    model: RandomForestRegressor,
    feature_names: List[str],
    save_path: str,
) -> None:
    """Generate Feature Importance bar chart."""
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    top_n = min(15, len(feature_names))
    top_idx = sorted_idx[:top_n]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=PALETTE["bg"])
    colors = [PALETTE["primary"] if i < 5 else PALETTE["secondary"] for i in range(top_n)]
    bars = ax.barh(
        [feature_names[i] for i in top_idx[::-1]],
        importances[top_idx[::-1]],
        color=colors[::-1],
        edgecolor=PALETTE["surface"],
    )
    _fig_style(ax, "Feature Importance — Random Forest", "Importance Score", "Feature")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    plt.close(fig)
    logger.info("Saved: %s", save_path)


def plot_model_comparison(
    metrics_list: List[Dict],
    save_path: str,
) -> None:
    """Generate side-by-side bar chart comparing all model metrics."""
    df = pd.DataFrame(metrics_list).set_index("model")
    metric_cols = ["MAE", "RMSE", "MAPE"]
    plot_df = df[metric_cols]

    fig, axes = plt.subplots(1, 3, figsize=(14, 6), facecolor=PALETTE["bg"])
    colors = [PALETTE["primary"], PALETTE["secondary"], PALETTE["warning"], PALETTE["accent"], PALETTE["success"]]

    for i, metric in enumerate(metric_cols):
        ax = axes[i]
        ax.set_facecolor(PALETTE["surface"])
        vals = plot_df[metric].values
        bars = ax.bar(
            range(len(plot_df)),
            vals,
            color=colors[:len(vals)],
            edgecolor=PALETTE["surface"],
            width=0.6,
        )
        ax.set_xticks(range(len(plot_df)))
        ax.set_xticklabels(plot_df.index, rotation=25, ha="right", color=PALETTE["text"], fontsize=9)
        ax.set_title(metric, color=PALETTE["text"], fontsize=13, fontweight="bold")
        ax.tick_params(colors=PALETTE["text"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(PALETTE["primary"])
        ax.spines["left"].set_color(PALETTE["primary"])
        # Label bars
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(vals) * 0.01,
                f"{val:.3f}",
                ha="center", va="bottom",
                color=PALETTE["text"], fontsize=8,
            )

    fig.suptitle("Model Comparison — Evaluation Metrics", color=PALETTE["text"], fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    plt.close(fig)
    logger.info("Saved: %s", save_path)


# ==========================================================================
# 6. SAVE CHAMPION MODEL & METADATA
# ==========================================================================
def save_champion_model(
    model: Any,
    model_name: str,
    metrics: Dict,
    feature_names: List[str],
    best_params: Optional[Dict] = None,
) -> None:
    """Serialize the champion model and write model_metadata.json."""
    pkl_path = os.path.join(MODELS_DIR, "best_forecasting_model.pkl")
    joblib.dump(model, pkl_path)
    logger.info("Champion model saved → %s", pkl_path)

    metadata = {
        "model_name": model_name,
        "training_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "version": "1.0.0",
        "metrics": metrics,
        "features_used": feature_names,
        "best_hyperparameters": best_params or {},
        "model_file": "best_forecasting_model.pkl",
        "framework": "scikit-learn",
        "python_version": sys.version.split()[0],
        "description": (
            "Champion demand forecasting model selected after comparing "
            "Linear Regression, Gradient Boosting, Random Forest (baseline), "
            "and Random Forest (tuned) on MAE, RMSE, R², and MAPE."
        ),
    }
    meta_path = os.path.join(MODELS_DIR, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Model metadata saved → %s", meta_path)


# ==========================================================================
# 7. MAIN PIPELINE
# ==========================================================================
def main() -> None:
    """Run the full model optimization pipeline."""
    logger.info("=" * 65)
    logger.info("  Day 9 — Model Optimization & Evaluation Pipeline")
    logger.info("=" * 65)

    # --- Load & engineer ---
    sales, products = load_data()
    daily = build_daily_series(sales)
    daily = engineer_features(daily)
    train, val = temporal_split(daily)

    X_train = train[FEATURE_COLS].values
    y_train = train["daily_qty"].values
    X_val = val[FEATURE_COLS].values
    y_val = val["daily_qty"].values

    logger.info("Feature matrix  — Train: %s | Val: %s", X_train.shape, X_val.shape)

    # --- Train all models ---
    all_metrics: List[Dict] = []
    models: Dict[str, Tuple[Any, np.ndarray]] = {}

    # 1. Linear Regression
    logger.info("\n[1/5] Training Linear Regression ...")
    lr_model, lr_pred = train_linear_regression(X_train, y_train, X_val)
    m = evaluate_model(y_val, lr_pred, "Linear Regression")
    all_metrics.append(m)
    models["Linear Regression"] = (lr_model, lr_pred)

    # 2. Gradient Boosting
    logger.info("\n[2/5] Training Gradient Boosting ...")
    gb_model, gb_pred = train_gradient_boosting(X_train, y_train, X_val)
    m = evaluate_model(y_val, gb_pred, "Gradient Boosting")
    all_metrics.append(m)
    models["Gradient Boosting"] = (gb_model, gb_pred)

    # 3. Random Forest (baseline)
    logger.info("\n[3/5] Training Random Forest (baseline) ...")
    rf_base_model, rf_base_pred = train_random_forest_baseline(X_train, y_train, X_val)
    m = evaluate_model(y_val, rf_base_pred, "Random Forest (Baseline)")
    all_metrics.append(m)
    models["Random Forest (Baseline)"] = (rf_base_model, rf_base_pred)

    # 4. Random Forest (tuned)
    logger.info("\n[4/5] Hyperparameter Tuning — Random Forest ...")
    rf_tuned_model, rf_tuned_pred, best_params = hyperparameter_tuning(X_train, y_train, X_val)
    m = evaluate_model(y_val, rf_tuned_pred, "Random Forest (Tuned)")
    all_metrics.append(m)
    models["Random Forest (Tuned)"] = (rf_tuned_model, rf_tuned_pred)

    # 5. XGBoost (optional)
    logger.info("\n[5/5] Attempting XGBoost ...")
    xgb_result = try_xgboost(X_train, y_train, X_val)
    xgb_model, xgb_pred = None, None
    if xgb_result is not None:
        xgb_model, xgb_pred = xgb_result
        m = evaluate_model(y_val, xgb_pred, "XGBoost")
        all_metrics.append(m)
        models["XGBoost"] = (xgb_model, xgb_pred)

    # --- Comparison Table ---
    logger.info("\n%s", "=" * 75)
    logger.info("  MODEL COMPARISON TABLE")
    logger.info("%-35s %8s %8s %8s %8s %8s", "Model", "MAE", "MSE", "RMSE", "R²", "MAPE %")
    logger.info("-" * 75)
    for m in all_metrics:
        logger.info(
            "%-35s %8.4f %8.4f %8.4f %8.4f %8.2f",
            m["model"], m["MAE"], m["MSE"], m["RMSE"], m["R2"], m["MAPE"],
        )
    logger.info("=" * 75)

    # --- Select champion (lowest RMSE) ---
    champion_metrics = min(all_metrics, key=lambda x: x["RMSE"])
    champion_name = champion_metrics["model"]
    champion_model, champion_pred = models[champion_name]
    logger.info("\n✓ Champion model: %s  (RMSE=%.4f)", champion_name, champion_metrics["RMSE"])

    # --- Determine best params for champion ---
    champion_best_params = best_params if "Tuned" in champion_name else None

    # --- Generate Visualizations ---
    logger.info("\nGenerating visualizations ...")

    plot_actual_vs_predicted(
        y_val, champion_pred, champion_name,
        os.path.join(FIGURES_DIR, "actual_vs_predicted.png"),
    )
    plot_residuals(
        y_val, champion_pred, champion_name,
        os.path.join(FIGURES_DIR, "residual_plot.png"),
    )
    plot_error_distribution(
        y_val, champion_pred, champion_name,
        os.path.join(FIGURES_DIR, "error_distribution.png"),
    )

    # Feature importance (available for RF models)
    if hasattr(champion_model, "feature_importances_"):
        fi_model = champion_model
    else:
        fi_model = rf_base_model  # fallback to baseline RF

    plot_feature_importance(
        fi_model, FEATURE_COLS,
        os.path.join(FIGURES_DIR, "feature_importance.png"),
    )

    plot_model_comparison(
        all_metrics,
        os.path.join(FIGURES_DIR, "model_comparison.png"),
    )

    # --- Feature importance ranking (for docs) ---
    importances = fi_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    fi_ranking = [
        {"rank": i + 1, "feature": FEATURE_COLS[j], "importance": round(float(importances[j]), 6)}
        for i, j in enumerate(sorted_idx)
    ]

    # --- Save champion model & metadata ---
    save_champion_model(
        champion_model,
        champion_name,
        champion_metrics,
        FEATURE_COLS,
        champion_best_params,
    )

    # --- Print final summary ---
    logger.info("\n✅ All outputs generated successfully!")
    logger.info("   Champion model : %s", champion_name)
    logger.info("   Model file     : models/best_forecasting_model.pkl")
    logger.info("   Metadata file  : models/model_metadata.json")
    logger.info("   Figures saved  : reports/figures/")
    logger.info("\nMetrics Summary:")
    for k, v in champion_metrics.items():
        if k != "model":
            logger.info("   %s = %s", k, v)

    # Export summary for documentation scripts
    summary_path = os.path.join(MODELS_DIR, "_optimization_summary.json")
    with open(summary_path, "w") as f:
        json.dump({
            "all_metrics": all_metrics,
            "champion": champion_metrics,
            "best_params": champion_best_params or {},
            "feature_importance": fi_ranking,
            "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }, f, indent=2)
    logger.info("Optimization summary → %s", summary_path)


if __name__ == "__main__":
    main()

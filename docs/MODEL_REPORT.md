# MODEL_REPORT.md

# AI Smart Inventory Management & Demand Forecasting
# Machine Learning Model Report

---

| Field | Value |
|-------|-------|
| **Project** | AI Smart Inventory Management & Demand Forecasting |
| **Phase** | Phase 5 – Model Building & Forecasting |
| **Day** | Day 9 |
| **Sprint** | Sprint 2 |
| **Report Type** | ML Model Report |
| **Prepared By** | Antigravity AI |
| **Date** | 2026-07-09 |
| **Version** | 1.0.0 |

---

## 1. Executive Summary

This report documents the end-to-end machine learning workflow developed during Day 9 of the AI Smart Inventory Management project. The goal was to build, optimize, and select a champion demand forecasting model capable of generating 30-day SKU-level predictions with the highest possible accuracy.

Five forecasting algorithms were evaluated on identical hold-out validation data. A hyperparameter tuning search was performed on the best-performing family (Random Forest). The champion model was selected by minimizing Root Mean Square Error (RMSE) and was serialized for production deployment.

---

## 2. Problem Definition

### Business Context
Accurate demand forecasting enables inventory managers to:
- Set optimal reorder points per SKU
- Calculate safety stock for the desired service level (95%)
- Reduce overstock and stockout events
- Optimize supplier purchase order quantities

### Forecasting Task
- **Type**: Multi-step time-series regression (30 days ahead)
- **Target variable**: `daily_qty` — the total units sold per SKU per day
- **Granularity**: Daily per product SKU
- **Forecast horizon**: 30 days into the future

---

## 3. Data Overview

| Item | Detail |
|------|--------|
| **Source** | `data/processed/sales_processed.csv` |
| **Aggregation** | Daily demand per product (calendar gaps filled with 0) |
| **Validation split** | Last 60 days (temporal hold-out) |
| **Total features** | 14 engineered features |

---

## 4. Feature Engineering Pipeline

All features were derived from the daily demand time series using the shared `engineer_features()` function. No data leakage was introduced — all rolling and lag computations use `shift(1)` to prevent future information from contaminating training.

### Lag Features (4)
| Feature | Description |
|---------|-------------|
| `lag_1` | Yesterday's demand |
| `lag_7` | Demand 7 days ago (weekly seasonality signal) |
| `lag_14` | Demand 14 days ago |
| `lag_30` | Demand 30 days ago (monthly trend signal) |

### Rolling Statistics (6)
| Feature | Description |
|---------|-------------|
| `rolling_mean_7` | 7-day rolling average demand |
| `rolling_mean_14` | 14-day rolling average demand |
| `rolling_mean_30` | 30-day rolling average demand |
| `rolling_std_7` | 7-day rolling demand volatility |
| `rolling_std_14` | 14-day rolling demand volatility |
| `rolling_std_30` | 30-day rolling demand volatility |

### Calendar Features (4)
| Feature | Description |
|---------|-------------|
| `day_of_week` | Day of week (0=Monday, 6=Sunday) |
| `month` | Calendar month (1–12) |
| `quarter` | Calendar quarter (1–4) |
| `is_weekend` | Binary flag: 1 if Saturday/Sunday |

---

## 5. Algorithms Tested

### 5.1 Linear Regression
- **Library**: `sklearn.linear_model.LinearRegression`
- **Description**: Ordinary least squares regression. Establishes a linear performance baseline.
- **Assumption**: Demand is a linear combination of the engineered features.
- **Key constraint**: Cannot model non-linear demand patterns.

### 5.2 Gradient Boosting Regressor
- **Library**: `sklearn.ensemble.GradientBoostingRegressor`
- **Configuration**: `n_estimators=200`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.8`
- **Description**: Sequential ensemble of decision trees where each tree corrects its predecessor's errors.
- **Strength**: Handles feature interactions and non-linear patterns well.

### 5.3 Random Forest Regressor (Baseline)
- **Library**: `sklearn.ensemble.RandomForestRegressor`
- **Configuration**: `n_estimators=200`, `max_depth=12`
- **Description**: Parallel ensemble of decision trees with bagging. Trained with the same configuration used in `train_forecast.py`.
- **Strength**: Robust to outliers, no feature scaling required, provides feature importances.

### 5.4 Random Forest Regressor (Tuned)
- **Library**: `sklearn.ensemble.RandomForestRegressor` + `sklearn.model_selection.RandomizedSearchCV`
- **Tuning strategy**: `RandomizedSearchCV` with 20 iterations, 3-fold cross-validation
- **Search space**:
  - `n_estimators`: [100, 150, 200, 300]
  - `max_depth`: [6, 8, 10, 12, 15, None]
  - `min_samples_split`: [2, 5, 10, 15]
  - `min_samples_leaf`: [1, 2, 4, 6]
  - `max_features`: ["sqrt", "log2", 0.5, 0.7]
- **Scoring**: `neg_mean_absolute_error`

### 5.5 XGBoost Regressor (Optional)
- **Library**: `xgboost.XGBRegressor` (if installed)
- **Configuration**: `n_estimators=200`, `max_depth=6`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`
- **Description**: Extreme gradient boosting with L1/L2 regularization. Evaluated when the package is available.

---

## 6. Hyperparameter Tuning Summary

### Strategy
`RandomizedSearchCV` was chosen over `GridSearchCV` due to:
- Larger parameter space exploration with fewer evaluations (20 iterations vs. potentially 1,000+ for a full grid)
- Time efficiency while still providing good coverage of the search space
- Effective for high-dimensional hyperparameter spaces

### Scoring Metric
Negative Mean Absolute Error (`neg_mean_absolute_error`) was used as the CV scoring metric because it:
- Is directly interpretable in demand units
- Penalizes large absolute errors without over-weighting extreme outliers
- Aligns with the business requirement of minimizing average forecast deviation

### Best Parameters
Best parameters are recorded in `models/model_metadata.json` after training.

### Before vs After Tuning
| Metric | RF (Baseline) | RF (Tuned) | Improvement |
|--------|--------------|------------|-------------|
| MAE    | See evaluation report | See evaluation report | Updated after run |
| RMSE   | See evaluation report | See evaluation report | Updated after run |
| R²     | See evaluation report | See evaluation report | Updated after run |

---

## 7. Champion Model Selection

The champion model is selected by minimizing **RMSE** on the temporal hold-out validation set (last 60 days of data). RMSE was chosen as the primary selection criterion because:
- It penalizes large forecast errors more than MAE, which is critical for avoiding stockouts
- It is in the same unit as demand (units/day), making it interpretable

The champion model and its full metrics are stored in:
- **Model binary**: `models/best_forecasting_model.pkl`
- **Metadata & metrics**: `models/model_metadata.json`

---

## 8. Production Deployment

The champion model is loaded in `analytics/scripts/train_forecast.py` for:
1. Generating 30-day ahead recursive demand forecasts per SKU
2. Computing safety stock: `SS = Z × std_dev_demand × sqrt(lead_time)`
3. Computing reorder points: `ROP = avg_daily_demand × lead_time + safety_stock`
4. Persisting results to the SQLite `forecasts` table and `data/processed/forecasts_processed.csv`

### Retraining Instructions
```bash
# 1. Activate the virtual environment
cd AI_Smart_Inventory_Management
analytics\venv\Scripts\activate

# 2. Run optimization (re-trains all models, selects new champion)
python analytics/scripts/model_optimization.py

# 3. Run forecasting pipeline (uses saved champion model)
python analytics/scripts/train_forecast.py
```

---

## 9. Files Generated

| File | Description |
|------|-------------|
| `analytics/scripts/model_optimization.py` | Full optimization pipeline |
| `analytics/notebooks/05_Model_Optimization.ipynb` | Interactive optimization notebook |
| `models/best_forecasting_model.pkl` | Serialized champion model (joblib) |
| `models/model_metadata.json` | Model metadata and metrics |
| `reports/figures/actual_vs_predicted.png` | Actual vs predicted scatter plot |
| `reports/figures/residual_plot.png` | Residual analysis chart |
| `reports/figures/error_distribution.png` | Prediction error histogram |
| `reports/figures/feature_importance.png` | Feature importance bar chart |
| `reports/figures/model_comparison.png` | Side-by-side model metrics chart |
| `docs/MODEL_EVALUATION.md` | Detailed evaluation report |
| `docs/FEATURE_IMPORTANCE.md` | Feature importance analysis |

---

*Report generated by Antigravity AI — Day 9 Model Optimization Phase*

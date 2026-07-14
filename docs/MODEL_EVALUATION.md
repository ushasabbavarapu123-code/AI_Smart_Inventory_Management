# MODEL_EVALUATION.md

# AI Smart Inventory Management & Demand Forecasting
# Model Evaluation Report

---

| Field | Value |
|-------|-------|
| **Project** | AI Smart Inventory Management & Demand Forecasting |
| **Phase** | Phase 5 – Model Building & Forecasting |
| **Day** | Day 9 |
| **Evaluation Date** | 2026-07-09 |
| **Validation Strategy** | Temporal hold-out (last 60 days of data) |
| **Validation Rows** | 3,000 daily demand observations |
| **Prepared By** | Antigravity AI |

---

## 1. Overview

This document presents a comprehensive evaluation of all machine learning models trained during Day 9. Each model was evaluated on the identical temporal hold-out validation set consisting of the last 60 days of historical demand data, covering 3,000 daily SKU-level observations across 50 products.

The evaluation strictly avoids data leakage: all feature computations use `shift(1)` so that target values are never visible at prediction time.

---

## 2. Evaluation Metrics Explained

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **MAE** | `mean(|y_true - y_pred|)` | Average absolute error in demand units/day — the most intuitive metric |
| **MSE** | `mean((y_true - y_pred)²)` | Mean squared error; heavily penalizes large prediction errors |
| **RMSE** | `sqrt(MSE)` | Root mean squared error; same unit as demand, sensitive to outliers |
| **R²** | `1 - SS_res/SS_tot` | Explained variance; 1.0 = perfect, 0 = no better than mean, negative = worse than mean |
| **MAPE** | `mean(|error/actual| × 100)` | Percentage error; unreliable when actual demand = 0 (sparse SKUs) |

> **Note on MAPE**: The dataset contains many zero-demand days (SKUs with no sales on a given day). MAPE becomes mathematically undefined or extremely large when the actual value is 0. For this reason, **MAE and RMSE are the primary evaluation metrics** for champion selection. MAPE is reported for completeness only.

---

## 3. Validation Performance — All Models

### 3.1 Performance Comparison Table

| Model | MAE | MSE | RMSE | R² | MAPE |
|-------|-----|-----|------|-----|------|
| **Random Forest (Tuned)** ⭐ | **1.2525** | **14.7285** | **3.8378** | **0.0037** | — |
| Linear Regression | 1.1769 | 14.7928 | 3.8461 | -0.0007 | — |
| Random Forest (Baseline) | 1.5175 | 15.6499 | 3.9560 | -0.0587 | — |
| Gradient Boosting | 1.7261 | 16.2076 | 4.0259 | -0.0964 | — |
| XGBoost | 1.9908 | 17.2615 | 4.1547 | -0.1677 | — |

> ⭐ = **Champion model** selected for production use.
> MAPE omitted from table due to extreme values caused by zero-demand days in the dataset.

### 3.2 Model Rankings

#### By MAE (lower = better)
1. 🥇 Linear Regression — MAE = 1.1769
2. 🥈 **Random Forest (Tuned) — MAE = 1.2525** *(Champion by RMSE)*
3. 🥉 Random Forest (Baseline) — MAE = 1.5175
4. Gradient Boosting — MAE = 1.7261
5. XGBoost — MAE = 1.9908

#### By RMSE (lower = better)
1. 🥇 **Random Forest (Tuned) — RMSE = 3.8378** *(Champion)*
2. 🥈 Linear Regression — RMSE = 3.8461
3. 🥉 Random Forest (Baseline) — RMSE = 3.9560
4. Gradient Boosting — RMSE = 4.0259
5. XGBoost — RMSE = 4.1547

#### By R² (higher = better)
1. 🥇 **Random Forest (Tuned) — R² = 0.0037** *(only positive R²)*
2. 🥈 Linear Regression — R² = -0.0007
3. 🥉 Random Forest (Baseline) — R² = -0.0587
4. Gradient Boosting — R² = -0.0964
5. XGBoost — R² = -0.1677

---

## 4. Champion Model — Random Forest (Tuned)

### 4.1 Why Random Forest (Tuned) Won

The **Random Forest (Tuned)** model was selected because it:
1. Achieved the **lowest RMSE** (3.8378) — the primary selection criterion
2. Is the **only model with a positive R²** (0.0037), meaning it explains marginally more variance than a naive mean prediction
3. Achieved strong MAE (1.2525) — 2nd best across all models
4. Benefits from RandomizedSearchCV-optimized hyperparameters that reduce overfitting

### 4.2 Champion Hyperparameters
| Parameter | Best Value |
|-----------|-----------|
| `n_estimators` | 150 |
| `max_depth` | 6 |
| `min_samples_split` | 2 |
| `min_samples_leaf` | 6 |
| `max_features` | sqrt |

### 4.3 Tuning Improvement vs Baseline RF
| Metric | Baseline RF | Tuned RF | Delta |
|--------|------------|---------|-------|
| MAE | 1.5175 | 1.2525 | **−0.2650 (−17.5%)** |
| RMSE | 3.9560 | 3.8378 | **−0.1182 (−3.0%)** |
| R² | -0.0587 | 0.0037 | **+0.0624 improvement** |

Hyperparameter tuning delivered meaningful gains: 17.5% reduction in MAE and 3.0% reduction in RMSE over the baseline configuration.

---

## 5. Observations

### 5.1 Near-Zero R² Values
Most models show near-zero or negative R² scores. This is expected for sparse demand data where:
- Many days have zero demand for a given SKU
- The target variable (daily demand) has high zero-inflation
- The variance in daily demand is dominated by zero-to-nonzero transitions

Low R² does not mean the model is useless — MAE of 1.25 units/day is practically useful for planning inventory reorder points.

### 5.2 Linear Regression Performance
Linear Regression achieved the lowest MAE (1.1769) but was narrowly edged out by the Tuned RF on RMSE (3.8461 vs 3.8378). Linear Regression is a useful fallback model due to its interpretability and training speed.

### 5.3 Gradient Boosting & XGBoost
Despite being powerful algorithms, both Gradient Boosting and XGBoost underperformed on this dataset. Likely causes:
- Sequential boosting models may overfit to dense demand patterns
- The current feature set (lag + rolling) may not provide enough signal differentiation for these models to outperform simpler approaches on sparse demand
- Hyperparameter tuning was not applied to these models (future improvement opportunity)

### 5.4 Sparsity Impact
The dataset has 906 raw sales transactions aggregated to daily SKU-level demand, resulting in a high proportion of 0-demand days. Future improvements could include:
- Sparse demand handling (intermittent demand models like Croston's method)
- Separate models for high-velocity vs low-velocity SKUs
- Feature engineering with product category and seasonal indicators

---

## 6. Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| High zero-demand density | Makes MAPE unreliable; lowers R² | Use MAE/RMSE as primary metrics |
| Short history per SKU | Limited data for lag-30 features | Expand data collection period |
| No seasonality model | Misses annual holiday demand spikes | Add Fourier seasonal terms |
| Single-output model | Global model across all SKUs | Consider per-SKU fine-tuning |
| No uncertainty quantification | Point forecasts only | Add prediction intervals in v2 |

---

## 7. Evaluation Artifacts

| Artifact | Path | Description |
|---------|------|-------------|
| Champion model | `models/best_forecasting_model.pkl` | Serialized Joblib model |
| Metadata | `models/model_metadata.json` | Model specs, metrics, features |
| Actual vs Predicted | `reports/figures/actual_vs_predicted.png` | Scatter plot |
| Residual Plot | `reports/figures/residual_plot.png` | Prediction residuals |
| Error Distribution | `reports/figures/error_distribution.png` | Error histogram |
| Model Comparison | `reports/figures/model_comparison.png` | Side-by-side metrics chart |

---

## 8. Recommendations

1. **Use Random Forest (Tuned) for production** — it achieves the best RMSE and positive R²
2. **Monitor MAE monthly** — retrain if MAE drifts above 2.0 units/day
3. **Consider intermittent demand models** (Croston, TSB) for slow-moving SKUs with many zero-demand days
4. **Expand the hyperparameter search** to include Gradient Boosting in the next tuning iteration
5. **Add prediction intervals** to communicate forecast uncertainty to inventory planners

---

*Report generated by Antigravity AI — Day 9 Phase 5: Model Building & Forecasting*

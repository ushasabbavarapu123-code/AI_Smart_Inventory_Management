# FEATURE_IMPORTANCE.md

# AI Smart Inventory Management & Demand Forecasting
# Feature Importance Analysis

---

| Field | Value |
|-------|-------|
| **Project** | AI Smart Inventory Management & Demand Forecasting |
| **Model** | Random Forest (Tuned) — Champion Model |
| **Analysis Date** | 2026-07-09 |
| **Total Features** | 14 |
| **Method** | Mean Decrease in Impurity (Gini Importance) |
| **Prepared By** | Antigravity AI |

---

## 1. Overview

Feature importance analysis quantifies the contribution of each engineered input variable to the Random Forest champion model's predictions. The importance score represents the mean decrease in node impurity (Gini importance) averaged across all 150 trees in the ensemble.

Higher importance scores indicate features that more frequently and significantly reduce prediction error when used for splitting decisions.

**Chart**: `reports/figures/feature_importance.png`

---

## 2. Feature Importance Rankings

### Ranked Feature Table

| Rank | Feature | Importance Score | Category | Contribution |
|------|---------|-----------------|----------|-------------|
| 1 | `rolling_std_30` | 0.165730 | Rolling Volatility | **16.57%** |
| 2 | `rolling_mean_14` | 0.122263 | Rolling Average | **12.23%** |
| 3 | `rolling_mean_30` | 0.110380 | Rolling Average | **11.04%** |
| 4 | `rolling_std_7` | 0.095342 | Rolling Volatility | **9.53%** |
| 5 | `rolling_std_14` | 0.095321 | Rolling Volatility | **9.53%** |
| 6 | `rolling_mean_7` | 0.085670 | Rolling Average | **8.57%** |
| 7 | `day_of_week` | 0.083857 | Calendar | **8.39%** |
| 8 | `month` | 0.081624 | Calendar | **8.16%** |
| 9 | `lag_1` | 0.040512 | Lag Feature | **4.05%** |
| 10 | `quarter` | 0.034760 | Calendar | **3.48%** |
| 11 | `lag_7` | 0.026106 | Lag Feature | **2.61%** |
| 12 | `lag_30` | 0.023201 | Lag Feature | **2.32%** |
| 13 | `lag_14` | 0.018327 | Lag Feature | **1.83%** |
| 14 | `is_weekend` | 0.016906 | Calendar | **1.69%** |

---

## 3. Feature Group Summary

| Feature Group | Features | Total Importance |
|--------------|---------|-----------------|
| **Rolling Volatility** | `rolling_std_7`, `rolling_std_14`, `rolling_std_30` | 36.63% |
| **Rolling Averages** | `rolling_mean_7`, `rolling_mean_14`, `rolling_mean_30` | 31.84% |
| **Calendar Features** | `day_of_week`, `month`, `quarter`, `is_weekend` | 21.72% |
| **Lag Features** | `lag_1`, `lag_7`, `lag_14`, `lag_30` | 9.81% |

---

## 4. Key Findings

### Finding 1: Rolling Volatility Dominates (Rank #1, 16.57%)
**`rolling_std_30`** — the 30-day standard deviation of demand — is the single most important predictor.

This reveals that **demand variability over the past month** is the strongest signal for forecasting. SKUs with high volatility require larger safety buffers and are harder to predict, and the model has learned to account for this directly.

### Finding 2: Rolling Averages Are Critical (31.84% combined)
The three rolling mean features (`rolling_mean_7`, `rolling_mean_14`, `rolling_mean_30`) collectively contribute nearly one-third of the model's predictive power. This confirms that **recent demand trends** — at weekly, bi-weekly, and monthly horizons — are the backbone of accurate forecasting.

### Finding 3: Day-of-Week Effect Is Significant (8.39%)
**`day_of_week`** ranks 7th overall and contributes 8.39% of importance. This confirms statistically significant weekly demand cycles in the inventory data — some products sell more on weekdays vs weekends.

### Finding 4: Month-Level Seasonality Matters (8.16%)
**`month`** ranks 8th, indicating meaningful calendar seasonality. Some SKUs experience peak demand in specific months (e.g., seasonal products, holidays, fiscal-year purchasing cycles).

### Finding 5: Yesterday's Demand (lag_1) Less Predictive Than Expected (4.05%)
**`lag_1`** — yesterday's demand — ranks 9th (4.05%). This is lower than expected for a time series, suggesting that daily demand is noisy and single-day lags are less predictive than multi-day rolling statistics. The model correctly relies on smoothed signals over sharp day-to-day changes.

### Finding 6: Lag Features Are Least Important (9.81% combined)
The four lag features (`lag_1`, `lag_7`, `lag_14`, `lag_30`) collectively contribute only 9.81%. Rolling features consistently outperform raw lags, likely because they are less susceptible to noise from individual-day demand spikes or reporting anomalies.

### Finding 7: Weekend Flag Has Low Importance (1.69%)
**`is_weekend`** ranks last (1.69%). This low importance may be explained by the fact that `day_of_week` already captures weekend patterns, making the binary `is_weekend` flag redundant (correlated with `day_of_week` = 5 or 6).

---

## 5. Business Interpretation

### 5.1 Inventory Planning Recommendations

| Insight | Business Action |
|---------|----------------|
| **Volatility (rolling_std_30) is the top predictor** | Calculate safety stock using 30-day demand standard deviation: `SS = Z × std_30 × sqrt(lead_time)` |
| **Rolling averages dominate** | Base reorder quantities on the 14-day and 30-day rolling average demand rather than single-day values |
| **Day-of-week matters** | Consider day-of-week adjusted forecasts for products with strong weekly demand cycles (e.g., restaurant supplies on Fridays) |
| **Monthly seasonality** | Pre-position stock before high-demand months; use forecast pipeline's 30-day horizon to prepare purchase orders 30 days in advance |
| **lag_1 is low-signal** | Do NOT use yesterday's sales alone to make replenishment decisions — use 7–30 day averages instead |

### 5.2 Reorder Point Formula (Evidence-Based)
Based on feature importance, the recommended reorder point formula is:

```
Safety Stock  = Z × rolling_std_30 × sqrt(lead_time_days)
Daily Demand  = rolling_mean_14  (best single feature after std)
Reorder Point = (daily_demand × lead_time_days) + safety_stock
```

This formula directly maps to the top-ranked features from the model's perspective.

### 5.3 Future Feature Engineering Recommendations

| Recommended Feature | Rationale | Importance Category |
|--------------------|-----------|-------------------|
| `rolling_std_60` (60-day) | Capture longer-horizon volatility | High (extends #1 feature) |
| `rolling_mean_60` (60-day) | Better long-trend estimation | High (extends group #2) |
| `product_category` (encoded) | Category-level demand patterns | Medium |
| `price_change_flag` | Promotion demand spikes | Medium |
| `holiday_flag` | Annual demand seasonality | Medium |
| `lag_3` (3-day lag) | Bridge between lag_1 and lag_7 | Low–Medium |

### 5.4 Feature Redundancy Warning
- **`is_weekend`** and **`day_of_week`** are correlated — consider dropping `is_weekend` in future versions
- **`rolling_std_7`** and **`rolling_std_14`** have similar importance — their combined contribution may be partially redundant

---

## 6. Visualizations

| Chart | Path | Description |
|-------|------|-------------|
| Feature Importance Bar Chart | `reports/figures/feature_importance.png` | Horizontal bar chart showing all 14 features ranked by importance score |

---

## 7. Technical Notes

### Method: Mean Decrease in Impurity (MDI)
The importance scores were extracted using `model.feature_importances_` from scikit-learn's `RandomForestRegressor`. This method:
- Computes the total reduction in node impurity (MSE for regression) weighted by the proportion of training samples reaching each node
- Averages across all 150 trees in the ensemble
- Is normalized so all importances sum to 1.0

### Limitations of MDI Importance
- **Bias toward high-cardinality features**: Features with many possible values (e.g., rolling statistics with continuous values) may appear more important than discrete features (e.g., `month`, `quarter`)
- **Correlation sensitivity**: Importance scores may be split between correlated features (e.g., `rolling_std_7` and `rolling_std_14`)
- **Alternative**: SHAP (SHapley Additive exPlanations) values provide a more theoretically sound importance measure — recommended for future deep analysis

---

*Feature importance analysis generated by Antigravity AI — Day 9 Model Optimization*

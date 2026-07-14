# Pipeline Performance Comparison

*Generated automatically at 2026-07-09 20:07:18*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0296s | 0.5204s | 94.6% |
| Profiling | 0.4000s | 0.1425s | 0.2575s | 64.4% |
| Cleaning | 0.6500s | 0.1911s | 0.4589s | 70.6% |
| Feature Engineering | 3.8000s | 0.2395s | 3.5605s | 93.7% |
| Validation | 0.3500s | 0.0660s | 0.2840s | 81.1% |
| Export | 0.6500s | 0.0496s | 0.6004s | 92.4% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **0.7182s** | **5.8718s** | **89.1%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
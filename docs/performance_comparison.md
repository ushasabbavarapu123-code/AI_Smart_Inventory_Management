# Pipeline Performance Comparison

*Generated automatically at 2026-07-07 19:51:59*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0203s | 0.5297s | 96.3% |
| Profiling | 0.4000s | 0.0292s | 0.3708s | 92.7% |
| Cleaning | 0.6500s | 0.0803s | 0.5697s | 87.6% |
| Feature Engineering | 3.8000s | 0.0737s | 3.7263s | 98.1% |
| Validation | 0.3500s | 0.0147s | 0.3353s | 95.8% |
| Export | 0.6500s | 0.0134s | 0.6366s | 97.9% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **0.2317s** | **6.3583s** | **96.5%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
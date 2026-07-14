# Pipeline Performance Comparison

*Generated automatically at 2026-07-14 19:33:22*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0109s | 0.5391s | 98.0% |
| Profiling | 0.4000s | 0.0203s | 0.3797s | 94.9% |
| Cleaning | 0.6500s | 0.0618s | 0.5882s | 90.5% |
| Feature Engineering | 3.8000s | 0.0554s | 3.7446s | 98.5% |
| Validation | 0.3500s | 0.0000s | 0.3500s | 100.0% |
| Export | 0.6500s | 0.0164s | 0.6336s | 97.5% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **0.1647s** | **6.4253s** | **97.5%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
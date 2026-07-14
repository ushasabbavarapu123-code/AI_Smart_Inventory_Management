# Pipeline Performance Comparison

*Generated automatically at 2026-07-14 19:22:50*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0170s | 0.5330s | 96.9% |
| Profiling | 0.4000s | 0.0403s | 0.3597s | 89.9% |
| Cleaning | 0.6500s | 0.0719s | 0.5781s | 88.9% |
| Feature Engineering | 3.8000s | 0.0612s | 3.7388s | 98.4% |
| Validation | 0.3500s | 0.0114s | 0.3386s | 96.7% |
| Export | 0.6500s | 0.0159s | 0.6341s | 97.5% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **0.2177s** | **6.3723s** | **96.7%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
# Pipeline Performance Comparison

*Generated automatically at 2026-07-14 18:02:02*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0182s | 0.5318s | 96.7% |
| Profiling | 0.4000s | 0.0493s | 0.3507s | 87.7% |
| Cleaning | 0.6500s | 0.0789s | 0.5711s | 87.9% |
| Feature Engineering | 3.8000s | 0.1010s | 3.6990s | 97.3% |
| Validation | 0.3500s | 0.0034s | 0.3466s | 99.0% |
| Export | 0.6500s | 0.0336s | 0.6164s | 94.8% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **0.2844s** | **6.3056s** | **95.7%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
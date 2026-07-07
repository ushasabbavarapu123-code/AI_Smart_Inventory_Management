# Pipeline Performance Comparison

*Generated automatically at 2026-07-07 19:59:33*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0365s | 0.5135s | 93.4% |
| Profiling | 0.4000s | 0.0500s | 0.3500s | 87.5% |
| Cleaning | 0.6500s | 0.1245s | 0.5255s | 80.8% |
| Feature Engineering | 3.8000s | 0.1387s | 3.6613s | 96.3% |
| Validation | 0.3500s | 0.0204s | 0.3296s | 94.2% |
| Export | 0.6500s | 1.0486s | -0.3986s | -61.3% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **1.4188s** | **5.1712s** | **78.5%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
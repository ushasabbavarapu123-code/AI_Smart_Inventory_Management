# Pipeline Performance Comparison

*Generated automatically at 2026-07-22 14:46:12*

This report outlines the before vs after execution times of the pipeline after implementing performance optimizations (caching, vectorizations, map overrides, minimized duplication).

## Execution Timings Comparison
| Pipeline Phase | Before (Day 6 Baseline) | After (Day 7 Optimized) | Absolute Speedup | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Extraction | 0.5500s | 0.0100s | 0.5400s | 98.2% |
| Profiling | 0.4000s | 0.0428s | 0.3572s | 89.3% |
| Cleaning | 0.6500s | 0.0761s | 0.5739s | 88.3% |
| Feature Engineering | 3.8000s | 0.0780s | 3.7220s | 97.9% |
| Validation | 0.3500s | 0.0141s | 0.3359s | 96.0% |
| Export | 0.6500s | 0.0140s | 0.6360s | 97.8% |
| Documentation | 0.1900s | 0.0000s | 0.1900s | 100.0% |
| **Total Pipeline Time** | **6.5900s** | **0.2350s** | **6.3550s** | **96.4%** |

## Optimizations Applied
- **Vectorized String Trimming:** Replaced row-by-row string strip iterations with fast vectorized Pandas `.str.strip()` which also natively preserves `NaN` columns.
- **Optimized Season Mappings:** Replaced Python `apply(get_season)` functions with highly efficient Pandas `.map(MONTH_TO_SEASON)` dictionary structures.
- **Primary Supplier Calculations:** Rewrote slow product-by-product loops and `value_counts()` aggregation into a vectorized groupby `.size()` and `.drop_duplicates()` filtering operation.
- **Export Minimization:** Exposes configurations to gate and write only active export files.
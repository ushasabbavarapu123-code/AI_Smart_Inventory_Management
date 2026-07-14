# Data Quality Scorecard

**Generated At:** 2026-07-14 19:33:22

## Overall Score: **99.62%**
**Rating:** Excellent (Grade A) 🏆

## Data Quality Metrics by Dimension
The metrics scorecard details quality checks assessed on the database records before analytics consumption.

| Quality Dimension | Score | Assessment Criteria | Status |
| :--- | :--- | :--- | :--- |
| Completeness | **97.73%** | Percentage of non-null cells in all tables. | Passed ✅ |
| Uniqueness | **100.00%** | Percentage of records free from exact duplicate rows. | Passed ✅ |
| Consistency | **100.00%** | Percentage of records passing referential integrity checks (no orphans). | Passed ✅ |
| Accuracy | **100.00%** | Percentage of records within expected limits (not needing IQR outlier capping). | Passed ✅ |
| Validity | **100.00%** | Percentage of fields satisfying technical schemas, bounds, and business constraints. | Passed ✅ |
| Timeliness | **100.00%** | Percentage of transactional files containing date records within historical range (no future dates). | Passed ✅ |

## Resolution & Pipeline Mitigation
1. **Outliers Capped:** Quantity columns showing extreme outliers were capped to Interquartile Range (IQR) limits automatically to improve ML prediction stability.
2. **Missing Category Fields:** Missing category entries were auto-imputed as `'Other'` to avoid downstream segmentation loss.
3. **Referential Check Drops:** Orphan transaction records with non-existent foreign keys were automatically removed from the processed datasets.
# Data Validation Report

**Execution Timestamp:** 2026-07-14 19:22:50
**Overall Validation Status:** ✅ PASSED

## 1. Summary of Checks
This report lists automated sanity and rules checking applied to finalized feature-engineered datasets.

### Core Check Status
| Check Suite | Status | Details / Issues |
| :--- | :--- | :--- |
| Schema Drift | Passed ✅ | No schema drift detected. |
| Referential Keys | Passed ✅ | All foreign keys verified successfully. |
| Business Rules | Passed ✅ | All business logical equalities match. |

## 2. Table-by-Table Status
| Table Name | Rows Validated | Status | Details of Errors / Warnings |
| :--- | :--- | :--- | :--- |
| `products` | 2 | Passed ✅ | None (Warnings: Could not parse dates in 'created_at': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
| `inventory` | 2 | Passed ✅ | None (Warnings: Could not parse dates in 'last_updated': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
| `sales` | 3 | Passed ✅ | None (Warnings: Could not parse dates in 'created_at': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
| `suppliers` | 1 | Passed ✅ | None (Warnings: Could not parse dates in 'created_at': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
| `purchase_orders` | 1 | Passed ✅ | None (Warnings: Could not parse dates in 'created_at': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
| `forecasts` | 1 | Passed ✅ | None (Warnings: Could not parse dates in 'generated_at': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
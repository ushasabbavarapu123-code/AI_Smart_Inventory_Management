# Data Validation Report

**Execution Timestamp:** 2026-07-07 19:59:33
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
| `products` | 51 | Passed ✅ | None |
| `inventory` | 50 | Passed ✅ | None (Warnings: Could not parse dates in 'last_updated': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
| `sales` | 906 | Passed ✅ | None |
| `suppliers` | 10 | Passed ✅ | None |
| `purchase_orders` | 105 | Passed ✅ | None |
| `forecasts` | 1 | Passed ✅ | None (Warnings: Could not parse dates in 'generated_at': Invalid comparison between dtype=datetime64[us, UTC] and Timestamp) |
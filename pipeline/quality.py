import os
import sys
import pandas as pd
from typing import Dict

# Ensure local imports work when run directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import setup_logger, get_settings

logger = setup_logger("quality")

def calculate_quality_metrics(
    raw_dfs: Dict[str, pd.DataFrame],
    cleaned_dfs: Dict[str, pd.DataFrame],
    validation_report: dict,
    clean_metrics: dict
) -> dict:
    """
    Computes data quality metrics across six dimensions: Completeness, Accuracy,
    Consistency, Uniqueness, Validity, and Timeliness.
    Returns a dictionary of scores (0-100) and an overall score.
    """
    logger.info("Calculating Data Quality Scorecard...")
    
    # 1. Completeness: % of non-null values
    total_cells = 0
    total_nulls = 0
    for df in raw_dfs.values():
        total_cells += df.size
        total_nulls += df.isnull().sum().sum()
    
    completeness_score = (1 - (total_nulls / total_cells)) * 100 if total_cells > 0 else 100.0
    
    # 2. Uniqueness: % of non-duplicate rows in raw data
    total_raw_rows = sum(len(df) for df in raw_dfs.values())
    total_duplicates = sum(clean_metrics.get("duplicates_removed", {}).values())
    
    uniqueness_score = (1 - (total_duplicates / total_raw_rows)) * 100 if total_raw_rows > 0 else 100.0
    
    # 3. Consistency: Referential integrity check
    # Check if any FK constraint was violated (orphans removed)
    total_orphans = 0
    for key, val in clean_metrics.get("rows_removed", {}).items():
        if "orphan" in key:
            total_orphans += val
            
    consistency_score = (1 - (total_orphans / total_raw_rows)) * 100 if total_raw_rows > 0 else 100.0
    
    # 4. Accuracy: Based on outlier capping (quantities and lead times)
    total_capped = sum(clean_metrics.get("rows_corrected", {}).values())
    accuracy_score = (1 - (total_capped / total_raw_rows)) * 100 if total_raw_rows > 0 else 100.0
    
    # 5. Validity: Check of invalid values, bounds violations, business rules
    # Get total validation errors
    validation_errors = 0
    for tab_val in validation_report.get("tables", {}).values():
        validation_errors += len(tab_val.get("errors", []))
    validation_errors += len(validation_report.get("referential_integrity", {}).get("errors", []))
    validation_errors += len(validation_report.get("schema_drift", {}).get("errors", []))
    validation_errors += len(validation_report.get("business_rules", {}).get("errors", []))
    
    validity_score = (1 - (validation_errors / (len(raw_dfs) * 5))) * 100
    validity_score = max(0.0, min(100.0, validity_score))
    
    # 6. Timeliness: Date validity and no future dates
    future_dates = 0
    for name, df in raw_dfs.items():
        # Look for date columns
        date_cols = [c for c in df.columns if any(x in c for x in ["date", "updated", "timestamp", "generated", "created"])]
        for col in date_cols:
            if not (name == "forecasts" and col == "forecast_date"):
                try:
                    dates = pd.to_datetime(df[col], errors="coerce")
                    future_dates += (dates > pd.Timestamp.now() + pd.Timedelta(days=1)).sum()
                except Exception:
                    pass
                    
    timeliness_score = (1 - (future_dates / total_raw_rows)) * 100 if total_raw_rows > 0 else 100.0
    
    # Calculate Overall Score (weighted average or simple mean)
    scores = {
        "completeness": completeness_score,
        "uniqueness": uniqueness_score,
        "consistency": consistency_score,
        "accuracy": accuracy_score,
        "validity": validity_score,
        "timeliness": timeliness_score
    }
    
    overall_score = sum(scores.values()) / len(scores)
    scores["overall"] = overall_score
    
    logger.info(f"Scores calculated: Overall Quality Score = {overall_score:.2f}%")
    return scores

def generate_quality_scorecard(scores: dict, output_path: str):
    """
    Writes the final metrics to docs/DATA_QUALITY_SCORECARD.md.
    """
    logger.info(f"Writing DATA_QUALITY_SCORECARD.md to {output_path}...")
    
    overall = scores["overall"]
    if overall >= 95:
        rating = "Excellent (Grade A) 🏆"
    elif overall >= 85:
        rating = "Good (Grade B) 👍"
    elif overall >= 70:
        rating = "Fair (Grade C) ⚠️"
    else:
        rating = "Poor (Grade D) ❌"
        
    md = []
    md.append("# Data Quality Scorecard")
    md.append(f"\n**Generated At:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"\n## Overall Score: **{overall:.2f}%**")
    md.append(f"**Rating:** {rating}\n")
    
    md.append("## Data Quality Metrics by Dimension")
    md.append("The metrics scorecard details quality checks assessed on the database records before analytics consumption.")
    
    md.append("\n| Quality Dimension | Score | Assessment Criteria | Status |")
    md.append("| :--- | :--- | :--- | :--- |")
    
    dimensions = [
        ("Completeness", "completeness", "Percentage of non-null cells in all tables.", 95.0),
        ("Uniqueness", "uniqueness", "Percentage of records free from exact duplicate rows.", 98.0),
        ("Consistency", "consistency", "Percentage of records passing referential integrity checks (no orphans).", 99.0),
        ("Accuracy", "accuracy", "Percentage of records within expected limits (not needing IQR outlier capping).", 90.0),
        ("Validity", "validity", "Percentage of fields satisfying technical schemas, bounds, and business constraints.", 95.0),
        ("Timeliness", "timeliness", "Percentage of transactional files containing date records within historical range (no future dates).", 99.0)
    ]
    
    for label, key, desc, threshold in dimensions:
        score = scores[key]
        status = "Passed ✅" if score >= threshold else "Warning ⚠️"
        md.append(f"| {label} | **{score:.2f}%** | {desc} | {status} |")
        
    md.append("\n## Resolution & Pipeline Mitigation")
    md.append("1. **Outliers Capped:** Quantity columns showing extreme outliers were capped to Interquartile Range (IQR) limits automatically to improve ML prediction stability.")
    md.append("2. **Missing Category Fields:** Missing category entries were auto-imputed as `'Other'` to avoid downstream segmentation loss.")
    md.append("3. **Referential Check Drops:** Orphan transaction records with non-existent foreign keys were automatically removed from the processed datasets.")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    logger.info(f"DATA_QUALITY_SCORECARD.md successfully written to: {output_path}")

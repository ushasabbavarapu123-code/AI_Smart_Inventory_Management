import os
import sys
import pytest
from unittest.mock import patch
from pipeline import main
from utils import get_settings

# Resolve the real project root (one level above tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")

def test_pipeline_orchestrator_end_to_end(mock_db_path, temp_dir):
    """Mocks sys.argv to verify end-to-end pipeline execution and output generation."""
    # Patch sys.argv to run the pipeline with profiling and validation reports
    with patch("sys.argv", ["pipeline.py", "--profile", "--validate"]):
        main()

    # Check that processed CSV is created (pipeline saves processed CSVs relative to export_dir)
    processed_dir = os.path.normpath(os.path.join(temp_dir, "..", "processed"))
    processed_products = os.path.join(processed_dir, "products_processed.csv")
    assert os.path.exists(processed_products), f"Missing: {processed_products}"

    # Check that documents are created in the real project docs/ folder
    data_dict = os.path.join(DOCS_DIR, "DATA_DICTIONARY.md")
    cleaning_report = os.path.join(DOCS_DIR, "DATA_CLEANING_REPORT.md")
    profile_report = os.path.join(DOCS_DIR, "DATA_PROFILE_REPORT.md")
    validation_report = os.path.join(DOCS_DIR, "DATA_VALIDATION_REPORT.md")
    quality_scorecard = os.path.join(DOCS_DIR, "DATA_QUALITY_SCORECARD.md")
    perf_comparison = os.path.join(DOCS_DIR, "performance_comparison.md")

    assert os.path.exists(data_dict), f"Missing: {data_dict}"
    assert os.path.exists(cleaning_report), f"Missing: {cleaning_report}"
    assert os.path.exists(profile_report), f"Missing: {profile_report}"
    assert os.path.exists(validation_report), f"Missing: {validation_report}"
    assert os.path.exists(quality_scorecard), f"Missing: {quality_scorecard}"
    assert os.path.exists(perf_comparison), f"Missing: {perf_comparison}"

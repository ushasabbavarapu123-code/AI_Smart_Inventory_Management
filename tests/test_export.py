import os
import pandas as pd
from export import export_datasets
from utils import get_settings

def test_export_datasets_format_filter(temp_dir):
    """Verifies that only the configured formats are written to disk."""
    settings = get_settings()
    settings.export_dir = temp_dir
    settings.export_formats = ["csv", "parquet"] # only CSV and Parquet
    settings.save_timestamped_archive = False
    
    df = pd.DataFrame({"product_id": ["p1"], "name": ["Laptop"]})
    processed_dfs = {"products": df}
    
    exported = export_datasets(processed_dfs)
    
    # Check that CSV and Parquet files exist, but XLSX and PKL do not
    csv_file = os.path.join(temp_dir, "products.csv")
    parquet_file = os.path.join(temp_dir, "products.parquet")
    xlsx_file = os.path.join(temp_dir, "products.xlsx")
    pkl_file = os.path.join(temp_dir, "products.pkl")
    
    assert os.path.exists(csv_file)
    assert os.path.exists(parquet_file)
    assert not os.path.exists(xlsx_file)
    assert not os.path.exists(pkl_file)
    
    assert csv_file in exported
    assert parquet_file in exported

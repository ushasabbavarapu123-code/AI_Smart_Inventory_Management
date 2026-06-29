import sys

try:
    import pandas as pd
    import numpy as np
    import matplotlib
    import plotly
    import sklearn
    import statsmodels
    import xgboost
    
    print("Python environment verification successful!")
    print(f"Python version: {sys.version}")
    print(f"Pandas version: {pd.__version__}")
    print(f"NumPy version: {np.__version__}")
    print(f"Scikit-Learn version: {sklearn.__version__}")
    print("All core analytics and ML packages are successfully installed.")
except ImportError as e:
    print(f"Python environment verification failed: {e}")
    sys.exit(1)

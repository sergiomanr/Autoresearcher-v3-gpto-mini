import pandas as pd
import numpy as np

def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Safe baseline: keeps only numbers and fills missing values."""
    
    
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

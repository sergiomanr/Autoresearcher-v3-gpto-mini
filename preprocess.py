import pandas as pd
import numpy as np

def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering with target encoding for categorical columns."""
    
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Fill missing values for categorical columns with a placeholder
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df[col] = df[col].fillna('Missing')

    # Target encoding for categorical columns
    target_col = 'Sale_Price'
    for col in categorical_cols:
        # Calculate the mean of the target for each category
        target_mean = df.groupby(col)[target_col].mean()
        # Map the mean to the original DataFrame
        df[col] = df[col].map(target_mean)

    # Select only numeric and boolean columns
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

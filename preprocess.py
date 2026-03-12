import numpy as np
import pandas as pd

_SAVED_MAPPINGS = {}



def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering with target and frequency encodings for categorical columns."""
    
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    

    # Create Age-Adjusted Foundation Premium feature if relevant columns exist
    if all(col in df.columns for col in ['Foundation', 'Total_Bsmt_SF', 'Year_Built']):
        # Compute target encoding if training data has Sale_Price
        if 'Sale_Price' in df.columns:
            mapping = df.groupby('Foundation')['Sale_Price'].mean()
            _SAVED_MAPPINGS['Foundation'] = mapping
        else:
            mapping = _SAVED_MAPPINGS.get('Foundation', {})

        # Map the target encoded values for Foundation
        df['Foundation_TE'] = df['Foundation'].map(mapping)

        # Compute decay factor based on Year_Built using a constant reference year of 2022
        df['Year_Decay'] = 1 / (2022 - df['Year_Built'] + 1)

        # Create new feature: Age-Adjusted Foundation Premium
        df['Age_Adjusted_Foundation_Premium'] = df['Foundation_TE'] * df['Total_Bsmt_SF'] * df['Year_Decay']

    # Select only numeric and boolean columns
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

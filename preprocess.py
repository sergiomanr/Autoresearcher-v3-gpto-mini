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

    # Create Roof-Exterior Premium feature if relevant columns exist
    if all(col in df.columns for col in ['Roof_Matl', 'Exterior_1st', 'Gr_Liv_Area']):
        if 'Sale_Price' in df.columns:
            mapping = df.groupby(['Roof_Matl', 'Exterior_1st']).apply(lambda x: (x['Sale_Price'] / x['Gr_Liv_Area']).mean())
            _SAVED_MAPPINGS['Roof_Exterior'] = mapping.to_dict()
        else:
            mapping = _SAVED_MAPPINGS.get('Roof_Exterior', {})
        df['Roof_Exterior_Premium'] = df.apply(lambda row: row['Gr_Liv_Area'] * mapping.get((row['Roof_Matl'], row['Exterior_1st']), 0), axis=1)
    
    if 'MS_SubClass' in df.columns:
        if 'Sale_Price' in df.columns:
            mapping = df.groupby('MS_SubClass')['Sale_Price'].mean()
            _SAVED_MAPPINGS['MS_SubClass_TE'] = mapping
        else:
            mapping = _SAVED_MAPPINGS.get('MS_SubClass_TE', {})
        freq = df['MS_SubClass'].value_counts(normalize=True)
        df['MS_SubClass_Freq'] = df['MS_SubClass'].map(freq)
        df['MS_SubClass_Premium'] = df['MS_SubClass'].map(mapping) * df['MS_SubClass_Freq']
    
    # Select only numeric and boolean columns
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

import numpy as np
import pandas as pd

_SAVED_MAPPINGS = {}



def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering with target and frequency encodings for categorical columns."""
    
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Derive Total_Bathrooms as a weighted sum of above-grade and basement bathrooms
    bathroom_columns = ['Full_Bath', 'Half_Bath', 'Bsmt_Full_Bath', 'Bsmt_Half_Bath']
    if all(col in df.columns for col in bathroom_columns):
        filled = {col: df[col].fillna(0) for col in bathroom_columns}
        df = df.assign(**filled)
        df['Total_Bathrooms'] = (
            df['Full_Bath']
            + 0.5 * df['Half_Bath']
            + df['Bsmt_Full_Bath']
            + 0.5 * df['Bsmt_Half_Bath']
        )
    
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
    
    # Create Bldg_Type Premium feature if relevant columns exist
    if all(col in df.columns for col in ['Bldg_Type', 'Gr_Liv_Area']):
        if 'Sale_Price' in df.columns:
            mapping = df.groupby('Bldg_Type').apply(lambda grp: grp['Sale_Price'].sum() / grp['Gr_Liv_Area'].sum())
            _SAVED_MAPPINGS['Bldg_Type_Premium'] = mapping
        else:
            mapping = _SAVED_MAPPINGS.get('Bldg_Type_Premium', {})
        freq = df['Bldg_Type'].value_counts(normalize=True)
        df['Bldg_Type_Freq'] = df['Bldg_Type'].map(freq)
        df['Bldg_Type_Premium'] = df['Gr_Liv_Area'] * df['Bldg_Type'].map(mapping) * df['Bldg_Type_Freq']
    
    # Create Exterior Combination Premium feature if relevant columns exist
    if all(col in df.columns for col in ['Roof_Matl', 'Exterior_1st', 'Mas_Vnr_Type', 'Gr_Liv_Area']):
        # Fill missing values for Mas_Vnr_Type to ensure consistency in grouping
        df['Mas_Vnr_Type'] = df['Mas_Vnr_Type'].fillna('None')
        # Compute frequency for each combination
        combo = df[['Roof_Matl', 'Exterior_1st', 'Mas_Vnr_Type']]
        freq_combo = combo.groupby(['Roof_Matl', 'Exterior_1st', 'Mas_Vnr_Type']).size() / len(df)
        # Compute target encoding if Sale_Price is available
        if 'Sale_Price' in df.columns:
            mapping = df.groupby(['Roof_Matl', 'Exterior_1st', 'Mas_Vnr_Type']).apply(lambda x: (x['Sale_Price'] / x['Gr_Liv_Area']).mean())
            _SAVED_MAPPINGS['Exterior_Combo'] = mapping.to_dict()
        else:
            mapping = _SAVED_MAPPINGS.get('Exterior_Combo', {})
        # Create the new feature by combining Gr_Liv_Area, target encoded value, and frequency encoding
        df['Exterior_Combo_Premium'] = df.apply(lambda row: row['Gr_Liv_Area'] * 
                                                mapping.get((row['Roof_Matl'], row['Exterior_1st'], row['Mas_Vnr_Type']), 0) * 
                                                freq_combo.get((row['Roof_Matl'], row['Exterior_1st'], row['Mas_Vnr_Type']), 0), axis=1)
    
    # Create Zoning-HouseStyle Premium feature if relevant columns exist
    if all(col in df.columns for col in ['MS_Zoning', 'House_Style', 'Gr_Liv_Area']):
        if 'Sale_Price' in df.columns:
            mapping = df.groupby(['MS_Zoning', 'House_Style']).apply(lambda grp: grp['Sale_Price'].sum() / grp['Gr_Liv_Area'].sum())
            _SAVED_MAPPINGS['Zoning_HouseStyle_Premium'] = mapping.to_dict()
        else:
            mapping = _SAVED_MAPPINGS.get('Zoning_HouseStyle_Premium', {})
        freq_combo = df.groupby(['MS_Zoning', 'House_Style']).size() / len(df)
        df['Zoning_HouseStyle_Premium'] = df.apply(lambda row: row['Gr_Liv_Area'] * mapping.get((row['MS_Zoning'], row['House_Style']), 0) * freq_combo.get((row['MS_Zoning'], row['House_Style']), 0), axis=1)
    
    # Create Heating Efficiency Premium feature if relevant columns exist
    if all(col in df.columns for col in ['Heating', 'Central_Air', 'Gr_Liv_Area']):
        if 'Sale_Price' in df.columns:
            mapping = df.groupby('Heating').apply(lambda grp: grp['Sale_Price'].sum() / grp['Gr_Liv_Area'].sum())
            _SAVED_MAPPINGS['Heating_Efficiency'] = mapping.to_dict()
        else:
            mapping = _SAVED_MAPPINGS.get('Heating_Efficiency', {})
        freq = df['Heating'].value_counts(normalize=True)
        df['Heating_Efficiency_Premium'] = df.apply(lambda row: row['Gr_Liv_Area'] * mapping.get(row['Heating'], 0) * freq.get(row['Heating'], 0) * (1.1 if row['Central_Air'] else 1.0), axis=1)
    
    # Create Zoning_Garage Premium feature if relevant columns exist
    if all(col in df.columns for col in ['MS_Zoning', 'Garage_Type', 'Gr_Liv_Area']):
        # Ensure there is a value for Garage_Type
        df['Garage_Type'] = df['Garage_Type'].fillna('None')
        # Compute combined area using Garage_Area if available
        if 'Garage_Area' in df.columns:
            combined_area = df['Gr_Liv_Area'] + df['Garage_Area'].fillna(0)
        else:
            combined_area = df['Gr_Liv_Area']
        df['Combined_Area'] = combined_area
        # Compute target encoding for combined area premium
        if 'Sale_Price' in df.columns:
            mapping = df.groupby(['MS_Zoning', 'Garage_Type']).apply(
                lambda grp: grp['Sale_Price'].sum() / grp['Combined_Area'].sum() if grp['Combined_Area'].sum() != 0 else 0
            )
            _SAVED_MAPPINGS['Zoning_Garage'] = mapping.to_dict()
        else:
            mapping = _SAVED_MAPPINGS.get('Zoning_Garage', {})
        # Compute frequency encoding for the (MS_Zoning, Garage_Type) combination
        freq_group = df.groupby(['MS_Zoning', 'Garage_Type']).size() / len(df)
        freq_map = freq_group.to_dict()
        # Create the new premium feature
        df['Zoning_Garage_Premium'] = df.apply(
            lambda row: row['Combined_Area'] * mapping.get((row['MS_Zoning'], row['Garage_Type']), 0) * freq_map.get((row['MS_Zoning'], row['Garage_Type']), 0),
            axis=1
        )
        # Drop the temporary Combined_Area column
        df = df.drop(columns=['Combined_Area'])
    
    # Create Total_Area and Log_Total_Area features as a simple transformation
    if all(col in df.columns for col in ['Gr_Liv_Area', 'Total_Bsmt_SF']):
        df['Total_Area'] = df['Gr_Liv_Area'].fillna(0) + df['Total_Bsmt_SF'].fillna(0)
        df['Log_Total_Area'] = np.log1p(df['Total_Area'])
    
    if 'Lot_Area' in df.columns:
        df['Lot_Area'] = df['Lot_Area'].fillna(df['Lot_Area'].median())
        df['Lot_Area_Bin'] = pd.qcut(df['Lot_Area'], q=4, labels=False, duplicates='drop')
    
    # Create binary indicator for presence of a fireplace and impute missing Fireplaces if needed
    if 'Fireplaces' in df.columns:
        df['Fireplaces'] = df['Fireplaces'].fillna(0)
        df['Has_Fireplace'] = (df['Fireplaces'] > 0).astype(int)
    
    # Select only numeric and boolean columns
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

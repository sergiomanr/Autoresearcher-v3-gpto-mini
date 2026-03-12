import pandas as pd

def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering with target and frequency encodings for categorical columns."""
    
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Fill missing values for categorical columns with a placeholder
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df[col] = df[col].fillna('Missing')

    # Frequency-style encodings to capture how common each category is
    freq_feature_data = {}
    for col in categorical_cols:
        freq_feature_data[f"{col}_freq"] = (
            df[col]
            .map(df[col].value_counts(normalize=True))
            .fillna(0)
        )

    if freq_feature_data:
        freq_features = pd.DataFrame(freq_feature_data, index=df.index)
        df = pd.concat([df, freq_features], axis=1)

    # Target encoding for categorical columns
    for col in categorical_cols:
        target_mean = df.groupby(col)['Sale_Price'].mean()
        df[col] = df[col].map(target_mean)

    # Select only numeric and boolean columns
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

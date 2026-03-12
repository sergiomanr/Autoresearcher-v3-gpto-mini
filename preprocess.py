import numpy as np
import pandas as pd

_SAVED_MAPPINGS: dict[str, dict] = {}


def _store_target_mapping(name: str, series: pd.Series) -> None:
    _SAVED_MAPPINGS[name] = series.to_dict()


def _map_with_saved(series: pd.Series, mapping_name: str, fallback: float) -> pd.Series:
    mapping = _SAVED_MAPPINGS.get(mapping_name, {})
    return series.map(mapping).fillna(fallback)


def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering with target and frequency encodings for categorical columns."""
    
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    global_sale_price_median = df['Sale_Price'].median()
    global_sale_price_mean = df['Sale_Price'].mean()
    
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

    agg_feature_data = {}
    for col in categorical_cols:
        cat_values = df[col]
        grouped = df.groupby(col)['Sale_Price']
        category_mean = grouped.mean()
        category_std = grouped.std().fillna(0)
        category_median = grouped.median()
        category_rank = category_mean.rank(method='dense', ascending=False)

        median_map = cat_values.map(category_median)
        median_map = median_map.fillna(global_sale_price_median).replace(0, 1)

        agg_feature_data[f"{col}_saleprice_rank"] = (
            cat_values.map(category_rank).fillna(0)
        )
        agg_feature_data[f"{col}_saleprice_std"] = (
            cat_values.map(category_std).fillna(0)
        )
        agg_feature_data[f"{col}_saleprice_median_ratio"] = (
            df['Sale_Price'] / median_map
        )

    if agg_feature_data:
        agg_features = pd.DataFrame(agg_feature_data, index=df.index)
        df = pd.concat([df, agg_features], axis=1)

    smoothing = 15
    smoothing_feature_data = {}
    n_rows = len(df)

    for col in categorical_cols:
        col_values = df[col]
        category_counts = col_values.value_counts()
        count_map = col_values.map(category_counts).fillna(0)
        category_mean = df.groupby(col)['Sale_Price'].mean()
        smooth_map = (
            (category_mean * category_counts) + (global_sale_price_mean * smoothing)
        ) / (category_counts + smoothing)
        smoothed_col = col_values.map(smooth_map).fillna(global_sale_price_mean)
        freq_ratio = (count_map / n_rows).fillna(0)

        smoothing_feature_data[f"{col}_te_smooth"] = smoothed_col
        smoothing_feature_data[f"{col}_freq_ratio"] = freq_ratio
        smoothing_feature_data[f"{col}_smooth_freq_interaction"] = (
            smoothed_col * freq_ratio
        )

    if smoothing_feature_data:
        smoothing_features = pd.DataFrame(smoothing_feature_data, index=df.index)
        df = pd.concat([df, smoothing_features], axis=1)

    combo_lookup = (
        df["MS_Zoning"].astype(str)
        .str.cat(df["House_Style"].astype(str), sep="__")
    )
    fallback_mean = _SAVED_MAPPINGS.get(
        "global_sale_price_mean", global_sale_price_mean
    )

    if "Sale_Price" in df.columns:
        _SAVED_MAPPINGS["global_sale_price_mean"] = global_sale_price_mean
        _store_target_mapping(
            "foundation_te_mean", df.groupby("Foundation")["Sale_Price"].mean()
        )
        _store_target_mapping(
            "zoning_house_style_te",
            df.groupby(combo_lookup)["Sale_Price"].mean(),
        )

    foundation_te = _map_with_saved(
        df["Foundation"], "foundation_te_mean", fallback_mean
    )
    zoning_house_te = _map_with_saved(
        combo_lookup, "zoning_house_style_te", fallback_mean
    )

    year_reference = 2025
    year_built = df["Year_Built"].fillna(year_reference)
    age = np.clip(year_reference - year_built, 0, None)
    foundation_decay = np.exp(-age / 80)

    bsmt_log = np.log1p(df["Total_Bsmt_SF"].fillna(0))
    lot_log = np.log1p(df["Lot_Area"].fillna(0))

    foundation_premium = foundation_te * (bsmt_log + 1) * foundation_decay
    zoning_house_lot_interaction = zoning_house_te * (lot_log + 1)
    foundation_zoning_interaction = foundation_premium * zoning_house_te

    engineered_feature_data = {
        "foundation_age_adjusted_premium": foundation_premium,
        "foundation_age_decay": foundation_decay,
        "zoning_house_style_te": zoning_house_te,
        "zoning_house_lot_interaction": zoning_house_lot_interaction,
        "foundation_zoning_interaction": foundation_zoning_interaction,
    }
    engineered_features = pd.DataFrame(engineered_feature_data, index=df.index)
    df = pd.concat([df, engineered_features], axis=1)

    # Target encoding for categorical columns
    for col in categorical_cols:
        target_mean = df.groupby(col)['Sale_Price'].mean()
        df[col] = df[col].map(target_mean)

    # Select only numeric and boolean columns
    df = df.select_dtypes(include=['number', 'bool'])
    
    return df

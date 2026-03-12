import time
import sys
import os
import shutil
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from autogluon.tabular import TabularPredictor

# --- Configuration ---
TARGET_COL = 'Sale_Price'      # UPDATE THIS if your target column name is different
DATA_PATH = 'train.csv'        # UPDATE THIS if your filename is different
AG_SAVE_PATH = 'ag_model_temp'
TIME_LIMIT = 300               # 5 minutes search limit (300 seconds)

def load_and_evaluate():
    start_time = time.time()
    
    # 1. Load Raw Data
    try:
        raw_df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"Error: Could not find data at {DATA_PATH}. Please ensure the file exists.")
        sys.exit(1)

    # 2. Import and Apply Agent's Preprocessing safely
    # We catch BaseException here because LLMs often make Syntax/Indentation errors
    try:
        import preprocess 
        processed_df = preprocess.apply_preprocessing(raw_df.copy())
    except BaseException as e:
        print(f"Crash during preprocessing (likely Syntax or Logic Error):\n{e}")
        sys.exit(1)

    # Sanity checks after preprocessing
    if TARGET_COL not in processed_df.columns:
        print(f"Crash: Preprocessing dropped the target column '{TARGET_COL}'.")
        sys.exit(1)
    
    # Ensure all features are numeric (Keeping strict rules for the Agent)
    X = processed_df.drop(columns=[TARGET_COL])
    non_numeric_cols = X.select_dtypes(exclude=[np.number, bool]).columns
    if len(non_numeric_cols) > 0:
        print(f"Crash: Agent failed to encode categorical columns: {list(non_numeric_cols)}")
        sys.exit(1)

    # 3. Handle the Target Metric (Log Transformation)
    # Optimize for RMSLE by log-transforming the target before AutoGluon training
    processed_df['Log_Sale_Price'] = np.log1p(processed_df[TARGET_COL])
    
    # Drop the original target so the model doesn't cheat
    train_data = processed_df.drop(columns=[TARGET_COL])

    # Clean up the old AutoGluon model folder so it trains fresh every loop
    if os.path.exists(AG_SAVE_PATH):
        shutil.rmtree(AG_SAVE_PATH)

    # 4. Train AutoGluon with GPU and Best Quality
    print(f"\n[+] Starting AutoGluon Training (Time Limit: {TIME_LIMIT}s)...")
    
    # Suppress warnings to keep terminal clean
    warnings.filterwarnings('ignore')

    predictor = TabularPredictor(
        label='Log_Sale_Price', 
        eval_metric='root_mean_squared_error',
        problem_type='regression',
        path=AG_SAVE_PATH,
        verbosity=0 # Keep logs silent so it doesn't flood your terminal
    )
    
    # Wrap in try/except in case AI creates features that cause OOM or Infinite Value crashes
    try:
        predictor.fit(
            train_data=train_data,
            presets='best_quality', # Triggers multi-layer stacking and bagging
            time_limit=TIME_LIMIT,  # 5 minute limit
            num_gpus='auto',        # Safer than hardcoding 1, AutoGluon will find the RTX 3090 automatically
            ag_args_ensemble={'fold_fitting_strategy': 'sequential_local'}  # <--- THIS IS THE FIX
        )
    except Exception as e:
        print(f"Crash during AutoGluon training (likely bad features causing OOM/Inf):\n{e}")
        sys.exit(1)

    # 5. Get Metrics using Out-Of-Fold (OOF) Predictions
    # Best_quality uses cross-validation under the hood. We grab those predictions here.
    oof_preds_log = predictor.predict_oof()
    
    # Inverse the log transformation (expm1) to get actual house prices back
    oof_preds_raw = np.expm1(oof_preds_log)
    
    # Ensure indices align just in case AutoGluon dropped any heavily corrupted rows
    y_raw = processed_df.loc[oof_preds_raw.index, TARGET_COL]

    # Calculate actual RMSE and RMSLE
    cv_rmse = np.sqrt(mean_squared_error(y_raw, oof_preds_raw))
    
    preds_clipped = np.clip(oof_preds_raw, 0, None)
    cv_rmsle = np.sqrt(mean_squared_log_error(y_raw, preds_clipped))
    
    # (AutoGluon handles fold splitting internally, so we just set std to 0.0 for formatting)
    fold_rmse_std = 0.0 
    
    execution_time = time.time() - start_time
    num_features = train_data.shape[1] - 1 # Exclude the log target

    # 6. Print Strictly Formatted Output (For driver.py to parse)
    print("\n---")
    print(f"cv_rmse:          {cv_rmse:.6f}")
    print(f"cv_rmsle:         {cv_rmsle:.6f}")
    print(f"fold_rmse_std:    {fold_rmse_std:.6f}")
    print(f"execution_time:   {execution_time:.1f}")
    print(f"num_features:     {num_features}")

    # 7. LOG TO TSV
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a') as f:
        if not file_exists:
            f.write("timestamp\tcv_rmse\tcv_rmsle\tnum_features\n")
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{cv_rmse:.6f}\t{cv_rmsle:.6f}\t{num_features}\n")

if __name__ == "__main__":
    load_and_evaluate()
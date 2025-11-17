#!/usr/bin/env python3
"""
End-to-end ML Pipeline: Data Loading → Preprocessing → Training → Evaluation

This script orchestrates the complete MLOps pipeline from raw data to trained model.

Usage:
    python scripts/run_full_pipeline.py

Requirements:
    - DVC configured (for data versioning)
    - MLflow tracking server (optional, will use local if not available)
    - All dependencies installed (pip install -r requirements.txt)

Author: Equipo 43
Date: November 2025
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Project.CargaDatos import CargaDatasets
from Project.Preprocesamiento import Preprocesamiento
from Project.Modelo import ModeloEspecial


def print_header(message: str, char: str = "="):
    """Print a formatted header."""
    width = 70
    print(f"\n{char * width}")
    print(f"{message:^{width}}")
    print(f"{char * width}\n")


def print_step(step_num: int, message: str):
    """Print a step indicator."""
    print(f"\n>>> Step {step_num}: {message}")
    print("-" * 60)


def main():
    """Execute the full ML pipeline."""

    print_header("MLOps Pipeline - Equipo 43", "=")
    print(f"Pipeline started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configuration
    DATA_RAW_DIR = project_root / "data" / "raw"
    DATA_PROCESSED_DIR = project_root / "data" / "processed"
    MODEL_DIR = project_root / "models"
    FILENAME_RAW = "power_tetouan_city_modified.csv"
    FILENAME_PROCESSED = "power_tetouan_city_processed.csv"
    MODEL_PATH = MODEL_DIR / "best_model_pipeline.joblib"

    # Ensure directories exist
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # =================================================================
        # STEP 1: DATA LOADING
        # =================================================================
        print_step(1, "Loading Raw Data")

        cargador = CargaDatasets(
            carpeta_raw=DATA_RAW_DIR,
            nombre_archivo=FILENAME_RAW
        )

        df_raw = cargador.leer()
        print(f"[OK] Loaded dataset: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")
        print(f"[OK] Source: {DATA_RAW_DIR / FILENAME_RAW}")

        # =================================================================
        # STEP 2: DATA PREPROCESSING
        # =================================================================
        print_step(2, "Preprocessing Data")

        print("  -> Executing preprocessing pipeline...")
        df_clean = Preprocesamiento.ejecutar(
            df_raw,
            ventana_mediana=25,
            eliminar_datetime=True
        )

        # Save processed data
        processed_path = DATA_PROCESSED_DIR / FILENAME_PROCESSED
        df_clean.to_csv(processed_path, index=False)
        print(f"\n[OK] Preprocessing complete: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
        print(f"[OK] Saved to: {processed_path}")

        # Display info
        print(f"\n  Missing values after preprocessing:")
        missing = df_clean.isnull().sum()
        if missing.sum() == 0:
            print("  [OK] No missing values!")
        else:
            print(missing[missing > 0])

        # =================================================================
        # STEP 3: MODEL TRAINING
        # =================================================================
        print_step(3, "Training Machine Learning Model")

        # Initialize model trainer
        modelo = ModeloEspecial(
            model_path=str(MODEL_PATH),
            exp="Full_Pipeline_Execution",
            run_nm=f"AutoRun_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Define the best model (based on previous experiments)
        print("  -> Using Gradient Boost Regressor")
        print("     - n_estimators: 600")
        print("     - learning_rate: 0.1")
        print("     - max_depth: 5")
        print("     - min_samples_split: 5")
        print("     - min_samples_leaf: 3")
        print("     - random_state: 42")

        rf_model = GradientBoostingRegressor(
            n_estimators=600, learning_rate=0.1, max_depth=5,
            min_samples_split=5, min_samples_leaf=3, random_state=42
        )

        print(f"\n  -> Training model...")
        x_test, y_test = modelo.train_and_save(df=df_clean, model=rf_model)

        print(f"\n[OK] Model training complete!")
        print(f"[OK] Model saved to: {MODEL_PATH}")
        print(f"[OK] Test set size: {len(x_test):,} samples")

        # =================================================================
        # STEP 4: MODEL EVALUATION
        # =================================================================
        print_step(4, "Evaluating Model Performance")

        # Make predictions on test set
        y_pred = modelo.predict(x_test)

        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mae = np.mean(np.abs(y_test - y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        print("\n  Model Performance Metrics:")
        print("  " + "-" * 50)
        print(f"  RMSE (Root Mean Squared Error):  {rmse:>12.2f} kW")
        print(f"  MAE  (Mean Absolute Error):      {mae:>12.2f} kW")
        print(f"  MAPE (Mean Absolute % Error):    {mape:>12.2f} %")
        print(f"  R²   (Coefficient of Determination): {r2:>8.4f}")
        print("  " + "-" * 50)

        # Performance evaluation against targets
        print("\n  Performance vs. Target Metrics:")
        target_rmse = 4000
        target_mape = 12
        target_r2 = 0.90

        rmse_status = "[PASS]" if rmse < target_rmse else "[FAIL]"
        mape_status = "[PASS]" if mape < target_mape else "[FAIL]"
        r2_status = "[PASS]" if r2 > target_r2 else "[FAIL]"

        print(f"  RMSE < {target_rmse} kW:     {rmse_status}")
        print(f"  MAPE < {target_mape}%:        {mape_status}")
        print(f"  R² > {target_r2}:          {r2_status}")

        # =================================================================
        # STEP 5: PIPELINE SUMMARY
        # =================================================================
        print_header("Pipeline Execution Summary", "-")

        print("[SUCCESS] All steps completed successfully!\n")
        print("Pipeline outputs:")
        print(f"  1. Processed dataset: {processed_path}")
        print(f"  2. Trained model:     {MODEL_PATH}")
        print(f"  3. Model metrics:     Logged to MLflow")

        print("\n" + "=" * 70)
        print(f"Pipeline completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        return 0

    except FileNotFoundError as e:
        print(f"\n[ERROR] Required file not found - {e}")
        print("   Make sure to run 'dvc pull' to download the dataset.")
        return 1

    except Exception as e:
        print(f"\n[ERROR] Pipeline execution failed!")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

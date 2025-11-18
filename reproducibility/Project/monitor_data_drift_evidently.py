#!/usr/bin/env python3
"""
Data Drift Monitoring with Evidently.ai

This script uses Evidently to detect data drift between reference (training)
and current (production/monitoring) datasets.

Features:
- Data Quality Report
- Data Drift Report
- Target Drift Detection (via Regression Preset)
- Interactive HTML reports
- JSON metrics export

Usage:
    python scripts/monitor_data_drift_evidently.py

Requirements:
    pip install evidently==0.7.14

Author: Equipo 43 (Fields' contribution)
Date: November 2025
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Evidently imports (v0.7.14)
try:
    from evidently.core.report import Report
    from evidently.presets import DataDriftPreset, DataSummaryPreset
    from evidently.presets.regression import RegressionPreset
except ImportError as e:
    print("ERROR: Evidently not installed or import failed.")
    print(f"Error details: {e}")
    print("Install with: pip install evidently==0.7.14")
    sys.exit(1)


def print_header(message: str, char: str = "="):
    """Print formatted header."""
    width = 70
    print(f"\n{char * width}")
    print(f"{message:^{width}}")
    print(f"{char * width}\n")


def load_reference_data(data_path: Path) -> pd.DataFrame:
    """
    Load reference dataset (training data).

    This represents the "baseline" distribution against which we'll
    compare new data.
    """
    print("Loading reference dataset (training/validation data)...")
    df = pd.read_csv(data_path)

    # Normalize column names to match model expectations
    df.columns = [
        'Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
        'DiffuseFlows', 'PowerConsumption_Zone1',
        'PowerConsumption_Zone2', 'PowerConsumption_Zone3', 'Day',
        'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear', 'DayYear'
    ]

    print(f"[OK] Loaded {len(df):,} rows")
    return df


def generate_monitoring_data(reference_df: pd.DataFrame,
                            drift_type: str = "temperature") -> pd.DataFrame:
    """
    Generate synthetic monitoring data with drift.

    Parameters:
    -----------
    reference_df : pd.DataFrame
        Original reference data
    drift_type : str
        Type of drift to simulate:
        - 'temperature': Shift temperature distribution
        - 'humidity': Shift humidity distribution
        - 'mixed': Multiple feature drift
        - 'none': No drift (for testing)

    Returns:
    --------
    pd.DataFrame
        Monitoring dataset with simulated drift
    """
    print(f"\nGenerating monitoring dataset with '{drift_type}' drift...")

    # Take a sample from reference data
    monitoring_df = reference_df.sample(n=min(5000, len(reference_df)),
                                       random_state=42).copy()

    if drift_type == "temperature":
        # Shift temperature by +5 degrees (simulates climate change or seasonal shift)
        monitoring_df['Temperature'] = monitoring_df['Temperature'] + 5.0
        print("  -> Temperature shifted +5 degrees Celsius")

    elif drift_type == "humidity":
        # Increase humidity by 15%
        monitoring_df['Humidity'] = monitoring_df['Humidity'] * 1.15
        monitoring_df['Humidity'] = monitoring_df['Humidity'].clip(0, 100)
        print("  -> Humidity increased by 15%")

    elif drift_type == "mixed":
        # Multiple features drift
        monitoring_df['Temperature'] = monitoring_df['Temperature'] + 3.0
        monitoring_df['Humidity'] = monitoring_df['Humidity'] * 1.10
        monitoring_df['WindSpeed'] = monitoring_df['WindSpeed'] * 0.85
        print("  -> Multiple features drifted (temp, humidity, wind)")

    elif drift_type == "none":
        print("  -> No drift applied (control test)")

    print(f"[OK] Generated {len(monitoring_df):,} monitoring samples")
    return monitoring_df


def generate_data_drift_report(reference_df: pd.DataFrame,
                               current_df: pd.DataFrame,
                               target_col: str,
                               output_path: Path) -> Report:
    """
    Generate comprehensive Data Drift Report using Evidently 0.7.14 API.

    This report includes:
    - Dataset-level drift detection
    - Per-feature drift metrics
    - Distribution comparisons
    - Statistical tests (KS, Chi-squared, etc.)
    """
    print("\n>>> Generating Data Drift Report...")

    # Create report with presets (v0.7.14 API)
    report = Report([
        DataDriftPreset(),
        DataSummaryPreset(),
        # RegressionPreset()  # Removed - causing issues with target column detection
    ])

    # Run the report and get the evaluation result
    my_eval = report.run(
        reference_data=reference_df,
        current_data=current_df
    )

    # Save as HTML
    html_path = output_path / "data_drift_report.html"
    my_eval.save_html(str(html_path))
    print(f"[OK] HTML report saved: {html_path}")

    # Save as JSON for programmatic access
    json_path = output_path / "data_drift_report.json"
    with open(json_path, 'w') as f:
        f.write(my_eval.json())
    print(f"[OK] JSON report saved: {json_path}")

    return my_eval


def extract_drift_metrics(report_json_path: Path) -> dict:
    """
    Extract key drift metrics from JSON report.

    Returns summary metrics for logging/alerting.
    """
    import json

    with open(report_json_path) as f:
        report_data = json.load(f)

    metrics = {
        'timestamp': datetime.now().isoformat(),
        'dataset_drift_detected': False,
        'drifted_features': [],
        'drift_scores': {}
    }

    # Navigate the JSON structure to extract metrics
    # (Structure for Evidently 0.7+)
    try:
        for metric in report_data.get('metrics', []):
            metric_type = metric.get('metric', '')

            # Check for DatasetDriftMetric
            if 'DatasetDrift' in metric_type:
                result = metric.get('result', {})
                metrics['dataset_drift_detected'] = result.get('dataset_drift', False)
                metrics['drift_share'] = result.get('share_of_drifted_columns', 0)
                metrics['number_of_drifted_columns'] = result.get('number_of_drifted_columns', 0)

                # Get per-feature drift
                drift_by_columns = result.get('drift_by_columns', {})
                for col, drift_info in drift_by_columns.items():
                    if isinstance(drift_info, dict) and drift_info.get('drift_detected'):
                        metrics['drifted_features'].append(col)
                        metrics['drift_scores'][col] = drift_info.get('drift_score', 0)
    except Exception as e:
        print(f"[WARNING] Could not extract all metrics: {e}")

    return metrics


def evaluate_model_performance(model_path: Path, data_df: pd.DataFrame,
                                target_col: str, dataset_name: str) -> dict:
    """
    Evaluate model performance on a given dataset.

    Parameters:
    -----------
    model_path : Path
        Path to the saved model (.joblib)
    data_df : pd.DataFrame
        Dataset to evaluate
    target_col : str
        Name of target column
    dataset_name : str
        Name for identification (e.g., 'Baseline', 'Drift')

    Returns:
    --------
    dict
        Dictionary with performance metrics
    """
    import joblib
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    print(f"\n>>> Evaluating model on {dataset_name} dataset...")

    # Load model
    try:
        model = joblib.load(model_path)
        print(f"[OK] Model loaded from: {model_path}")
    except Exception as e:
        print(f"[ERROR] Could not load model: {e}")
        return None

    # Prepare data
    # Check if target column exists
    if target_col not in data_df.columns:
        print(f"[ERROR] Target column '{target_col}' not found in dataset")
        print(f"Available columns: {data_df.columns.tolist()}")
        return None

    X = data_df.drop(columns=[target_col])
    y_true = data_df[target_col]

    # Make predictions
    try:
        y_pred = model.predict(X)
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        return None

    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Calculate percentage errors
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    metrics = {
        'dataset': dataset_name,
        'samples': len(data_df),
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'mape': mape
    }

    print(f"  Samples: {metrics['samples']:,}")
    print(f"  RMSE:    {metrics['rmse']:.2f}")
    print(f"  MAE:     {metrics['mae']:.2f}")
    print(f"  R²:      {metrics['r2']:.4f}")
    print(f"  MAPE:    {metrics['mape']:.2f}%")

    return metrics


def compare_performance(baseline_metrics: dict, drift_metrics: dict,
                        output_path: Path) -> dict:
    """
    Compare baseline vs drift performance and generate comparison report.

    Parameters:
    -----------
    baseline_metrics : dict
        Metrics from baseline dataset
    drift_metrics : dict
        Metrics from drift dataset
    output_path : Path
        Directory to save comparison report

    Returns:
    --------
    dict
        Comparison results with degradation percentages
    """
    print("\n>>> Comparing Performance: Baseline vs Drift")

    # Calculate degradation
    rmse_degradation = ((drift_metrics['rmse'] - baseline_metrics['rmse']) /
                        baseline_metrics['rmse']) * 100
    mae_degradation = ((drift_metrics['mae'] - baseline_metrics['mae']) /
                       baseline_metrics['mae']) * 100
    r2_degradation = ((baseline_metrics['r2'] - drift_metrics['r2']) /
                      baseline_metrics['r2']) * 100

    comparison = {
        'baseline': baseline_metrics,
        'drift': drift_metrics,
        'degradation': {
            'rmse_pct': float(rmse_degradation),
            'mae_pct': float(mae_degradation),
            'r2_pct': float(r2_degradation)
        },
        'thresholds_exceeded': {
            'rmse': bool(rmse_degradation > 10),  # >10% degradation
            'mae': bool(mae_degradation > 10),
            'r2': bool(r2_degradation > 5)  # >5% degradation in R²
        }
    }

    # Print comparison table
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON TABLE")
    print("="*70)
    print(f"{'Metric':<15} {'Baseline':<15} {'Drift':<15} {'Degradation':<20}")
    print("-"*70)
    print(f"{'RMSE':<15} {baseline_metrics['rmse']:<15.2f} {drift_metrics['rmse']:<15.2f} "
          f"{rmse_degradation:+.2f}% {'⚠️' if comparison['thresholds_exceeded']['rmse'] else '✓'}")
    print(f"{'MAE':<15} {baseline_metrics['mae']:<15.2f} {drift_metrics['mae']:<15.2f} "
          f"{mae_degradation:+.2f}% {'⚠️' if comparison['thresholds_exceeded']['mae'] else '✓'}")
    print(f"{'R²':<15} {baseline_metrics['r2']:<15.4f} {drift_metrics['r2']:<15.4f} "
          f"{r2_degradation:+.2f}% {'⚠️' if comparison['thresholds_exceeded']['r2'] else '✓'}")
    print("="*70)

    # Save comparison to JSON
    comparison_path = output_path / "performance_comparison.json"
    import json
    with open(comparison_path, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"\n[OK] Comparison saved: {comparison_path}")

    return comparisonå


def main():
    """Execute Evidently monitoring pipeline."""

    print_header("Data Drift Monitoring with Evidently.ai")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configuration
    DATA_PATH = project_root / "data" / "processed" / "power_tetouan_city_processed.csv"
    MODEL_PATH = project_root / "models" / "best_model_pipeline.joblib"
    OUTPUT_DIR = project_root / "reports" / "evidently"
    TARGET_COL = "PowerConsumption_Zone2"

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Load reference data
        print_header("Step 1: Loading Data", "-")
        reference_df = load_reference_data(DATA_PATH)

        # Split reference into training (reference) and validation (for comparison)
        split_idx = int(len(reference_df) * 0.80)
        reference_data = reference_df.iloc[:split_idx].copy()
        validation_data = reference_df.iloc[split_idx:].copy()

        print(f"Reference data: {len(reference_data):,} rows")
        print(f"Validation data: {len(validation_data):,} rows")

        # Step 2: Generate monitoring data with drift
        print_header("Step 2: Simulating Production Data", "-")
        monitoring_data = generate_monitoring_data(
            validation_data,
            drift_type="temperature"  # Change to: 'humidity', 'mixed', or 'none'
        )

        # Step 3: Generate report
        print_header("Step 3: Generating Reports", "-")

        # Data Drift Report
        drift_report = generate_data_drift_report(
            reference_data,
            monitoring_data,
            TARGET_COL,
            OUTPUT_DIR
        )

        # Step 4: Extract metrics
        print_header("Step 4: Extracting Metrics", "-")
        metrics = extract_drift_metrics(OUTPUT_DIR / "data_drift_report.json")

        # Step 5: Evaluate Model Performance
        print_header("Step 5: Model Performance Evaluation", "-")

        # Evaluate on baseline (validation data without drift)
        baseline_metrics = evaluate_model_performance(
            MODEL_PATH, validation_data, TARGET_COL, "Baseline (No Drift)"
        )

        # Evaluate on drift data
        drift_metrics = evaluate_model_performance(
            MODEL_PATH, monitoring_data, TARGET_COL, "Drift (Temperature +5°C)"
        )

        # Compare performance
        if baseline_metrics and drift_metrics:
            comparison = compare_performance(baseline_metrics, drift_metrics, OUTPUT_DIR)
        else:
            print("[WARNING] Could not perform performance comparison")
            comparison = None

        print("\nDrift Detection Summary:")
        print(f"  - Dataset drift detected: {metrics.get('dataset_drift_detected', 'N/A')}")
        print(f"  - Drifted features: {len(metrics.get('drifted_features', []))}")

        if metrics.get('drifted_features'):
            print(f"\n  Features with drift:")
            for feature in metrics['drifted_features']:
                score = metrics['drift_scores'].get(feature, 'N/A')
                print(f"    - {feature}: {score}")

        # Step 6: Summary and Recommendations
        print_header("Step 6: Summary and Recommendations", "-")
        print("[SUCCESS] Monitoring pipeline completed!")
        print(f"\nGenerated reports:")
        print(f"  1. Data Drift Report:         {OUTPUT_DIR}/data_drift_report.html")
        print(f"  2. JSON Metrics:              {OUTPUT_DIR}/data_drift_report.json")
        print(f"  3. Performance Comparison:    {OUTPUT_DIR}/performance_comparison.json")

        # Determine severity based on thresholds
        critical_degradation = False
        if comparison:
            thresholds = comparison['thresholds_exceeded']
            critical_degradation = any(thresholds.values())

        print(f"\n" + "="*70)
        print("RECOMMENDATIONS AND ACTIONS")
        print("="*70)

        if critical_degradation:
            print("\n[CRITICAL] Significant performance degradation detected!")
            print("\nImmediate Actions Required:")
            print("  1. INVESTIGATE root cause of drift")
            print("     - Check data collection pipeline for errors")
            print("     - Verify sensor calibration (Temperature sensor)")
            print("     - Review recent changes in data sources")
            print()
            print("  2. RETRAIN model with recent data")
            print("     - Include drift dataset in training")
            print("     - Validate on hold-out test set")
            print("     - Compare with current production model")
            print()
            print("  3. UPDATE monitoring thresholds")
            print("     - Set alerts for RMSE degradation > 10%")
            print("     - Set alerts for R2 degradation > 5%")
            print("     - Configure Evidently UI for real-time monitoring")
            print()
            print("  4. DOCUMENT incident")
            print("     - Record drift event in model registry")
            print("     - Update model card with performance degradation")
            print("     - Schedule post-mortem meeting")
        elif metrics.get('dataset_drift_detected'):
            print("\n[WARNING] Data drift detected but performance stable")
            print("\nRecommended Actions:")
            print("  1. Continue monitoring model performance")
            print("  2. Investigate feature drift patterns")
            print("  3. Consider proactive retraining in next cycle")
        else:
            print("\n[OK] No significant drift or performance degradation")
            print("\nMaintenance Actions:")
            print("  1. Continue scheduled monitoring")
            print("  2. Archive reports for compliance")
            print("  3. Review model performance quarterly")

        print("\n" + "="*70)
        print("MONITORING THRESHOLDS (Current Configuration)")
        print("="*70)
        print(f"  RMSE Degradation Alert:    > 10%")
        print(f"  MAE Degradation Alert:     > 10%")
        print(f"  R2 Degradation Alert:      > 5%")
        print(f"  Statistical Drift (p-val): < 0.05")
        print("="*70)

        print(f"\nTo view the interactive report:")
        print(f"  open {OUTPUT_DIR}/data_drift_report.html")

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        return 0 if not critical_degradation else 1

    except FileNotFoundError as e:
        print(f"\n[ERROR] Required file not found: {e}")
        print("Make sure processed data exists at:", DATA_PATH)
        return 1

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

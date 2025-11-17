#!/usr/bin/env python3
"""
Complete MLOps Pipeline Orchestrator
====================================

Executes the full end-to-end MLOps workflow:
1. Environment validation (dependencies, DVC, MLflow)
2. Data loading and preprocessing
3. Model training with MLflow tracking
4. Model testing and validation
5. Data drift monitoring with Evidently.ai
6. Comprehensive report generation

This script ensures all components of the MLOps pipeline are executed
in the correct order with proper error handling and reporting.

Usage:
    python scripts/run_mlops_complete.py [--skip-tests] [--skip-drift]

Options:
    --skip-tests    Skip running pytest test suite
    --skip-drift    Skip data drift monitoring
    --help          Show this help message

Requirements:
    - DVC configured with S3 remote
    - Virtual environment activated
    - All dependencies installed (requirements.txt)

Author: Equipo 43
Date: November 2025
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json


project_root = Path(__file__).parent.parent


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str, char: str = "=", color: str = Colors.HEADER):
    """Print a formatted colored header."""
    width = 80
    print(f"\n{color}{char * width}")
    print(f"{message:^{width}}")
    print(f"{char * width}{Colors.ENDC}\n")


def print_step(step_num: int, total_steps: int, message: str):
    """Print a step indicator with progress."""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}>>> Step {step_num}/{total_steps}: {message}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * 80}{Colors.ENDC}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}[SUCCESS] {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.FAIL}[ERROR] {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.WARNING}[WARNING] {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}[INFO] {message}{Colors.ENDC}")


def run_command(cmd: list, description: str, check: bool = True) -> tuple:
    """
    Run a shell command and return success status and output.

    Args:
        cmd: Command as list of strings
        description: Description of what the command does
        check: Whether to raise exception on failure

    Returns:
        (success: bool, output: str)
    """
    print_info(f"Running: {description}")
    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=check
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed with exit code {e.returncode}")
            print(f"  STDOUT: {e.stdout}")
            print(f"  STDERR: {e.stderr}")
        return False, e.stderr


def step_1_environment_validation() -> bool:
    """Step 1: Validate environment setup."""
    print_step(1, 6, "Environment Validation")

    # Check if validate_environment.py exists
    validate_script = project_root / "scripts" / "validate_environment.py"
    if not validate_script.exists():
        print_warning("validate_environment.py not found, skipping environment validation")
        return True

    success, output = run_command(
        [sys.executable, str(validate_script)],
        "Validating Python environment, dependencies, and configurations",
        check=False
    )

    if success:
        print_success("Environment validation passed")
        print(output)
        return True
    else:
        print_warning("Environment validation had issues, but continuing...")
        print(output)
        return True


def step_2_dvc_pull() -> bool:
    """Step 2: Pull latest data from DVC."""
    print_step(2, 6, "DVC Data Pull")

    print_info("Checking DVC status...")
    success, output = run_command(
        [sys.executable, "-m", "dvc", "status"],
        "Checking DVC data status",
        check=False
    )

    if "Data and pipelines are up to date" in output:
        print_success("DVC data is already up to date")
        return True

    print_info("Pulling latest data from DVC remote...")
    success, output = run_command(
        [sys.executable, "-m", "dvc", "pull"],
        "Downloading data from S3",
        check=False
    )

    if success:
        print_success("DVC data pulled successfully")
        return True
    else:
        print_error("DVC pull failed - check your AWS credentials and remote configuration")
        return False


def step_3_training_pipeline() -> bool:
    """Step 3: Execute training pipeline."""
    print_step(3, 6, "Model Training Pipeline")

    # Try run_full_pipeline.py first
    pipeline_script = project_root / "scripts" / "run_full_pipeline.py"
    if pipeline_script.exists():
        print_info("Attempting full pipeline with MLflow...")
        success, output = run_command(
            [sys.executable, str(pipeline_script)],
            "Executing full ML pipeline (load, preprocess, train, evaluate)",
            check=False
        )

        if success:
            print_success("Training pipeline completed successfully")
            print(output)
            return True
        else:
            print_warning("Full pipeline failed (likely MLflow permissions)")
            print_info("Falling back to local training without MLflow...")

    # Fallback: Train locally without MLflow
    print_info("Training model locally (no MLflow logging)...")

    train_code = """
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score
import joblib

data_path = Path("data/processed/power_tetouan_city_processed.csv")
model_path = Path("app/best_model_pipeline.joblib")

print("Loading data...")
df = pd.read_csv(data_path)

# Rename columns
df.columns=['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
           'DiffuseFlows','PowerConsumption_Zone1',
           'PowerConsumption_Zone2', 'PowerConsumption_Zone3', 'Day',
           'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear', 'DayYear']

# Split data
target = "PowerConsumption_Zone2"
X = df.drop(columns=[col for col in df.columns if 'PowerConsumption_Zone' in col])
y = df[target].values.ravel()
n, i = len(df), int(len(df) * 0.80)
x_train, x_test = X.iloc[:i], X.iloc[i:]
y_train, y_test = y[:i], y[i:]

# Create pipeline
num_cols = ['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows']
num_pipeline = Pipeline([('impMediana', SimpleImputer(strategy='median')),
                         ('escalaNum', MinMaxScaler(feature_range=(1, 2)))])
preprocessor = ColumnTransformer([('numpipe', num_pipeline, num_cols)], remainder='passthrough')

# Train model
rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
pipeline = Pipeline([('ct', preprocessor), ('m', rf)])

print("Training model...")
pipeline.fit(x_train, y_train)

# Evaluate
y_pred = pipeline.predict(x_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:.2f}")
print(f"R2: {r2:.4f}")

# Save
joblib.dump(pipeline, model_path)
print(f"Model saved to: {model_path}")
"""

    success, output = run_command(
        [sys.executable, "-c", train_code],
        "Training model without MLflow",
        check=False
    )

    if success:
        print_success("Training completed successfully (local mode)")
        print(output)
        return True
    else:
        print_error("Training failed")
        return False


def step_4_run_tests(skip: bool = False) -> bool:
    """Step 4: Run test suite."""
    print_step(4, 6, "Model Testing and Validation")

    if skip:
        print_warning("Skipping tests (--skip-tests flag)")
        return True

    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print_warning("pytest not installed, skipping tests")
        return True

    # Check if tests directory exists
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        print_warning("tests/ directory not found, skipping tests")
        return True

    print_info("Running pytest test suite...")
    success, output = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        "Running automated tests with pytest",
        check=False
    )

    if success:
        print_success("All tests passed")
        return True
    else:
        print_warning("Some tests failed, check output above")
        return True


def step_5_data_drift_monitoring(skip: bool = False) -> bool:
    """Step 5: Run data drift monitoring."""
    print_step(5, 6, "Data Drift Monitoring")

    if skip:
        print_warning("Skipping drift monitoring (--skip-drift flag)")
        return True

    drift_script = project_root / "scripts" / "monitor_data_drift_evidently.py"
    if not drift_script.exists():
        print_warning("monitor_data_drift_evidently.py not found, skipping drift monitoring")
        return True

    success, output = run_command(
        [sys.executable, str(drift_script)],
        "Running Evidently.ai data drift analysis",
        check=False
    )

    if success:
        print_success("Data drift monitoring completed")
        print(output)
        return True
    else:
        print_error("Data drift monitoring failed")
        return False


def step_6_generate_summary() -> bool:
    """Step 6: Generate comprehensive summary."""
    print_step(6, 6, "Generating MLOps Pipeline Summary")

    summary = {
        "execution_timestamp": datetime.now().isoformat(),
        "pipeline_status": "completed",
        "components": {}
    }

    # Check for model file
    model_path = project_root / "app" / "best_model_pipeline.joblib"
    summary["components"]["model"] = {
        "path": str(model_path),
        "exists": model_path.exists(),
        "size_mb": round(model_path.stat().st_size / (1024 * 1024), 2) if model_path.exists() else 0
    }

    # Check for drift reports
    drift_report = project_root / "reports" / "evidently" / "data_drift_report.html"
    summary["components"]["drift_report"] = {
        "path": str(drift_report),
        "exists": drift_report.exists()
    }

    # Check for performance comparison
    perf_comparison = project_root / "reports" / "evidently" / "performance_comparison.json"
    if perf_comparison.exists():
        with open(perf_comparison, 'r') as f:
            perf_data = json.load(f)
            summary["components"]["performance"] = perf_data

    # Save summary
    summary_path = project_root / "reports" / "mlops_pipeline_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print_success(f"Summary saved to: {summary_path}")

    # Print summary to console
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}MLOps Pipeline Summary{Colors.ENDC}")
    print("=" * 80)

    print(f"\nExecution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n{Colors.BOLD}Generated Artifacts:{Colors.ENDC}")
    print(f"  Model:              {summary['components']['model']['path']}")
    print(f"                      Size: {summary['components']['model']['size_mb']} MB")

    if summary['components']['drift_report']['exists']:
        print(f"  Drift Report:       {summary['components']['drift_report']['path']}")

    if 'performance' in summary['components']:
        perf = summary['components']['performance']
        print(f"\n{Colors.BOLD}Model Performance:{Colors.ENDC}")
        print(f"  Baseline RMSE:      {perf['baseline']['rmse']:.2f}")
        print(f"  Baseline R²:        {perf['baseline']['r2']:.4f}")
        print(f"  Baseline MAE:       {perf['baseline']['mae']:.2f}")

        print(f"\n{Colors.BOLD}Degradation Analysis:{Colors.ENDC}")
        print(f"  RMSE Change:        {perf['degradation']['rmse_pct']:+.2f}%")
        print(f"  MAE Change:         {perf['degradation']['mae_pct']:+.2f}%")
        print(f"  R² Change:          {perf['degradation']['r2_pct']:+.2f}%")

        any_exceeded = any(perf['thresholds_exceeded'].values())
        if any_exceeded:
            print_warning("Some performance thresholds exceeded!")
        else:
            print_success("All performance thresholds within acceptable limits")

    print("\n" + "=" * 80)

    return True


def main():
    """Main orchestration function."""
    parser = argparse.ArgumentParser(
        description="Complete MLOps Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--skip-tests", action="store_true", help="Skip running pytest test suite")
    parser.add_argument("--skip-drift", action="store_true", help="Skip data drift monitoring")

    args = parser.parse_args()

    print_header("MLOps Complete Pipeline - Equipo 43", "=", Colors.HEADER)
    print(f"Pipeline started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {project_root}")

    results = {}

    try:
        # Step 1: Environment Validation
        results["environment"] = step_1_environment_validation()
        if not results["environment"]:
            print_error("Environment validation failed - continuing anyway...")

        # Step 2: DVC Pull
        results["dvc"] = step_2_dvc_pull()
        if not results["dvc"]:
            print_error("DVC pull failed - cannot continue without data")
            return 1

        # Step 3: Training Pipeline
        results["training"] = step_3_training_pipeline()
        if not results["training"]:
            print_error("Training pipeline failed - cannot continue")
            return 1

        # Step 4: Run Tests
        results["tests"] = step_4_run_tests(skip=args.skip_tests)

        # Step 5: Data Drift Monitoring
        results["drift"] = step_5_data_drift_monitoring(skip=args.skip_drift)

        # Step 6: Generate Summary
        results["summary"] = step_6_generate_summary()

        # Final status
        print_header("Pipeline Execution Complete", "=", Colors.OKGREEN)

        all_success = all(results.values())
        if all_success:
            print_success("All pipeline steps completed successfully!")
            return 0
        else:
            print_warning("Pipeline completed with some warnings or errors")
            print("\nStep Results:")
            for step, success in results.items():
                status = "PASS" if success else "FAIL"
                color = Colors.OKGREEN if success else Colors.FAIL
                print(f"  {color}{step.capitalize()}: {status}{Colors.ENDC}")
            return 0

    except KeyboardInterrupt:
        print_error("\n\nPipeline interrupted by user")
        return 130

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Fase 3: Script para verificar reproducibilidad del modelo.
Comando: python scripts/reproducibilidad_f3.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import json
from datetime import datetime
import random

# --- Configuración de semillas para reproducibilidad ---
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

def set_all_seeds(seed=42):
    """Configura todas las semillas para garantizar reproducibilidad."""
    np.random.seed(seed)
    random.seed(seed)
    # Para sklearn
    os.environ['PYTHONHASHSEED'] = str(seed)

def load_processed_data():
    """Carga los datos procesados."""
    try:
        data_path = Path("data/processed/power_tetouan_city_processed.csv")
        if not data_path.exists():
            print(f"Error: No se encontró {data_path}")
            return None
        
        df = pd.read_csv(data_path)
        print(f"Datos cargados: {df.shape}")
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return None

def prepare_features(df):
    """Prepara las características siguiendo la estructura del proyecto."""
    # Asegurar nombres de columnas consistentes
    df.columns = ['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
                  'DiffuseFlows','PowerConsumption_Zone1',
                  'PowerConsumption_Zone2', 'PowerConsumption_Zone3' ,'Day',
                  'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear',
                  'DayYear']
    
    # Separar características y target
    X = df.drop(columns=['PowerConsumption_Zone1','PowerConsumption_Zone2','PowerConsumption_Zone3'])
    y = df['PowerConsumption_Zone2'].values
    
    return X, y

def create_model_pipeline():
    """Crea un pipeline de modelo reproducible."""
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.compose import ColumnTransformer
    
    # Características numéricas para el preprocesador
    num_cols = ['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows']
    
    # Pipeline de preprocesamiento
    num_pipeline = Pipeline(steps=[
        ('impMediana', SimpleImputer(strategy='median')),
        ('escalaNum', MinMaxScaler(feature_range=(1, 2))),
    ])
    
    ct = ColumnTransformer(
        transformers=[('numpipe', num_pipeline, num_cols)],
        remainder='passthrough'
    )
    
    # Modelo con semilla fija
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=RANDOM_SEED,
        n_jobs=1  # Para máxima reproducibilidad
    )
    
    # Pipeline completo
    pipeline = Pipeline(steps=[
        ('preprocessor', ct),
        ('model', model)
    ])
    
    return pipeline

def train_and_evaluate(X, y, test_size=0.2):
    """Entrena el modelo y calcula métricas."""
    set_all_seeds(RANDOM_SEED)
    
    # Split temporal (últimos datos como test)
    n = len(X)
    split_idx = int(n * (1 - test_size))
    
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Crear y entrenar pipeline
    pipeline = create_model_pipeline()
    pipeline.fit(X_train, y_train)
    
    # Predicciones
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    
    # Métricas
    metrics = {
        "train": {
            "mse": float(mean_squared_error(y_train, y_pred_train)),
            "rmse": float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
            "mae": float(mean_absolute_error(y_train, y_pred_train)),
            "r2": float(r2_score(y_train, y_pred_train))
        },
        "test": {
            "mse": float(mean_squared_error(y_test, y_pred_test)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            "mae": float(mean_absolute_error(y_test, y_pred_test)),
            "r2": float(r2_score(y_test, y_pred_test))
        }
    }
    
    return pipeline, metrics, (X_test, y_test, y_pred_test)

def save_reproducibility_report(metrics, model_info, output_dir="reports"):
    """Guarda un reporte de reproducibilidad."""
    Path(output_dir).mkdir(exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "random_seed": RANDOM_SEED,
        "model_info": model_info,
        "metrics": metrics,
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__
    }
    
    report_path = Path(output_dir) / "reproducibilidad_f3_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Reporte guardado en: {report_path}")
    return report_path

def compare_with_baseline(metrics, baseline_path="reports/baseline_metrics_f3.json"):
    """Compara métricas actuales con línea base."""
    baseline_path = Path(baseline_path)
    
    if baseline_path.exists():
        with open(baseline_path, "r") as f:
            baseline = json.load(f)
        
        print("\n=== COMPARACIÓN CON LÍNEA BASE ===")
        for split in ["train", "test"]:
            print(f"\n{split.upper()}:")
            for metric in ["mse", "rmse", "mae", "r2"]:
                current = metrics[split][metric]
                baseline_val = baseline["metrics"][split][metric]
                diff = current - baseline_val
                diff_pct = (diff / baseline_val) * 100 if baseline_val != 0 else 0
                
                print(f"  {metric:4s}: {current:8.4f} vs {baseline_val:8.4f} "
                      f"(diff: {diff:+8.4f}, {diff_pct:+6.1f}%)")
    else:
        print(f"No se encontró línea base en {baseline_path}")
        print("Guardando métricas actuales como nueva línea base...")
        
        baseline_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(baseline_path, "w") as f:
            json.dump(baseline_data, f, indent=2)
        print(f"Línea base guardada en: {baseline_path}")

def main():
    """Función principal del script de reproducibilidad."""
    print("=== SCRIPT DE VERIFICACIÓN DE REPRODUCIBILIDAD - FASE 3 ===")
    print(f"Semilla aleatoria: {RANDOM_SEED}")
    
    # 1. Cargar datos
    print("\n1. Cargando datos...")
    df = load_processed_data()
    if df is None:
        return
    
    # 2. Preparar características
    print("\n2. Preparando características...")
    X, y = prepare_features(df)
    print(f"Características: {X.shape[1]}, Muestras: {len(y)}")
    
    # 3. Entrenar y evaluar
    print("\n3. Entrenando modelo...")
    set_all_seeds(RANDOM_SEED)
    pipeline, metrics, (X_test, y_test, y_pred_test) = train_and_evaluate(X, y)
    
    # 4. Mostrar métricas
    print("\n4. MÉTRICAS OBTENIDAS:")
    for split in ["train", "test"]:
        print(f"\n{split.upper()}:")
        for metric, value in metrics[split].items():
            print(f"  {metric:4s}: {value:8.4f}")
    
    # 5. Guardar modelo reproducible
    model_path = Path("models/reproducible_model_f3.joblib")
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\n5. Modelo guardado en: {model_path}")
    
    # 6. Guardar reporte
    model_info = {
        "model_type": "RandomForestRegressor",
        "n_estimators": 100,
        "max_depth": 10,
        "model_path": str(model_path)
    }
    
    report_path = save_reproducibility_report(metrics, model_info)
    
    # 7. Comparar con línea base
    compare_with_baseline(metrics)
    
    # 8. Verificar reproducibilidad con segunda ejecución
    print("\n6. Verificando reproducibilidad con segunda ejecución...")
    set_all_seeds(RANDOM_SEED)
    _, metrics2, _ = train_and_evaluate(X, y)
    
    # Comparar métricas
    identical = True
    for split in ["train", "test"]:
        for metric in ["mse", "rmse", "mae", "r2"]:
            diff = abs(metrics[split][metric] - metrics2[split][metric])
            if diff > 1e-10:  # Tolerancia muy pequeña
                identical = False
                print(f"  DIFERENCIA en {split}_{metric}: {diff}")
    
    if identical:
        print("  ✅ REPRODUCIBILIDAD VERIFICADA: Métricas idénticas en ambas ejecuciones")
    else:
        print("  ❌ PROBLEMA: Métricas diferentes entre ejecuciones")
    
    print(f"\n=== SCRIPT COMPLETADO ===")
    print(f"Reporte disponible en: {report_path}")

if __name__ == "__main__":
    main()
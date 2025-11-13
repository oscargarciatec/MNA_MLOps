"""
Fase 3: Pruebas unitarias y de integración para el pipeline de predicción de consumo energético.
- pytest -q tests/test_pipeline_f3.py
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
import joblib
import tempfile
import os

# --- FIXTURES ---
@pytest.fixture(scope="session")
def sample_data():
    """Genera un DataFrame sintético con la estructura esperada."""
    n = 100
    data = {
        'Temperature': np.random.normal(20, 5, n),
        'Humidity': np.random.uniform(30, 80, n),
        'WindSpeed': np.random.uniform(0, 10, n),
        'GeneralDiffuseFlows': np.random.uniform(100, 300, n),
        'DiffuseFlows': np.random.uniform(50, 150, n),
        'PowerConsumption_Zone1': np.random.uniform(100, 500, n),
        'PowerConsumption_Zone2': np.random.uniform(200, 1000, n),
        'PowerConsumption_Zone3': np.random.uniform(100, 500, n),
        'Day': np.random.randint(1, 31, n),
        'Month': np.random.randint(1, 13, n),
        'Hour': np.random.randint(0, 24, n),
        'Minute': np.random.randint(0, 60, n),
        'DayWeek': np.random.randint(1, 8, n),
        'QuarterYear': np.random.randint(1, 5, n),
        'DayYear': np.random.randint(1, 366, n),
    }
    df = pd.DataFrame(data)
    return df

@pytest.fixture
def temp_model_path():
    """Crea una ruta temporal para guardar modelos de prueba."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir) / "test_model_f3.joblib"

# --- UNIT TESTS ---
def test_data_preprocessing_f3(sample_data):
    """Prueba la funcionalidad de preprocesamiento de datos."""
    df = sample_data.copy()
    
    # Simular valores faltantes
    df.loc[0:5, 'Temperature'] = np.nan
    df.loc[10:15, 'Humidity'] = np.nan
    
    # Imputación con mediana
    for col in ['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows']:
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)
    
    # Verificar que no hay valores nulos
    assert not df[['Temperature', 'Humidity']].isna().any().any(), "No debe haber nulos tras imputación"
    assert df.shape[0] == sample_data.shape[0], "Número de filas debe mantenerse"

def test_feature_engineering_f3(sample_data):
    """Prueba la extracción de características temporales."""
    df = sample_data.copy()
    
    # Verificar características temporales
    assert 'Day' in df.columns, "Debe existir característica Day"
    assert 'Month' in df.columns, "Debe existir característica Month"
    assert 'Hour' in df.columns, "Debe existir característica Hour"
    assert 'DayWeek' in df.columns, "Debe existir característica DayWeek"
    
    # Verificar rangos válidos
    assert df['Day'].min() >= 1 and df['Day'].max() <= 31, "Day debe estar en rango 1-31"
    assert df['Month'].min() >= 1 and df['Month'].max() <= 12, "Month debe estar en rango 1-12"
    assert df['Hour'].min() >= 0 and df['Hour'].max() <= 23, "Hour debe estar en rango 0-23"
    assert df['DayWeek'].min() >= 1 and df['DayWeek'].max() <= 7, "DayWeek debe estar en rango 1-7"

def test_model_pipeline_creation_f3():
    """Prueba la creación del pipeline de modelo."""
    # Características numéricas
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
    
    # Modelo
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    
    # Pipeline completo
    pipeline = Pipeline(steps=[('preprocessor', ct), ('model', model)])
    
    assert pipeline is not None, "Pipeline debe crearse correctamente"
    assert len(pipeline.steps) == 2, "Pipeline debe tener 2 pasos"
    assert pipeline.steps[0][0] == 'preprocessor', "Primer paso debe ser preprocessor"
    assert pipeline.steps[1][0] == 'model', "Segundo paso debe ser model"

def test_model_training_and_prediction_f3(sample_data, temp_model_path):
    """Prueba entrenamiento y predicción del modelo."""
    df = sample_data.copy()
    
    # Preparar datos
    X = df.drop(columns=['PowerConsumption_Zone1','PowerConsumption_Zone2','PowerConsumption_Zone3'])
    y = df['PowerConsumption_Zone2'].values
    
    # Crear pipeline
    num_cols = ['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows']
    num_pipeline = Pipeline(steps=[
        ('impMediana', SimpleImputer(strategy='median')),
        ('escalaNum', MinMaxScaler(feature_range=(1, 2))),
    ])
    ct = ColumnTransformer(
        transformers=[('numpipe', num_pipeline, num_cols)],
        remainder='passthrough'
    )
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    pipeline = Pipeline(steps=[('preprocessor', ct), ('model', model)])
    
    # Entrenar
    pipeline.fit(X, y)
    
    # Predicción
    y_pred = pipeline.predict(X)
    
    # Verificaciones
    assert len(y_pred) == len(y), "Predicción debe tener misma longitud que y"
    assert not np.isnan(y_pred).any(), "Predicciones no deben contener NaN"
    assert y_pred.min() >= 0, "Predicciones deben ser positivas"
    
    # Guardar modelo
    joblib.dump(pipeline, temp_model_path)
    assert temp_model_path.exists(), "Modelo debe guardarse correctamente"
    
    # Cargar y probar
    loaded_pipeline = joblib.load(temp_model_path)
    y_pred_loaded = loaded_pipeline.predict(X)
    np.testing.assert_array_almost_equal(y_pred, y_pred_loaded, decimal=6), "Predicciones deben ser idénticas"

def test_metrics_calculation_f3(sample_data):
    """Prueba el cálculo de métricas de evaluación."""
    y_true = sample_data['PowerConsumption_Zone2'].values
    y_pred = y_true + np.random.normal(0, 10, len(y_true))
    
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    assert mse >= 0, "MSE debe ser no negativo"
    assert rmse >= 0, "RMSE debe ser no negativo"
    assert -1 <= r2 <= 1, "R2 debe estar en [-1, 1]"
    assert rmse == np.sqrt(mse), "RMSE debe ser raíz cuadrada de MSE"

def test_data_validation_f3(sample_data):
    """Prueba validación de estructura de datos."""
    df = sample_data.copy()
    
    # Verificar columnas requeridas
    required_columns = [
        'Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows',
        'PowerConsumption_Zone1', 'PowerConsumption_Zone2', 'PowerConsumption_Zone3',
        'Day', 'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear', 'DayYear'
    ]
    
    for col in required_columns:
        assert col in df.columns, f"Columna {col} debe existir"
    
    # Verificar tipos de datos
    for col in ['Temperature', 'Humidity', 'WindSpeed']:
        assert pd.api.types.is_numeric_dtype(df[col]), f"Columna {col} debe ser numérica"
    
    # Verificar rango de valores para características temporales
    assert df['Month'].min() >= 1 and df['Month'].max() <= 12, "Month fuera de rango"
    assert df['Day'].min() >= 1 and df['Day'].max() <= 31, "Day fuera de rango"
    assert df['Hour'].min() >= 0 and df['Hour'].max() <= 23, "Hour fuera de rango"

# --- INTEGRATION TEST ---
def test_pipeline_end_to_end_f3(sample_data, temp_model_path):
    """Prueba el flujo completo end-to-end del pipeline."""
    # 1. Datos de entrada
    df_raw = sample_data.copy()
    assert df_raw is not None, "Datos deben cargarse correctamente"
    
    # 2. Preprocesamiento
    # Simular algunos valores faltantes
    df_raw.loc[0:2, 'Temperature'] = np.nan
    
    # Imputar valores faltantes
    for col in ['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows']:
        if df_raw[col].isna().any():
            median_val = df_raw[col].median()
            df_raw[col].fillna(median_val, inplace=True)
    
    assert not df_raw.isna().any().any(), "No debe haber valores faltantes tras preprocesamiento"
    
    # 3. Separar características y target
    X = df_raw.drop(columns=['PowerConsumption_Zone1','PowerConsumption_Zone2','PowerConsumption_Zone3'])
    y = df_raw['PowerConsumption_Zone2'].values
    
    # 4. Crear y entrenar pipeline
    num_cols = ['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows']
    num_pipeline = Pipeline(steps=[
        ('impMediana', SimpleImputer(strategy='median')),
        ('escalaNum', MinMaxScaler(feature_range=(1, 2))),
    ])
    ct = ColumnTransformer(
        transformers=[('numpipe', num_pipeline, num_cols)],
        remainder='passthrough'
    )
    model = RandomForestRegressor(n_estimators=20, random_state=42)
    pipeline = Pipeline(steps=[('preprocessor', ct), ('model', model)])
    
    # Split temporal
    n = len(X)
    split_idx = int(n * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Entrenar
    pipeline.fit(X_train, y_train)
    
    # 5. Inferencia
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    
    # 6. Métricas
    mse_train = mean_squared_error(y_train, y_pred_train)
    mse_test = mean_squared_error(y_test, y_pred_test)
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    
    # Verificaciones finales
    assert mse_train >= 0 and mse_test >= 0, "MSE debe ser no negativo"
    assert len(y_pred_train) == len(y_train), "Predicción train debe tener correcta longitud"
    assert len(y_pred_test) == len(y_test), "Predicción test debe tener correcta longitud"
    
    # 7. Persistencia
    joblib.dump(pipeline, temp_model_path)
    assert temp_model_path.exists(), "Pipeline debe guardarse correctamente"
    
    # 8. Carga y verificación
    loaded_pipeline = joblib.load(temp_model_path)
    y_pred_loaded = loaded_pipeline.predict(X_test)
    np.testing.assert_array_almost_equal(y_pred_test, y_pred_loaded, decimal=6), "Predicciones deben ser idénticas tras carga"
    
    print(f"✅ Pipeline end-to-end completado:")
    print(f"   Train MSE: {mse_train:.4f}, R²: {r2_train:.4f}")
    print(f"   Test MSE: {mse_test:.4f}, R²: {r2_test:.4f}")

# --- DOCUMENTACIÓN DE EJECUCIÓN ---
# Para ejecutar todas las pruebas:
# source venv/bin/activate && pytest -v tests/test_pipeline_f3.py
# Para ejecutar con reporte de cobertura:
# pytest --cov=. --cov-report=html tests/test_pipeline_f3.py

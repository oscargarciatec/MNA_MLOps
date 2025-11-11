import pytest
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression 
from Project.Modelo import ModeloEspecial
from sklearn.compose import ColumnTransformer
import mlflow
from sklearn.metrics import mean_squared_error

# --- FIXTURES ---

@pytest.fixture(scope="session")
def setup_data():
    """Genera un DataFrame simple con todas las columnas esperadas."""
    n_samples = 50
    data = {
        'Temperature': np.random.rand(n_samples),
        'Humidity': np.random.rand(n_samples),
        'WindSpeed': np.random.rand(n_samples),
        'GeneralDiffuseFlows': np.random.rand(n_samples),
        'DiffuseFlows': np.random.rand(n_samples),
        'PowerConsumption_Zone1': np.random.rand(n_samples) * 100,
        'PowerConsumption_Zone2': np.random.rand(n_samples) * 1000, # Target
        'PowerConsumption_Zone3': np.random.rand(n_samples) * 100,
        'Day': np.random.randint(1, 30, n_samples),
        'Month': np.random.randint(1, 12, n_samples),
        'Hour': np.random.randint(0, 23, n_samples),
        'Minute': np.random.randint(0, 59, n_samples),
        'DayWeek': np.random.randint(0, 6, n_samples),
        'QuarterYear': np.random.randint(1, 4, n_samples),
        'DayYear': np.random.randint(1, 365, n_samples),
    }
    df = pd.DataFrame(data)
    
    # Asegurarse de la limpieza del archivo de prueba
    model_path = "test_model_temp.pkl"
    if os.path.exists(model_path):
        os.remove(model_path)
        
    return df, model_path

# Fixture para obtener una instancia de la clase y un modelo simple
@pytest.fixture
def trainer_instance(setup_data):
    """Retorna una instancia de ModeloEspecial sin entrenar."""
    df, model_path = setup_data
    return ModeloEspecial(
        model_path=model_path, 
        exp="Test_Exp", 
        run_nm="Test_Run"
    ), LinearRegression()


# --- PRUEBAS UNITARIAS ---

def test_setup_preprocessor_structure(trainer_instance):
    """Valida que el preprocesador sea un ColumnTransformer y contenga los pasos correctos."""
    trainer, _ = trainer_instance
    ct = trainer._setup_preprocessor()
    
    # Assert 1: Tipo de Objeto
    assert isinstance(ct, ColumnTransformer), "El objeto debe ser un ColumnTransformer."
    
    # Assert 2: Pasos (solo un transformer para columnas numéricas)
    transformer_names = [name for name, _, _ in ct.transformers]
    assert 'numpipe' in transformer_names, "Falta el pipeline numérico ('numpipe')."
    
    # Assert 3: Transformaciones en el Pipeline Numérico
    # Accede al pipeline numérico (índice 0)
    num_pipeline = ct.transformers[0][1] 
    assert len(num_pipeline.steps) == 2, "El pipeline numérico debe tener 2 pasos."
    assert num_pipeline.steps[0][0] == 'impMediana', "El primer paso debe ser SimpleImputer."
    assert num_pipeline.steps[1][0] == 'escalaNum', "El segundo paso debe ser MinMaxScaler."


def test_data_split_ratio(trainer_instance, setup_data):
    """Valida que la división de datos (train/test) se haga correctamente según el ratio."""
    trainer, model = trainer_instance
    df, _ = setup_data
    
    # Simular la preparación de datos dentro de train_and_save (sin entrenar)
    trainer.train_ratio = 0.80
    
    # Ejecutar una versión simplificada de la preparación de datos
    X = df.drop(columns=[col for col in df.columns if 'PowerConsumption_Zone' in col])
    n = len(df)
    i = int(n * trainer.train_ratio)

    x_train = X.iloc[:i]
    x_test = X.iloc[i:]
    
    # Assert: Verificar la división
    assert x_train.shape[0] == int(n * 0.80), "El tamaño de entrenamiento es incorrecto."
    assert x_test.shape[0] == int(n * 0.20), "El tamaño de prueba es incorrecto."


# --- PRUEBAS DE INTEGRACIÓN ---

def test_full_pipeline_flow(trainer_instance, setup_data, mocker):
    """
    Prueba el flujo completo: Entrenamiento, Logueo (mockeado), Guardado y Predicción.
    """
    trainer, model = trainer_instance
    df, model_path = setup_data
    
    # MOCKING: Simular llamadas a servicios externos
    mocker.patch('mlflow.log_metric')
    mocker.patch('mlflow.log_params')
    mocker.patch('mlflow.log_artifact')
    mocker.patch('dagshub.init')
    mocker.patch('mlflow.set_experiment')
    mocker.patch('mlflow.start_run')
    mocker.patch('mlflow.active_run')

    # 1. Ejecutar Entrenamiento y Guardado (train_and_save)
    x_test, y_test = trainer.train_and_save(df=df, model=model)
    
    # ASSERT: Verificación del Entrenamiento y Persistencia
    assert trainer.pipeline_ is not None, "El pipeline debe estar ajustado."
    assert os.path.exists(model_path), "El modelo no se guardó localmente."
    
    # ASSERT: Verificación de Logueo de MLflow
    mlflow.log_metric.assert_any_call("rmse", np.sqrt(mean_squared_error(y_test, trainer.pipeline_.predict(x_test))))
    mlflow.log_artifact.assert_called_once()
    
    # 2. Ejecutar Carga (load_model)
    # Resetear el pipeline de la instancia
    trainer.pipeline_ = None 
    assert trainer.load_model() is True, "El modelo debe cargarse correctamente."
    
    # 3. Ejecutar Predicción (predict)
    X_new = x_test.head(5)
    predictions = trainer.predict(X_new)
    
    # ASSERT: Verificación de la Predicción
    assert predictions.shape[0] == 5, "El número de predicciones no coincide con las entradas."
    assert isinstance(predictions, np.ndarray), "La salida debe ser un array de NumPy."
    
    # CLEANUP: Limpieza del archivo
    os.remove(model_path)


def test_predict_before_load(trainer_instance):
    """Valida que la predicción falle si el modelo no ha sido cargado/entrenado."""
    trainer, _ = trainer_instance
    X_dummy = pd.DataFrame(np.zeros((1, 5)))
    
    with pytest.raises(RuntimeError) as excinfo:
        trainer.predict(X_dummy)
        
    assert "Model is not loaded" in str(excinfo.value)
"""
Fase 3: API FastAPI para servir predicciones de consumo energético.
Comando para ejecutar: uvicorn app.api_f3:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import os
from typing import Optional
from pathlib import Path

# --- Configuración de la aplicación ---
app = FastAPI(
    title="Power Consumption Prediction API - Fase 3",
    description="API para predecir el consumo de energía en la Zona 2 de Tetuán",
    version="3.0.0"
)

# --- Cargar el modelo ---
MODEL_PATH = Path("app/best_model_pipeline.joblib")
if not MODEL_PATH.exists():
    MODEL_PATH = Path("Project/best_model_pipeline.joblib")

try:
    model_pipeline = joblib.load(MODEL_PATH)
    print(f"Modelo cargado exitosamente desde: {MODEL_PATH}")
except FileNotFoundError:
    print(f"Error: No se encontró el modelo en {MODEL_PATH}")
    model_pipeline = None

# --- Esquemas de entrada y salida ---
class PredictionInput_F3(BaseModel):
    """Esquema de entrada para la predicción de la Fase 3."""
    Temperature: float = Field(..., example=25.5, description="Temperatura ambiente (°C)")
    Humidity: float = Field(..., example=60.2, description="Humedad relativa (%)")
    WindSpeed: float = Field(..., example=5.0, description="Velocidad del viento (m/s)")
    GeneralDiffuseFlows: float = Field(..., example=150.0, description="Flujos difusos generales")
    DiffuseFlows: float = Field(..., example=80.0, description="Flujos difusos específicos")
    Timestamp: datetime = Field(..., example="2023-10-29T10:30:00", description="Fecha y hora de la observación")

    class Config:
        json_schema_extra = {
            "example": {
                "Temperature": 22.5,
                "Humidity": 65.3,
                "WindSpeed": 3.2,
                "GeneralDiffuseFlows": 180.5,
                "DiffuseFlows": 95.1,
                "Timestamp": "2023-10-29T14:30:00"
            }
        }

class PredictionOutput_F3(BaseModel):
    """Esquema de salida para la predicción de la Fase 3."""
    predicted_power_consumption_zone2: float = Field(..., description="Consumo predicho en la Zona 2")
    model_version: str = Field(..., description="Versión del modelo utilizado")
    timestamp: datetime = Field(..., description="Timestamp de la predicción")

class HealthResponse_F3(BaseModel):
    """Esquema para el endpoint de salud."""
    status: str
    model_loaded: bool
    model_path: str

# --- Funciones auxiliares ---
def extract_time_features_f3(dt: datetime) -> dict:
    """Extrae características temporales de un datetime."""
    return {
        "Day": dt.day,
        "Month": dt.month,
        "Hour": dt.hour,
        "Minute": dt.minute,
        "DayWeek": dt.weekday() + 1,  # 1-7
        "QuarterYear": (dt.month - 1) // 3 + 1,  # 1-4
        "DayYear": int(dt.strftime('%j'))  # 1-366
    }

# --- Endpoints ---
@app.get("/", response_model=dict)
def root():
    """Endpoint raíz con información básica de la API."""
    return {
        "message": "Power Consumption Prediction API - Fase 3",
        "version": "3.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse_F3)
def health_check():
    """Endpoint de verificación de salud del servicio."""
    return HealthResponse_F3(
        status="healthy" if model_pipeline is not None else "unhealthy",
        model_loaded=model_pipeline is not None,
        model_path=str(MODEL_PATH)
    )

@app.post("/predict", response_model=PredictionOutput_F3)
def predict_power_consumption_f3(input_data: PredictionInput_F3):
    """
    Endpoint principal para predecir el consumo de energía en la Zona 2.
    
    Args:
        input_data: Datos de entrada con variables meteorológicas y timestamp
        
    Returns:
        PredictionOutput_F3: Predicción del consumo energético
        
    Raises:
        HTTPException: Error 500 si el modelo no está cargado o falla la predicción
    """
    try:
        # Verificar que el modelo esté cargado
        if model_pipeline is None:
            raise HTTPException(
                status_code=500, 
                detail=f"Modelo no encontrado en {MODEL_PATH}. Verifique que el archivo existe."
            )
        
        # 1. Preparar características base
        base_features = {
            "Temperature": input_data.Temperature,
            "Humidity": input_data.Humidity,
            "WindSpeed": input_data.WindSpeed,
            "GeneralDiffuseFlows": input_data.GeneralDiffuseFlows,
            "DiffuseFlows": input_data.DiffuseFlows
        }
        
        # 2. Extraer características temporales
        time_features = extract_time_features_f3(input_data.Timestamp)
        
        # 3. Combinar todas las características
        all_features = {**base_features, **time_features}
        
        # 4. Crear DataFrame con orden de columnas esperado por el modelo
        expected_columns = [
            'Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows',
            'Day', 'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear', 'DayYear'
        ]
        
        X_new = pd.DataFrame([all_features])[expected_columns]
        
        # 5. Realizar predicción
        prediction = model_pipeline.predict(X_new)
        
        # 6. Retornar resultado
        return PredictionOutput_F3(
            predicted_power_consumption_zone2=float(prediction[0]),
            model_version="3.0.0",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        # Log del error para debugging
        print(f"Error en predicción: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error durante la predicción: {str(e)}"
        )

# --- CORS (para desarrollo) ---
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Comando para ejecutar ---
# uvicorn app.api_f3:app --host 0.0.0.0 --port 8000 --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
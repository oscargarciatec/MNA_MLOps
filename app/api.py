# Install necessary libraries: pip install fastapi uvicorn pandas numpy python-multipart joblib
# NOTE: Ensure your trained model file (e.g., 'model_pipeline.joblib') is available.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import pandas as pd
import numpy as np
import os
from typing import Optional

# --- Import your existing classes (assuming ModeloEspecial is imported) ---
# from .Modelo import ModeloEspecial # Adjust import based on your structure
# For simplicity, we'll redefine the relevant parts or assume it's imported correctly.
# Assuming ModeloEspecial is available:
from Modelo import ModeloEspecial

# ----------------------------------------------------
# 1. Initialize Model
# ----------------------------------------------------
MODEL_PATH = "best_model_pipeline.joblib" # <--- **UPDATE THIS PATH** to your saved model file
model_instance = ModeloEspecial(model_path=MODEL_PATH)

if not model_instance.load_model():
    raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}. Cannot start API.")

# ----------------------------------------------------
# 2. Define API Input Schema
# ----------------------------------------------------
class PredictionInput(BaseModel):
    # Features required for the prediction
    Temperature: float = Field(..., example=25.5, description="Ambient temperature.")
    Humidity: float = Field(..., example=60.2, description="Air humidity percentage.")
    WindSpeed: float = Field(..., example=5.0, description="Wind speed.")
    GeneralDiffuseFlows: float = Field(..., example=150.0, description="General diffuse solar flows.")
    DiffuseFlows: float = Field(..., example=80.0, description="Diffuse solar flows.")
    # Input for time features
    Timestamp: datetime = Field(..., example="2023-10-29T10:30:00", description="The date and time of the observation.")

# ----------------------------------------------------
# 3. Create FastAPI App
# ----------------------------------------------------
app = FastAPI(title="Power Consumption Prediction API")

# Simple CORS setup for local development (adjust for production)
from fastapi.middleware.cors import CORSMiddleware
origins = ["https://powerconsumption-pred.netlify.app",
           "https://localhost:3000"] # Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 4. Helper Function for Time Features
# ----------------------------------------------------
# Replicating the logic of Preprocesamiento._features_tiempo for a single timestamp
def create_time_features(dt: datetime) -> pd.Series:
    """Extracts required time features from a single datetime object."""
    dt_series = pd.Series([dt])
    return pd.Series({
        "Day": dt.day,
        "Month": dt.month,
        "Hour": dt.hour,
        "Minute": dt.minute,
        # The model expects columns: DayWeek, QuarterYear, DayYear
        "DayWeek": dt.weekday() + 1, # Day of Week (1-7)
        "QuarterYear": (dt.month - 1) // 3 + 1, # Quarter of Year (1-4)
        "DayYear": int(dt.strftime('%j')), # Day of Year (1-366)
    })

# ----------------------------------------------------
# 5. Prediction Endpoint
# ----------------------------------------------------
@app.post("/predict", tags=["Prediction"])
def predict_power_consumption(input_data: PredictionInput):
    """
    Returns the predicted power consumption for Zone 2.
    """
    try:
        # 1. Prepare base features DataFrame
        base_features = {
            k: [v] for k, v in input_data.model_dump(exclude={"Timestamp"}).items()
        }
        df_base = pd.DataFrame(base_features)

        # 2. Extract Time Features
        time_features = create_time_features(input_data.Timestamp)
        
        # 3. Combine DataFrames
        X_new = pd.concat([df_base, pd.DataFrame([time_features.to_dict()])], axis=1)

        # 4. Order Columns (must match the order the model was trained on)
        # The model's train_and_save assumes this column order (implicitly from _features_tiempo):
        expected_cols = [
            'Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
            'DiffuseFlows', 'Day', 'Month', 'Hour', 'Minute', 
            'DayWeek', 'QuarterYear', 'DayYear'
        ]
        
        # NOTE: The training code has some column name mismatches vs Preprocesamiento.
        # Ensure the column names used in training match those generated here.
        # Based on your training code, the names used are: 'Day', 'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear', 'DayYear'.
        # However, the Preprocesamiento uses: 'Day of Week', 'Quarter of Year', 'Day of Year'.
        # I'm using the names from the training code's explicit column assignment: 'DayWeek', 'QuarterYear', 'DayYear'
        # The time features function above *needs to match* the names the model was trained with.
        
        # Let's adjust the names to match the `df.columns` assignment in `train_and_save`:
        # DayWeek -> DayWeek
        # Quarter of Year -> QuarterYear
        # Day of Year -> DayYear
        
        # Re-map the time feature names to match the expected training column names:
        X_new.columns = [
            'Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows', 
            'Day', 'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear', 'DayYear'
        ]
        X_new = X_new[expected_cols]


        # 5. Make Prediction
        prediction = model_instance.predict(X_new)
        
        # 6. Return Result
        return {"predicted_power_consumption_zone2": float(prediction[0])}
        
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Model Error: {str(e)}")
    except Exception as e:
        # Log the detailed error for debugging
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during prediction.")

# --- Run the API: uvicorn api:app --reload ---
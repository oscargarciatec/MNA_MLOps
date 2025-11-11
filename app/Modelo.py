from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.base import RegressorMixin
import pandas as pd
import numpy as np
import joblib # The library for saving/loading models
import os
from typing import Tuple
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime
import dagshub

class ModeloEspecial:
    """
    Handles training, saving, loading, and predicting for a production environment.
    """
    
    def __init__(
        self,
        model_path: str,
        model: RegressorMixin = None,
        df: pd.DataFrame = None,
        target: str = "PowerConsumption_Zone2",
        num_cols: Tuple = ('Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows'),
        feature_range: Tuple = (1,2),
        train_ratio: float = 0.80,
        exp: str = "Power_Consumption_Pred",
        run_nm : str = None
    ):
        self.model_path = model_path
        self.target = target
        self.num_cols = list(num_cols)
        self.feature_range = feature_range
        self.train_ratio = train_ratio
        self.exp = exp
        self.run_nm = run_nm
        
        # Initialize pipeline as None
        self.pipeline_ = None 

        # Initial set for MLFlow
        dagshub.init(repo_owner='garc1a0scar', repo_name='mna-mlops-team43', mlflow=True)
        #mlflow.set_tracking_uri("https://dagshub.com/garc1a0scar/mna-mlops-team43.mlflow")
        mlflow.set_experiment(self.exp)

    def _setup_preprocessor(self):
        """Helper to create the preprocessing components."""
        num_pipeline = Pipeline(steps=[
            ('impMediana', SimpleImputer(strategy='median')),
            ('escalaNum', MinMaxScaler(feature_range=self.feature_range)),
        ])
        return ColumnTransformer(
            transformers=[('numpipe', num_pipeline, self.num_cols)],
            remainder='passthrough'
        )
        
    def train_and_save(self, df: pd.DataFrame, model: RegressorMixin):
        """
        1. Splits data (X, y).
        2. Fits the full pipeline (preprocessor + model).
        3. Saves the fitted pipeline to disk.
        """
        # 1. Prepare Data
        df.columns=['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
                   'DiffuseFlows','PowerConsumption_Zone1',
                   'PowerConsumption_Zone2', 'PowerConsumption_Zone3' ,'Day',
                   'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear',
                   'DayYear']
        
        X = df.drop(columns=[col for col in df.columns if 'PowerConsumption_Zone' in col])
        y = df[[self.target]].values.ravel()
        
        n = len(df)
        i = int(n * self.train_ratio)

        x_train = X.iloc[:i]
        y_train= y[:i]

        x_test = X.iloc[i:]
        y_test = y[i:]

        run_name = f"{self.run_nm}_{self.target}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        with mlflow.start_run(run_name=run_name):

            # 2. Create and Fit Pipeline
            ct = self._setup_preprocessor()
            self.pipeline_ = Pipeline(steps=[('ct', ct), ('m', model)])

            print("Starting model training...")
            self.pipeline_.fit(x_train, y_train)
            print("Training complete.")

            input_example = x_train.head(1)

            if hasattr(model, 'get_params'):
                mlflow.log_params({
                    'estimator': type(model).__name__,
                    'train_ratio': self.train_ratio,
                    # Log model-specific hyperparameters (e.g., n_estimators)
                    'model_params': model.get_params()
                })
            
            # Log Metrics
            y_pred_test = self.pipeline_.predict(x_test)
            mse = mean_squared_error(y_test, y_pred_test)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred_test)
            
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2_score", r2)

            # Log Model Artifact to MLFlow
            """mlflow.sklearn.log_model(
                sk_model=self.pipeline_,
                name="model", # Path inside the MLFlow run
                registered_model_name=f"{self.target}_Pipeline", # Optional: Register for deployment
                input_example=input_example
            )"""
            mlflow.log_artifact(local_path=self.model_path, artifact_path="model")
            print(f"MLFlow Run ID: {mlflow.active_run().info.run_id}")

            # 3. Save the Fitted Pipeline
            joblib.dump(self.pipeline_, self.model_path)
            print(f"Model successfully saved to: {self.model_path}")

            print(f"\nModel performance on the x_test dataset:")
            print(f"Test RMSE: {rmse:.3f}")

        return x_test, y_test
    
    def load_model(self):
        """Loads the fitted pipeline from disk."""
        if os.path.exists(self.model_path):
            self.pipeline_ = joblib.load(self.model_path)
            print(f"Model successfully loaded from: {self.model_path}")
            return True
        else:
            print(f"Error: Model file not found at {self.model_path}")
            return False

    def predict(self, X_new: pd.DataFrame) -> np.ndarray:
        """
        Performs a prediction using the loaded, trained pipeline.
        Must call load_model() first.
        """
        if self.pipeline_ is None:
            raise RuntimeError("Model is not loaded. Please call load_model() first.")
            
        return self.pipeline_.predict(X_new)
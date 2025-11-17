"""
Fase 3: Simulación de Data Drift y Detección de Pérdida de Performance.
Comando: python scripts/drift_simulation_f3.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.mixture import GaussianMixture
import joblib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataDriftSimulator_F3:
    """Simulador de Data Drift para la Fase 3."""
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        np.random.seed(random_state)
        self.baseline_metrics = {}
        self.drift_metrics = {}
        self.drift_config = {}
    
    def load_data(self, data_path="data/processed/power_tetouan_city_processed.csv"):
        """Carga los datos procesados."""
        try:
            self.data_path = Path(data_path)
            if not self.data_path.exists():
                raise FileNotFoundError(f"No se encontró {data_path}")
            
            df = pd.read_csv(self.data_path)
            
            # Asegurar nombres consistentes
            df.columns = ['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
                         'DiffuseFlows','PowerConsumption_Zone1',
                         'PowerConsumption_Zone2', 'PowerConsumption_Zone3' ,'Day',
                         'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear',
                         'DayYear']
            
            self.df_original = df.copy()
            
            # Separar características y target
            self.X_original = df.drop(columns=['PowerConsumption_Zone1','PowerConsumption_Zone2','PowerConsumption_Zone3'])
            self.y_original = df['PowerConsumption_Zone2'].values
            
            print(f"✅ Datos cargados: {df.shape}")
            print(f"   Características: {self.X_original.shape[1]}")
            print(f"   Muestras: {len(self.y_original)}")
            
            return True
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False
    
    def train_baseline_model(self, test_size=0.2):
        """Entrena un modelo baseline en datos originales."""
        # Split temporal
        n = len(self.X_original)
        split_idx = int(n * (1 - test_size))
        
        self.X_train = self.X_original.iloc[:split_idx]
        self.X_test = self.X_original.iloc[split_idx:]
        self.y_train = self.y_original[:split_idx]
        self.y_test = self.y_original[split_idx:]
        
        # Modelo simple para la simulación
        self.baseline_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.baseline_model.fit(self.X_train, self.y_train)
        
        # Evaluar modelo baseline
        y_pred_baseline = self.baseline_model.predict(self.X_test)
        
        self.baseline_metrics = {
            "mse": float(mean_squared_error(self.y_test, y_pred_baseline)),
            "rmse": float(np.sqrt(mean_squared_error(self.y_test, y_pred_baseline))),
            "mae": float(mean_absolute_error(self.y_test, y_pred_baseline)),
            "r2": float(r2_score(self.y_test, y_pred_baseline))
        }
        
        print(f"✅ Modelo baseline entrenado")
        print(f"   Train set: {self.X_train.shape}")
        print(f"   Test set: {self.X_test.shape}")
        print(f"   Baseline RMSE: {self.baseline_metrics['rmse']:.4f}")
        
        return self.baseline_model
    
    def simulate_temperature_drift(self, shift_factor=1.5, noise_factor=0.1):
        """Simula drift en la temperatura usando Gaussian Mixture Model."""
        print(f"\n🔄 Simulando drift en Temperature (shift_factor={shift_factor})")
        
        # Ajustar GMM a los datos originales de temperatura
        gmm = GaussianMixture(n_components=3, random_state=self.random_state)
        temp_data = self.df_original[['Temperature']].values
        gmm.fit(temp_data)
        
        # Modificar las medias para simular drift
        original_means = gmm.means_.copy()
        shifted_means = original_means * shift_factor
        gmm.means_ = shifted_means
        
        # Generar nuevos datos con drift
        n_samples = len(self.df_original)
        temp_drifted, _ = gmm.sample(n_samples)
        
        # Agregar ruido adicional
        noise = np.random.normal(0, noise_factor, temp_drifted.shape)
        temp_drifted += noise
        
        # Crear dataset con drift
        df_drifted = self.df_original.copy()
        df_drifted['Temperature'] = temp_drifted.flatten()
        
        self.drift_config = {
            "variable": "Temperature",
            "method": "GMM + noise",
            "shift_factor": shift_factor,
            "noise_factor": noise_factor,
            "original_mean": float(self.df_original['Temperature'].mean()),
            "drifted_mean": float(df_drifted['Temperature'].mean()),
            "original_std": float(self.df_original['Temperature'].std()),
            "drifted_std": float(df_drifted['Temperature'].std())
        }
        
        return df_drifted
    
    def simulate_seasonal_drift(self, amplitude=2.0):
        """Simula drift estacional agregando componente sinusoidal."""
        print(f"\n🔄 Simulando drift estacional (amplitude={amplitude})")
        
        df_drifted = self.df_original.copy()
        
        # Crear componente estacional basada en el mes
        seasonal_component = amplitude * np.sin(2 * np.pi * df_drifted['Month'] / 12)
        
        # Aplicar a múltiples variables
        for var in ['Temperature', 'Humidity']:
            df_drifted[var] = df_drifted[var] + seasonal_component
        
        self.drift_config = {
            "variable": "Temperature, Humidity",
            "method": "Seasonal sinusoidal",
            "amplitude": amplitude,
            "original_temp_mean": float(self.df_original['Temperature'].mean()),
            "drifted_temp_mean": float(df_drifted['Temperature'].mean()),
            "original_humidity_mean": float(self.df_original['Humidity'].mean()),
            "drifted_humidity_mean": float(df_drifted['Humidity'].mean())
        }
        
        return df_drifted
    
    def simulate_missing_features_drift(self, missing_prob=0.3):
        """Simula drift por características faltantes."""
        print(f"\n🔄 Simulando drift por features faltantes (missing_prob={missing_prob})")
        
        df_drifted = self.df_original.copy()
        
        # Introducir valores faltantes aleatoriamente
        for feature in ['WindSpeed', 'DiffuseFlows']:
            mask = np.random.random(len(df_drifted)) < missing_prob
            df_drifted.loc[mask, feature] = np.nan
        
        # Imputar con la media (simulando degradación del preprocessing)
        for feature in ['WindSpeed', 'DiffuseFlows']:
            mean_val = df_drifted[feature].mean()
            df_drifted[feature].fillna(mean_val, inplace=True)
        
        self.drift_config = {
            "variable": "WindSpeed, DiffuseFlows",
            "method": "Random missing + mean imputation",
            "missing_probability": missing_prob,
            "affected_samples": int(len(df_drifted) * missing_prob)
        }
        
        return df_drifted
    
    def evaluate_drift_impact(self, df_drifted):
        """Evalúa el impacto del drift en el rendimiento del modelo."""
        # Preparar datos con drift
        X_drifted = df_drifted.drop(columns=['PowerConsumption_Zone1','PowerConsumption_Zone2','PowerConsumption_Zone3'])
        y_drifted = df_drifted['PowerConsumption_Zone2'].values
        
        # Usar el mismo split temporal
        n = len(X_drifted)
        split_idx = int(n * 0.8)
        X_drift_test = X_drifted.iloc[split_idx:]
        y_drift_test = y_drifted[split_idx:]
        
        # Predecir con el modelo baseline
        y_pred_drift = self.baseline_model.predict(X_drift_test)
        
        # Calcular métricas en datos con drift
        self.drift_metrics = {
            "mse": float(mean_squared_error(y_drift_test, y_pred_drift)),
            "rmse": float(np.sqrt(mean_squared_error(y_drift_test, y_pred_drift))),
            "mae": float(mean_absolute_error(y_drift_test, y_pred_drift)),
            "r2": float(r2_score(y_drift_test, y_pred_drift))
        }
        
        # Calcular degradación
        degradation = {}
        for metric in ["mse", "rmse", "mae", "r2"]:
            baseline_val = self.baseline_metrics[metric]
            drift_val = self.drift_metrics[metric]
            
            if metric == "r2":
                # Para R², una disminución es degradación
                degradation[metric] = baseline_val - drift_val
                degradation[f"{metric}_pct"] = ((baseline_val - drift_val) / abs(baseline_val)) * 100
            else:
                # Para MSE, RMSE, MAE, un aumento es degradación
                degradation[metric] = drift_val - baseline_val
                degradation[f"{metric}_pct"] = ((drift_val - baseline_val) / baseline_val) * 100
        
        self.degradation = degradation
        
        print(f"✅ Evaluación de drift completada")
        print(f"   Drift RMSE: {self.drift_metrics['rmse']:.4f}")
        print(f"   Degradación RMSE: {degradation['rmse']:.4f} ({degradation['rmse_pct']:+.1f}%)")
        
        return self.drift_metrics, degradation
    
    def create_drift_visualizations(self, df_drifted, output_dir="reports/figures"):
        """Crea visualizaciones del drift detectado."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        
        # 1. Comparación de distribuciones
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Data Drift Detection - Distributional Shifts', fontsize=16)
        
        # Temperatura
        axes[0,0].hist(self.df_original['Temperature'], bins=50, alpha=0.7, label='Original', color='blue')
        axes[0,0].hist(df_drifted['Temperature'], bins=50, alpha=0.7, label='Drifted', color='red')
        axes[0,0].set_title('Temperature Distribution')
        axes[0,0].set_xlabel('Temperature')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].legend()
        
        # Humedad
        axes[0,1].hist(self.df_original['Humidity'], bins=50, alpha=0.7, label='Original', color='blue')
        axes[0,1].hist(df_drifted['Humidity'], bins=50, alpha=0.7, label='Drifted', color='red')
        axes[0,1].set_title('Humidity Distribution')
        axes[0,1].set_xlabel('Humidity')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].legend()
        
        # Viento
        axes[1,0].hist(self.df_original['WindSpeed'], bins=50, alpha=0.7, label='Original', color='blue')
        axes[1,0].hist(df_drifted['WindSpeed'], bins=50, alpha=0.7, label='Drifted', color='red')
        axes[1,0].set_title('WindSpeed Distribution')
        axes[1,0].set_xlabel('WindSpeed')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].legend()
        
        # Métricas de rendimiento
        metrics = ['RMSE', 'MAE', 'R²']
        baseline_vals = [self.baseline_metrics['rmse'], self.baseline_metrics['mae'], self.baseline_metrics['r2']]
        drift_vals = [self.drift_metrics['rmse'], self.drift_metrics['mae'], self.drift_metrics['r2']]
        
        x_pos = np.arange(len(metrics))
        width = 0.35
        
        axes[1,1].bar(x_pos - width/2, baseline_vals, width, label='Baseline', color='blue', alpha=0.7)
        axes[1,1].bar(x_pos + width/2, drift_vals, width, label='With Drift', color='red', alpha=0.7)
        axes[1,1].set_title('Model Performance Comparison')
        axes[1,1].set_xlabel('Metrics')
        axes[1,1].set_ylabel('Values')
        axes[1,1].set_xticks(x_pos)
        axes[1,1].set_xticklabels(metrics)
        axes[1,1].legend()
        
        plt.tight_layout()
        plot_path = Path(output_dir) / "drift_analysis_f3.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualizaciones guardadas en: {plot_path}")
        return plot_path
    
    def apply_drift_thresholds(self):
        """Aplica umbrales de drift y genera alertas."""
        # Umbrales configurables
        thresholds = {
            "rmse_degradation_pct": 10.0,  # 10% de degradación en RMSE
            "r2_degradation_pct": 5.0,     # 5% de degradación en R²
            "mae_degradation_pct": 15.0     # 15% de degradación en MAE
        }
        
        alerts = []
        
        # Verificar umbrales
        for metric, threshold in thresholds.items():
            if metric in self.degradation:
                degradation_pct = abs(self.degradation[metric])
                if degradation_pct > threshold:
                    alerts.append({
                        "metric": metric,
                        "threshold": threshold,
                        "actual": degradation_pct,
                        "severity": "HIGH" if degradation_pct > threshold * 2 else "MEDIUM"
                    })
        
        # Acciones recomendadas
        if alerts:
            print(f"\n🚨 ALERTAS DE DRIFT DETECTADAS:")
            for alert in alerts:
                print(f"   {alert['severity']}: {alert['metric']} = {alert['actual']:.1f}% (umbral: {alert['threshold']:.1f}%)")
            
            print(f"\n📋 ACCIONES RECOMENDADAS:")
            print(f"   1. Revisar pipeline de feature engineering")
            print(f"   2. Considerar reentrenamiento del modelo")
            print(f"   3. Implementar monitoreo continuo")
            print(f"   4. Evaluar nuevas fuentes de datos")
        else:
            print(f"\n✅ No se detectaron degradaciones significativas")
        
        return alerts, thresholds
    
    def save_drift_report(self, df_drifted, alerts, thresholds, output_dir="reports"):
        """Guarda reporte completo de drift."""
        Path(output_dir).mkdir(exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_info": {
                "original_samples": len(self.df_original),
                "drifted_samples": len(df_drifted),
                "features": list(self.X_original.columns)
            },
            "drift_config": self.drift_config,
            "baseline_metrics": self.baseline_metrics,
            "drift_metrics": self.drift_metrics,
            "performance_degradation": self.degradation,
            "thresholds": thresholds,
            "alerts": alerts,
            "recommendations": {
                "immediate": [
                    "Investigar causa raíz del drift",
                    "Recopilar datos adicionales",
                    "Evaluar reentrenamiento"
                ],
                "monitoring": [
                    "Implementar drift detection continuo",
                    "Configurar alertas automatizadas",
                    "Revisar pipeline periódicamente"
                ]
            }
        }
        
        report_path = Path(output_dir) / "drift_simulation_f3_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Reporte completo guardado en: {report_path}")
        return report_path

def main():
    """Función principal para ejecutar simulación de drift."""
    print("=== SIMULACIÓN DE DATA DRIFT Y DETECCIÓN DE PERFORMANCE - FASE 3 ===")
    
    # Inicializar simulador
    simulator = DataDriftSimulator_F3(random_state=42)
    
    # 1. Cargar datos
    if not simulator.load_data():
        return
    
    # 2. Entrenar modelo baseline
    print(f"\n1. Entrenando modelo baseline...")
    simulator.train_baseline_model()
    
    # 3. Simular diferentes tipos de drift
    print(f"\n2. Simulando data drift...")
    
    # Elegir tipo de drift (puedes cambiar este parámetro)
    drift_type = "temperature"  # Opciones: "temperature", "seasonal", "missing"
    
    if drift_type == "temperature":
        df_drifted = simulator.simulate_temperature_drift(shift_factor=1.3)
    elif drift_type == "seasonal":
        df_drifted = simulator.simulate_seasonal_drift(amplitude=3.0)
    elif drift_type == "missing":
        df_drifted = simulator.simulate_missing_features_drift(missing_prob=0.4)
    
    # 4. Evaluar impacto
    print(f"\n3. Evaluando impacto del drift...")
    drift_metrics, degradation = simulator.evaluate_drift_impact(df_drifted)
    
    # 5. Crear visualizaciones
    print(f"\n4. Generando visualizaciones...")
    simulator.create_drift_visualizations(df_drifted)
    
    # 6. Aplicar umbrales y alertas
    print(f"\n5. Aplicando umbrales de drift...")
    alerts, thresholds = simulator.apply_drift_thresholds()
    
    # 7. Guardar reporte
    print(f"\n6. Guardando reporte...")
    simulator.save_drift_report(df_drifted, alerts, thresholds)
    
    print(f"\n=== SIMULACIÓN COMPLETADA ===")
    print(f"Degradación RMSE: {degradation['rmse_pct']:+.1f}%")
    print(f"Alertas generadas: {len(alerts)}")

if __name__ == "__main__":
    main()
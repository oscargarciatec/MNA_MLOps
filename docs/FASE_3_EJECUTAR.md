# Documentación de Ejecución - Fase 3

## Implementaciones de la Fase 3

Este documento describe cómo ejecutar cada uno de los componentes implementados en la Fase 3 del proyecto MLOps.

---

## 1. Pruebas Unitarias y de Integración

### Descripción
Pruebas automatizadas para validar componentes críticos del pipeline de ML.

### Archivo
- **Ubicación**: `tests/test_pipeline_f3.py`
- **Tipo**: Pruebas unitarias e integración con pytest

### Comandos de Ejecución
```bash
# Activar ambiente virtual
source venv/bin/activate

# Ejecutar todas las pruebas
pytest tests/test_pipeline_f3.py

# Ejecutar con output detallado
pytest -v tests/test_pipeline_f3.py

# Ejecutar con reporte de cobertura
pytest --cov=. --cov-report=html tests/test_pipeline_f3.py
```

### Pruebas Incluidas
- ✅ `test_data_preprocessing_f3`: Validación de preprocesamiento
- ✅ `test_feature_engineering_f3`: Extracción de características temporales
- ✅ `test_model_pipeline_creation_f3`: Creación de pipeline ML
- ✅ `test_model_training_and_prediction_f3`: Entrenamiento y predicción
- ✅ `test_metrics_calculation_f3`: Cálculo de métricas
- ✅ `test_data_validation_f3`: Validación de estructura de datos
- ✅ `test_pipeline_end_to_end_f3`: Flujo completo end-to-end

---

## 2. Servicio FastAPI

### Descripción
API REST para servir predicciones de consumo energético en tiempo real.

### Archivo
- **Ubicación**: `app/api_f3.py`
- **Puerto**: 8000 (configurable)
- **Documentación**: `/docs` (Swagger UI)

### Comandos de Ejecución
```bash
# Activar ambiente virtual
source venv/bin/activate

# Ejecutar API en desarrollo
uvicorn app.api_f3:app --host 0.0.0.0 --port 8000 --reload

# Ejecutar API en producción
uvicorn app.api_f3:app --host 0.0.0.0 --port 8000

# Ejecutar directamente
cd app && python api_f3.py
```

### Endpoints Disponibles
- **GET** `/`: Información básica de la API
- **GET** `/health`: Estado de salud del servicio
- **POST** `/predict`: Predicción de consumo energético
- **GET** `/docs`: Documentación interactiva Swagger

### Ejemplo de Uso
```bash
# Verificar salud del servicio
curl http://localhost:8000/health

# Realizar predicción
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Temperature": 22.5,
    "Humidity": 65.3,
    "WindSpeed": 3.2,
    "GeneralDiffuseFlows": 180.5,
    "DiffuseFlows": 95.1,
    "Timestamp": "2023-10-29T14:30:00"
  }'
```

### Schema de Entrada
```json
{
  "Temperature": 22.5,
  "Humidity": 65.3,
  "WindSpeed": 3.2,
  "GeneralDiffuseFlows": 180.5,
  "DiffuseFlows": 95.1,
  "Timestamp": "2023-10-29T14:30:00"
}
```

### Schema de Salida
```json
{
  "predicted_power_consumption_zone2": 450.25,
  "model_version": "3.0.0",
  "timestamp": "2023-10-29T14:30:15"
}
```

---

## 3. Verificación de Reproducibilidad

### Descripción
Script para verificar que el modelo produce resultados consistentes en diferentes entornos.

### Archivo
- **Ubicación**: `scripts/reproducibilidad_f3.py`
- **Salida**: `reports/reproducibilidad_f3_report.json`
- **Modelo**: `models/reproducible_model_f3.joblib`

### Comandos de Ejecución
```bash
# Activar ambiente virtual
source venv/bin/activate

# Ejecutar script de reproducibilidad
python scripts/reproducibilidad_f3.py

# Ver reporte generado
cat reports/reproducibilidad_f3_report.json
```

### Funcionalidades
- ✅ Configuración de semillas aleatorias (seed=42)
- ✅ Entrenamiento con pipeline reproducible
- ✅ Comparación de métricas entre ejecuciones
- ✅ Guardado de modelo con versión fija de dependencias
- ✅ Generación de reporte detallado en JSON
- ✅ Comparación con línea base

### Artefactos Generados
- `models/reproducible_model_f3.joblib`: Modelo entrenado reproducible
- `reports/reproducibilidad_f3_report.json`: Reporte de métricas y configuración
- `reports/baseline_metrics_f3.json`: Métricas de línea base

---

## 4. Contenedor Docker

### Descripción
Imagen Docker para empaquetar el servicio API y sus dependencias.

### Archivos
- **Dockerfile**: `app/Dockerfile_f3`
- **Dependencias**: `requirements_f3.txt`
- **Imagen**: `ml-service-f3:latest`

### Comandos de Construcción y Ejecución
```bash
# Construir imagen Docker
docker build -f app/Dockerfile_f3 -t ml-service-f3:latest .

# Ejecutar contenedor
docker run -p 8000:8000 ml-service-f3:latest

# Ejecutar en segundo plano
docker run -d -p 8000:8000 --name power-api-f3 ml-service-f3:latest

# Ver logs del contenedor
docker logs power-api-f3

# Detener contenedor
docker stop power-api-f3

# Publicar en Docker Hub (opcional)
docker tag ml-service-f3:latest username/ml-service-f3:v3.0.0
docker push username/ml-service-f3:v3.0.0
```

### Verificación del Contenedor
```bash
# Probar API dentro del contenedor
curl http://localhost:8000/health

# Probar predicción
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Temperature": 25.0,
    "Humidity": 60.0,
    "WindSpeed": 5.0,
    "GeneralDiffuseFlows": 150.0,
    "DiffuseFlows": 80.0,
    "Timestamp": "2023-10-29T10:30:00"
  }'
```

---

## 5. Simulación de Data Drift

### Descripción
Script para simular cambios de distribución en datos y detectar impacto en performance del modelo.

### Archivo
- **Ubicación**: `scripts/drift_simulation_f3.py`
- **Salidas**: 
  - `reports/drift_simulation_f3_report.json`
  - `reports/figures/drift_analysis_f3.png`

### Comandos de Ejecución
```bash
# Activar ambiente virtual
source venv/bin/activate

# Instalar dependencias adicionales si es necesario
pip install matplotlib seaborn

# Ejecutar simulación de drift
python scripts/drift_simulation_f3.py

# Ver reporte generado
cat reports/drift_simulation_f3_report.json

# Ver visualizaciones
open reports/figures/drift_analysis_f3.png
```

### Tipos de Drift Simulados
- **Temperature Drift**: Cambio de distribución usando Gaussian Mixture Models
- **Seasonal Drift**: Componente sinusoidal agregado a variables climáticas
- **Missing Features Drift**: Introducción aleatoria de valores faltantes

### Métricas de Detección
- **Umbrales de Alerta**:
  - RMSE degradación > 10%
  - R² degradación > 5%
  - MAE degradación > 15%
- **Alertas**: HIGH/MEDIUM según severidad
- **Acciones Recomendadas**: Reentrenamiento, revisión del pipeline, monitoreo

### Artefactos Generados
- `reports/drift_simulation_f3_report.json`: Reporte completo de drift
- `reports/figures/drift_analysis_f3.png`: Visualizaciones comparativas

---

## 6. Rutas de Artefactos y Versiones

### Modelos Versionados
```
models/
├── reproducible_model_f3.joblib          # Modelo reproducible (v3.0.0)
└── app/best_model_pipeline.joblib        # Modelo de la API (requerido)
```

### MLflow Registry
- **Experiment**: `Power_Consumption_Pred`
- **Model Name**: `PowerConsumption_Zone2_Pipeline`
- **Versiones**:
  - Version 1: Modelo baseline
  - Version 2: Modelo optimizado
  - Version 3: Modelo Fase 3 (reproducible)

### Reportes y Documentación
```
reports/
├── reproducibilidad_f3_report.json       # Reporte de reproducibilidad
├── drift_simulation_f3_report.json       # Reporte de drift
├── baseline_metrics_f3.json              # Métricas de línea base
└── figures/
    └── drift_analysis_f3.png             # Gráficos de drift
```

### Registros DVC
- `data/raw/power_tetouan_city_modified.csv.dvc`
- `data/processed/power_tetouan_city_processed.csv.dvc`

---

## 7. Comandos Integrados - Makefile

Se pueden agregar estos comandos al `Makefile` existente:

```makefile
## Ejecutar todas las pruebas de Fase 3
.PHONY: test-f3
test-f3:
	pytest tests/test_pipeline_f3.py

## Ejecutar API FastAPI de Fase 3
.PHONY: api-f3
api-f3:
	uvicorn app.api_f3:app --host 0.0.0.0 --port 8000 --reload

## Verificar reproducibilidad
.PHONY: reproducibility-f3
reproducibility-f3:
	python scripts/reproducibilidad_f3.py

## Simular data drift
.PHONY: drift-f3
drift-f3:
	python scripts/drift_simulation_f3.py

## Construir imagen Docker
.PHONY: docker-f3
docker-f3:
	docker build -f app/Dockerfile_f3 -t ml-service-f3:latest .
```

---

## 8. Validación de Implementación

### Lista de Verificación
- ✅ Pruebas unitarias y de integración implementadas
- ✅ API FastAPI con validación Pydantic y documentación OpenAPI
- ✅ Script de reproducibilidad con semillas fijas y comparación de métricas
- ✅ Dockerfile funcional con imagen optimizada
- ✅ Simulación de data drift con múltiples escenarios
- ✅ Documentación completa de comandos y rutas de artefactos

### Comandos de Verificación Rápida
```bash
# Verificar todas las implementaciones
make test-f3 && echo "✅ Tests passed"
make reproducibility-f3 && echo "✅ Reproducibility verified"
make drift-f3 && echo "✅ Drift simulation completed"
make docker-f3 && echo "✅ Docker image built"
make api-f3 & sleep 5 && curl http://localhost:8000/health && echo "✅ API running"
```

---

**Fase 3 completada exitosamente con todas las implementaciones solicitadas.**
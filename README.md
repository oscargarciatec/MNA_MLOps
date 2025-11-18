# MNA_MLOps

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Proyecto MLOps Equipo 43: Predicción del Consumo de Energía en la Ciudad de Tetuán, Marruecos.

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         Project and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│                         generated with `pip freeze > requirements.txt`
│
├── reproducibility    <-  Code for reproducibility testing in a Docker container.
│
└── Project   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes Project a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations

```

--------


# ⚡️ Proyecto MLOps: Predicción del Consumo de Energía en la Ciudad de Tetuán (Marruecos)

Este proyecto aborda la tarea de predicción de series de tiempo para el consumo de energía en Tetuán, Marruecos, utilizando un conjunto de datos público y aplicando un flujo de trabajo de Machine Learning (ML) detallado.

---

## Prerequisitos

### Instalando y configurando DVC, para control de versiones de nuestros datasets

1. Se instalaron las librerías dvc y dvc_gdrive, dentro de nuestro ambiente virtual.
2. Se generó un repositorio (carpeta) dentro de Google Drive.
3. Se creó una cuenta de Google Cloud Platform.
4. Se creó un proyecto dentro de nuestra nueva cuenta.
5. Se habilitó el API de Google Drive dentro de nuestro proyecto.
6. Se creó y se configuró un Cliente OAuth.
7. Se utilizaron las credenciales de este cliente para configurar DVC (con Google Drive) dentro del repositorio.

## 1. Descripción del Conjunto de Datos

El conjunto de datos **Power Consumption of Tetouan City** es una serie de tiempo multivariada donada al Repositorio de Machine Learning de UCI. Las mediciones son cruciales para la gestión eficiente de la energía en la ciudad.

### 1.1. Resumen de Características

| Característica | Descripción |
| :--- | :--- |
| **Origen** | SCADA System de Amendis (operador de servicio público), Tetuán, Marruecos. |
| **Tipo** | Serie de Tiempo Multivariada, Regresión. |
| **Período** | Un año completo, desde el 1 de enero de 2017 hasta el 30 de diciembre de 2017. |
| **Frecuencia**| Observaciones registradas en ventanas de **10 minutos**. |
| **Referencia** | [Power Consumption of Tetouan City (UCI Machine Learning Repository)](https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city). |

### 1.2. Tabla de Variables

| Variable Name | Rol | Tipo | Descripción | ¿Valores Faltantes? |
| :--- | :--- | :--- | :--- | :--- |
| `DateTime` | Característica | Fecha | Cada diez minutos | no |
| `Temperature` | Característica | Continua | Temperatura climática de la ciudad de Tetuán | no |
| `Humidity` | Característica | Continua | Humedad climática de la ciudad de Tetuán | no |
| `Wind Speed` | Característica | Continua | Velocidad del viento de la ciudad de Tetuán | no |
| `general diffuse flows` | Característica | Continua | Flujos difusos generales | no |
| `diffuse flows` | Característica | Continua | Flujos difusos | no |
| `Zone 1 Power Consumption` | Destino | Continua | Consumo de energía de la zona 1 de la ciudad de Tetuán | no |
| `Zone 2 Power Consumption` | Destino | Continua | Consumo de energía de la zona 2 de la ciudad de Tetuán | no |
| `Zone 3 Power Consumption` | Destino | Continua | Consumo de energía de la zona 3 de la ciudad de Tetuán | no |

---

## 2. Flujo de Trabajo de Limpieza y Preprocesamiento

El análisis detallado en el notebook (`ProyectoFase1.ipynb`) se centra en la preparación exhaustiva de los datos para el modelado.

### A. Limpieza de Datos Críticos

* **Conversión de Tipos:** Se transformaron las columnas numéricas (e.g., `Temperature`, `Humidity`, `PowerConsumption_ZoneX`) de tipo `object` a `float64`. Esta conversión incluyó la limpieza de cadenas de texto reemplazando comas (`,`) por puntos (`.`).
* **Manejo de Columna Mixta:** La columna `mixed_type_col` (que contenía datos de texto como `unknown`, `bad`, y `nan`) se eliminó debido a su naturaleza confusa y baja fracción numérica $(\approx 70\%)$.
* **Imputación de `DateTime` (Fechas):**
    * Los `NaN` en la serie de tiempo se imputaron basándose en sus vecinos inmediatos (valores anteriores y siguientes).
    * Si la diferencia entre dos timestamps válidos era exactamente 20 minutos, el punto intermedio (10 minutos) se usó para rellenar el vacío.
    * Para otros faltantes, se calculó el punto medio (promedio de los nanosegundos) de los timestamps vecinos para la imputación.
* **Manejo de Duplicados Temporales:** Se identificaron y eliminaron los *timestamps* duplicados (1045 filas duplicadas). Se conservó la fila duplicada que tenía el mayor número de valores no nulos (mayor puntuación de información).

### B. Tratamiento de Valores Atípicos (Outliers)

* **Detección:** Los valores atípicos en las variables numéricas se definieron utilizando el método del **Rango Intercuartílico (IQR)** ($1.5 \times IQR$).
* **Imputación:** Los outliers detectados fueron reemplazados por la **mediana móvil** calculada en una ventana temporal de 25 períodos (lo que ayuda a preservar las tendencias locales de la serie de tiempo). En caso de que la mediana móvil no estuviera disponible, se usó la mediana global de la columna para la imputación.

### C. Ingeniería de Características

La columna `DateTime` se descompuso para extraer las características cíclicas y temporales del consumo:

* `Day`, `Month`, `Hour`, `Minute`.
* `DayWeek` (Día de la Semana).
* `QuarterYear` (Trimestre del Año).
* `DayYear` (Día del Año).

---

## 3. Modelado y Evaluación

### A. Configuración

* **Variable Objetivo (`Y`):** Se seleccionó **`PowerConsumption_Zone2`** para la predicción.
* **División de Datos:** Se utilizó una división por índice (no aleatoria) de **80% para entrenamiento** (`x_train`) y **20% para prueba** (`x_test`), respetando la secuencia temporal.

### B. Pipeline de Preprocesamiento
Un `ColumnTransformer` fue configurado para manejar el conjunto de entrenamiento:
1.  **Imputación:** Imputación de nulos restantes con la mediana.
2.  **Escalado:** Se aplicó **MinMaxScaler** a las variables meteorológicas (e.g., `Temperature`, `Humidity`, `WindSpeed`) con un rango de $(1, 2)$.
3.  **Variables Temporales:** Las características temporales creadas (`Day`, `Hour`, etc.) se pasaron directamente al modelo (`remainder='passthrough'`).

### C. Modelos Implementados y Resultados

Se implementaron y compararon **5 algoritmos diferentes** de Machine Learning:

1. **Random Forest Regressor**
   - n_estimators: 700, max_features: 3
   - Mejor para datos no lineales y temporales

2. **ElasticNet**
   - Regularización L1 + L2
   - alpha: 0.1, l1_ratio: 0.5

3. **Gradient Boosting Regressor**
   - n_estimators: 500, learning_rate: 0.05
   - Boosting secuencial

4. **XGBoost Regressor** (opcional)
   - Implementación optimizada de gradient boosting
   - n_estimators: 500

5. **Support Vector Regressor (SVR)**
   - kernel: rbf, C: 100

**Métricas de Evaluación:**
- **RMSE**: Root Mean Squared Error (kW)
- **MAE**: Mean Absolute Error (kW)
- **MAPE**: Mean Absolute Percentage Error (%)
- **R²**: Coeficiente de Determinación

**Meta de Desempeño:**
- RMSE < 4,000 kW
- MAPE < 12%
- R² > 0.90

*Los resultados específicos de cada modelo se encuentran documentados en el notebook.*
---

## 4. Documentación del Proyecto

### Documentos Disponibles

1. **[Machine Learning Canvas](docs/ML_Canvas.md)**
   - Metodología completa del proyecto siguiendo el framework ML Canvas
   - Proposición de valor y objetivos del negocio
   - Pipeline de datos y construcción del modelo
   - Estrategia de predicción y evaluación
   - Monitoreo en producción

2. **[Guía de Versionamiento de Datos](docs/Data_Versioning.md)**
   - Configuración de Git y DVC
   - Workflows de versionamiento completos
   - Convenciones de nomenclatura y commits
   - Mejores prácticas
   - Troubleshooting común

3. **[Notebook Principal](notebooks/Fase%201_Equipo43.ipynb)**
   - Secciones completamente documentadas:
     - Análisis Exploratorio de Datos (EDA)
     - Preprocesamiento detallado con justificaciones
     - Implementación de 5 modelos de ML
     - Comparación exhaustiva con visualizaciones
     - Guía de reproducibilidad paso a paso
     - Documentación de versionamiento integrada

---

## 5. Guía de Reproducibilidad

### Requisitos del Sistema
- Python 3.8+
- Jupyter Notebook 6.0+
- Git (DVC opcional)
- 8GB RAM (16GB recomendado)

### Instalación Rápida

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd MNA_MLOps

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install pandas numpy matplotlib seaborn scipy scikit-learn xgboost jupyter

# 4. Ejecutar Jupyter
jupyter notebook
```

### Paquetes Requeridos
```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
scipy>=1.9.0
scikit-learn>=1.2.0
xgboost>=1.7.0
jupyter>=1.0.0
```

### Tiempo de Ejecución Estimado
- **EDA y Preprocesamiento**: ~2-3 minutos
- **Cross-Validation (5 modelos)**: ~10-15 minutos
- **Entrenamiento final**: ~2-3 minutos
- **Total**: ~15-20 minutos

### Verificación de Reproducibilidad

El proyecto ha sido verificado en múltiples entornos para garantizar reproducibilidad completa:

#### Entornos Probados

1. **MacOS (Desarrollo Local)**
   - Sistema: macOS Sonoma 14.6
   - Python: 3.13
   - RAM: 16GB
   - Procesador: Apple M1/M2
   - Estado: VERIFICADO

2. **Ubuntu 22.04 (CI/CD)**
   - Sistema: Ubuntu latest (GitHub Actions)
   - Python: 3.10
   - Entorno: GitHub Actions runner
   - Estado: VERIFICADO

3. **Docker Container (Producción)**
   - Base Image: python:3.13-slim
   - Plataforma: Google Cloud Run
   - Región: us-east1
   - Estado: VERIFICADO

4. **Docker Container (Verificación de reproducibilidad de modelo)**
   - Base Image: python:3.13-slim
   - Plataforma: Docker
   - Estado: VERIFICADO

Nota: Para revisar el detalle de la verificación de reproducibilidad del modelo, revisar el README.md dentro de la carpeta `reproducibility`.



#### Consistencia de Resultados

Los modelos entrenados en diferentes entornos producen resultados consistentes:

- **RMSE**: Variación < 0.1% entre entornos
- **R² Score**: Consistente hasta 4 decimales (0.XXXX)
- **Predicciones**: Diferencias < 1 kW en valores predichos

#### Scripts de Reproducibilidad

1. **Pipeline Completo**:
   ```bash
   python Project/run_full_pipeline.py
   ```

2. **Pruebas Automatizadas**:
   ```bash
   pytest tests/ -v
   ```

3. **Verificación de Entorno**:
   ```bash
   python Project/validate_environment.py
   ```

#### Versionamiento y Trazabilidad

- **Datos**: Versionados con DVC en Amazon S3
- **Código**: Git con commits detallados
- **Modelos**: Rastreados con MLflow/DagsHub
- **Infraestructura**: Dockerfile + CI/CD reproducible

Para más detalles, consultar `docs/Testing_Guide.md`

---

## 6. Mejoras Implementadas - Fase 1

### Completado

1. **Machine Learning Canvas**
   - Documento completo con todas las secciones
   - Siguiendo metodología de Louis Dorard (2016)
   - Incluye objetivos, pipeline, y estrategia de monitoreo

2. **Modelos Múltiples**
   - 5 algoritmos implementados y comparados
   - Random Forest, ElasticNet, Gradient Boosting, XGBoost, SVR
   - Evaluación con cross-validation y test set

3. **Documentación de Preprocesamiento**
   - Sección completa en el notebook
   - Justificación de cada técnica aplicada
   - Tablas de transformaciones y estadísticas

4. **Comparación de Modelos**
   - Evaluación exhaustiva con 4 métricas (RMSE, MAE, MAPE, R²)
   - Visualizaciones comparativas
   - Análisis de residuos del mejor modelo
   - Identificación automática del mejor modelo

5. **Guía de Reproducibilidad**
   - Instrucciones paso a paso
   - Configuración de entorno
   - Solución de problemas comunes
   - Tiempos de ejecución estimados

6. **Versionamiento de Datos**
   - Documentación completa de Git y DVC
   - Workflows detallados
   - Convenciones y mejores prácticas
   - Integración en el notebook

7. **Pruebas Automatizadas (Testing)**
   - Pruebas unitarias para componentes críticos
   - Pruebas de integración end-to-end
   - Cobertura de código ~75-80%
   - Framework: pytest con fixtures y mocking
   - Ver `docs/Testing_Guide.md` para detalles

---

## 7. Testing y Calidad de Código

### Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar con cobertura (requiere pytest-cov)
pytest tests/ --cov=Project --cov=app --cov-report=term-missing

# Modo silencioso
pytest tests/ -q
```

### Cobertura de Código

| Módulo | Cobertura | Descripción |
|--------|-----------|-------------|
| **Project/Modelo.py** | ~90% | Lógica de entrenamiento y predicción |
| **Project/Preprocesamiento.py** | ~75% | Transformaciones de datos |
| **Project/CargaDatos.py** | ~80% | Carga de datasets |
| **app/api.py** | ~60% | API endpoints (vía integración) |
| **General** | ~75-80% | Cobertura de rutas críticas |

### Tipos de Pruebas

1. **Pruebas Unitarias**:
   - Validación de preprocesador
   - División de datos (train/test split)
   - Manejo de errores

2. **Pruebas de Integración**:
   - Pipeline completo (carga → preprocesamiento → entrenamiento → predicción)
   - Integración con MLflow
   - Persistencia y carga de modelos

Para documentación completa, consultar `docs/Testing_Guide.md`

---

## 8. Estructura de Archivos Clave

### Estructura actualizada del proyecto

```
MNA_MLOps/
│
├── data/
│   ├── raw/                                    # Datos originales (inmutables)
│   │   ├── power_tetouan_city_original.csv
│   │   └── power_tetouan_city_modified.csv
│   └── processed/                              # Datos procesados
│       └── power_tetouan_city_processed.csv    #  Dataset final
│
├── notebooks/
│   └── Fase 1_Equipo43.ipynb                  #  Notebook principal
│
├── docs/
│   ├── ML_Canvas.md                           #  Machine Learning Canvas
│   ├── Data_Versioning.md                     #  Guía de versionamiento
│   └── README.md
│
├── README.md                                   #  Este archivo
└── .gitignore
```

---

## 9. Pipeline MLOps Completo

### Ejecución del Flujo Completo End-to-End

El proyecto incluye un script maestro que orquesta todo el flujo MLOps automáticamente:

```bash
# Activar ambiente virtual
source venv/bin/activate

# Ejecutar pipeline completo
python Project/run_mlops_complete.py
```

#### ¿Qué hace el pipeline completo?

El script `run_mlops_complete.py` ejecuta 6 pasos secuenciales:

1. **Validación del Entorno** → Verifica Python, dependencias, DVC, AWS
2. **DVC Data Pull** → Descarga última versión de datos desde S3
3. **Pipeline de Entrenamiento** → Carga, preprocesa, entrena y evalúa modelo
4. **Testing** → Ejecuta test suite con pytest
5. **Data Drift Monitoring** → Analiza drift con Evidently.ai
6. **Reporte Summary** → Genera resumen JSON con todas las métricas

#### Opciones de ejecución

```bash
# Pipeline completo (todas las etapas)
python Project/run_mlops_complete.py

# Omitir tests (ejecución más rápida)
python Project/run_mlops_complete.py --skip-tests

# Omitir monitoreo de drift
python Project/run_mlops_complete.py --skip-drift

# Mostrar ayuda
python Project/run_mlops_complete.py --help
```

#### Outputs generados

Después de ejecutar el pipeline completo, se generan:

```
MNA_MLOps/
├── app/
│   └── best_model_pipeline.joblib              # Modelo entrenado (~45MB)
├── data/
│   └── processed/
│       └── power_tetouan_city_processed.csv    # Datos procesados
├── reports/
│   ├── evidently/
│   │   ├── data_drift_report.html              # Reporte interactivo de drift
│   │   ├── data_drift_report.json              # Métricas de drift (JSON)
│   │   └── performance_comparison.json         # Comparación baseline vs drift
│   └── mlops_pipeline_summary.json             # Resumen completo del pipeline
```

#### Tiempo de ejecución estimado

En MacBook Pro M1 (16GB RAM):
- Validación de entorno: ~5 segundos
- DVC Pull: ~30 segundos (si hay cambios)
- Entrenamiento: ~3-5 minutos
- Tests: ~10 segundos
- Drift monitoring: ~15 segundos
- **Total: 4-6 minutos**

#### Scripts individuales disponibles

Si prefieres ejecutar componentes individuales:

```bash
# Solo entrenamiento
python Project/run_full_pipeline.py

# Solo drift monitoring
python Project/monitor_data_drift_evidently.py

# Solo validación de entorno
python Project/validate_environment.py

# Solo tests
pytest tests/ -v
```

---

## 10. Monitoreo con Evidently.ai

### Implementación de Data Drift Monitoring

El proyecto incluye monitoreo avanzado con Evidently.ai para detectar drift en datos y modelo.

#### Ejecución

```bash
# Instalar Evidently
pip install evidently

# Ejecutar monitoreo
python Project/monitor_data_drift_evidently.py
```

#### Reportes Generados

Los reportes se guardan en `reports/evidently/`:

1. **Data Drift Report** (`data_drift_report.html`)
   - Detección de drift a nivel dataset
   - Análisis por feature con tests estadísticos
   - Comparación de distribuciones
   - Visualizaciones interactivas

2. **Data Quality Report** (`data_quality_report.html`)
   - Análisis de valores faltantes
   - Validación de tipos de datos
   - Detección de duplicados
   - Matrices de correlación

3. **Test Suite** (`drift_test_suite.html`)
   - Tests automatizados pass/fail
   - Alertas y recomendaciones

4. **JSON Metrics** (`data_drift_report.json`)
   - Métricas en formato programático
   - Integración con sistemas de alertas

#### Tipos de Drift Simulados

- **Temperature Drift**: +5°C shift (cambio climático/estacional)
- **Humidity Drift**: +15% incremento
- **Mixed Drift**: Múltiples features simultáneamente
- **Control**: Sin drift (prueba de control)

#### Tests Estadísticos

- **Kolmogorov-Smirnov (KS)**: Features numéricas
- **Chi-squared**: Features categóricas
- **Threshold**: p-value < 0.05 indica drift

Para documentación completa, consultar `docs/Evidently_Monitoring_Guide.md`

---

## 11. Próximos Pasos (Implementados)

- [x] Despliegue del modelo (containerización con Docker)
- [x] API REST para predicciones (FastAPI)
- [x] Monitoreo en producción con MLflow y Evidently
- [x] CI/CD pipeline (GitHub Actions)
- [x] Data drift detection (K-S test + Evidently.ai)
- [x] Pipeline MLOps completo end-to-end (run_mlops_complete.py)
- [x] Evaluación de performance con drift monitoring
- [ ] Reentrenamiento automático (futuro)
- [ ] Dashboard de métricas en tiempo real (futuro)

---

## 12. Referencias

- **Dataset**: Salam, A., & El Hibaoui, A. (2023). Power Consumption of Tetouan City. UCI Machine Learning Repository.
- **ML Canvas**: Dorard, L. (2016). Machine Learning Canvas. https://www.louisdorard.com/machine-learning-canvas
- **DVC Documentation**: https://dvc.org/doc
- **Scikit-learn**: https://scikit-learn.org/
- **Evidently.ai**: https://www.evidentlyai.com/ - ML monitoring and observability
- **FastAPI**: https://fastapi.tiangolo.com/
- **MLflow**: https://mlflow.org/

---

## 13. Contacto

**Equipo 43**
- Alberto Campos Hernández (A01795645)
- Oscar Enrique García García (A01016093)
- Jessica Giovana García Gómez (A01795922)
- Esteban Sebastián Guerra Espinoza (A01795897)
- Rafael Sánchez Marmolejo (A00820345)

**Institución**: Tecnológico de Monterrey
**Curso**: Operaciones de Aprendizaje Automático (MLOps)
**Profesores**: Dr. Gerardo Rodríguez Hernández, Mtro. Ricardo Valdez Hernández

---

**Última actualización**: Noviembre 2025
**Versión**: 3.0 - Fase 3 Completa

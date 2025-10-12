<<<<<<< HEAD
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
    * Los `NaN` en la serie de tiempo se imputaron basándose en sus vecinos inmediatos (valores anteriores y siguientes).
    * Si la diferencia entre dos timestamps válidos era exactamente 20 minutos, el punto intermedio (10 minutos) se usó para rellenar el vacío.
    * Para otros faltantes, se calculó el punto medio (promedio de los nanosegundos) de los timestamps vecinos para la imputación.
* **Manejo de Duplicados Temporales:** Se identificaron y eliminaron los *timestamps* duplicados (1045 filas duplicadas). Se conservó la fila duplicada que tenía el mayor número de valores no nulos (mayor puntuación de información).

### B. Tratamiento de Valores Atípicos (Outliers)

* **Detección:** Los valores atípicos en las variables numéricas se definieron utilizando el método del **Rango Intercuartílico (IQR)** ($1.5 \times IQR$).
* **Imputación:** Los outliers detectados fueron reemplazados por la **mediana móvil** calculada en una ventana temporal de 25 períodos (lo que ayuda a preservar las tendencias locales de la serie de tiempo). En caso de que la mediana móvil no estuviera disponible, se usó la mediana global de la columna para la imputación.

### C. Ingeniería de Características


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

### C. Modelo y Resultados

Se utilizó el algoritmo **RandomForestRegressor** con hiperparámetros específicos (ej. `n_estimators=700`, `max_features=3`).

| Etapa | Métrica | Resultado |
| :--- | :--- | :--- |
| **Validación Cruzada** | RMSE (Repetido K-Fold) | $864.586 \pm 21.037$ |
| **Evaluación Final (Test)** | RMSE (Error Cuadrático Medio Raíz) | $3736.559$ |
| **Evaluación Final (Test)** | MAPE (Error Porcentual Absoluto Medio) | $11.222\%$ |

**Nota sobre los Resultados:** La diferencia entre el RMSE de Cross-Validation y el RMSE de la evaluación final del Test Set sugiere una posible **sobreestimación** del rendimiento durante el entrenamiento, o que el conjunto de prueba (los últimos meses del año) presenta patrones de consumo más difíciles de predecir.
=======
# 🚀 Proyecto MLOps Mejorado - Predicción de Energía Eléctrica

## 📋 Información del Proyecto

**Equipo:** 43  
**Programa:** MNA (Maestría en Inteligencia Artificial Aplicada)  
**Dataset:** Consumo de energía eléctrica en Tetuán, Marruecos  
**Objetivo:** Desarrollar un pipeline completo de MLOps para predicción de consumo energético

## 🎯 Objetivos del Proyecto

### Objetivos Principales
- ✅ Implementar una **estructura mejorada de MLOps** siguiendo mejores prácticas
- ✅ Realizar **análisis exploratorio de datos** más profundo y comprehensivo  
- ✅ Aplicar **ingeniería de características** avanzada para series temporales
- ✅ Desarrollar **múltiples modelos** con optimización de hiperparámetros
- ✅ Implementar **versionado de datos** con DVC
- ✅ Integrar **seguimiento de experimentos** con MLflow
- ✅ Lograr **mejores resultados de performance** que el proyecto base

### Lineamientos MLOps Implementados
1. **Manipulación de datos:** Pipelines automatizados y reproducibles
2. **EDA (Análisis Exploratorio):** Análisis comprehensivo con visualizaciones avanzadas
3. **Preprocesamiento:** Estrategias robustas para series temporales
4. **Versionado:** Control de versiones de datos, código y modelos
5. **Construcción de modelos:** Múltiples algoritmos con validación rigurosa

## 📊 Dataset

**Fuente:** Consumo de energía eléctrica en Tetuán, Marruecos  
**Características:**
- Variables climáticas (temperatura, humedad, velocidad del viento)
- Variables de radiación solar
- Variable objetivo: Consumo de energía eléctrica
- Datos temporales para análisis de series de tiempo

## 🏗️ Arquitectura del Proyecto

```
📦 Proyecto_MLOps_Mejorado_Equipo43/
├── 📁 config/                    # Configuraciones
│   └── config.yaml              # Configuración principal
├── 📁 data/                     # Datos (versionados con DVC)
│   ├── raw/                     # Datos originales
│   ├── interim/                 # Datos intermedios
│   ├── processed/               # Datos procesados
│   └── external/                # Datos externos
├── 📁 experiments/              # Resultados de experimentos
├── 📁 logs/                     # Logs del sistema
├── 📁 mlruns/                   # Tracking de MLflow
├── 📁 models/                   # Modelos entrenados
├── 📁 notebooks/                # Notebooks Jupyter
│   ├── 01_EDA_Comprehensivo.ipynb
│   ├── 02_Preprocesamiento_Avanzado.ipynb
│   ├── 03_Ingenieria_Caracteristicas.ipynb
│   ├── 04_Entrenamiento_Modelos.ipynb
│   ├── 05_Evaluacion_Performance.ipynb
│   └── 06_Pipeline_Completo.ipynb
├── 📁 references/               # Documentación y referencias
├── 📁 reports/                  # Reportes y visualizaciones
│   └── figures/                 # Gráficos generados
├── 📁 scripts/                  # Scripts de utilidad
├── 📁 src/                      # Código fuente principal
│   ├── data/                    # Módulos de datos
│   ├── features/                # Ingeniería de características
│   ├── models/                  # Modelos ML
│   ├── utils/                   # Utilidades
│   ├── visualization/           # Visualizaciones
│   └── main_pipeline.py         # Pipeline principal
├── 📁 tests/                    # Tests unitarios
├── requirements.txt             # Dependencias Python
├── pyproject.toml              # Configuración del proyecto
├── Makefile                    # Comandos automatizados
└── README.md                   # Este archivo
```

## 🚀 Instalación y Configuración

### 1️⃣ Clonar el Repositorio
```bash
git clone <repository-url>
cd Proyecto_MLOps_Mejorado_Equipo43
```

### 2️⃣ Crear Entorno Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
# O usando make
make install
```

### 4️⃣ Configurar DVC (Versionado de Datos)
```bash
make setup-dvc
```

### 5️⃣ Configurar MLflow (Tracking de Experimentos)
```bash
mlflow ui --host 0.0.0.0 --port 5000
# O usando make
make mlflow-ui
```

## 🔄 Pipeline de MLOps

### Flujo Completo
```bash
# 1. Procesar datos
make data-process

# 2. Entrenar modelos
make train

# 3. Evaluar modelos
make evaluate

# 4. Pipeline completo
make run-pipeline
```

### Comandos Individuales
```bash
# Análisis exploratorio
jupyter lab notebooks/01_EDA_Comprehensivo.ipynb

# Entrenamiento específico
python src/main_pipeline.py --stage train --model xgboost

# Evaluación
python src/main_pipeline.py --stage evaluate
```

## 📈 Modelos Implementados

### Algoritmos Base
- **Random Forest:** Robusto para características no lineales
- **ElasticNet:** Regularización para características lineales
- **XGBoost:** Gradient boosting optimizado
- **LightGBM:** Gradient boosting eficiente

### Técnicas Avanzadas
- ✅ **Optimización de hiperparámetros** con Optuna
- ✅ **Validación cruzada temporal** para series de tiempo
- ✅ **Ensambles** de múltiples modelos
- ✅ **Feature selection** automatizada

## 📊 Métricas de Evaluación

### Métricas Principales
- **RMSE (Root Mean Square Error)**
- **MAE (Mean Absolute Error)**
- **MAPE (Mean Absolute Percentage Error)**
- **R² (Coefficient of Determination)**

### Objetivos de Performance
- 🎯 **RMSE < 50.0**
- 🎯 **R² > 0.85**
- 🎯 **MAPE < 10%**

## 📚 Notebooks Incluidos

### 1️⃣ EDA Comprehensivo (`01_EDA_Comprehensivo.ipynb`)
- Análisis estadístico detallado
- Visualizaciones avanzadas
- Detección de outliers y patrones
- Análisis de correlaciones

### 2️⃣ Preprocesamiento Avanzado (`02_Preprocesamiento_Avanzado.ipynb`)
- Limpieza de datos
- Manejo de valores faltantes
- Normalización y escalado
- División temporal de datos

### 3️⃣ Ingeniería de Características (`03_Ingenieria_Caracteristicas.ipynb`)
- Características temporales
- Características de lag
- Estadísticas móviles
- Interacciones entre variables

### 4️⃣ Entrenamiento de Modelos (`04_Entrenamiento_Modelos.ipynb`)
- Configuración de modelos
- Optimización de hiperparámetros
- Validación cruzada
- Tracking con MLflow

### 5️⃣ Evaluación de Performance (`05_Evaluacion_Performance.ipynb`)
- Comparación de modelos
- Análisis de residuos
- Métricas de evaluación
- Visualización de resultados

### 6️⃣ Pipeline Completo (`06_Pipeline_Completo.ipynb`)
- Demostración end-to-end
- Automatización del flujo
- Reproducibilidad
- Documentación de resultados

## 🛠️ Herramientas y Tecnologías

### Core ML Stack
- **Python 3.8+**
- **Pandas, NumPy:** Manipulación de datos
- **Scikit-learn:** Modelos base
- **XGBoost, LightGBM:** Gradient boosting

### MLOps Stack
- **MLflow:** Tracking de experimentos
- **DVC:** Versionado de datos
- **Optuna:** Optimización de hiperparámetros
- **Great Expectations:** Validación de datos

### Visualización
- **Matplotlib, Seaborn:** Gráficos estáticos
- **Plotly:** Gráficos interactivos
- **Jupyter Lab:** Notebooks interactivos

## 📋 Comandos Útiles

```bash
# Desarrollo
make dev-setup              # Configuración completa de desarrollo
make quality-check          # Verificación de calidad del código
make test                   # Ejecutar tests

# Datos
make data-add              # Añadir datos a DVC
make data-push             # Subir datos versionados
make data-pull             # Descargar datos versionados

# MLflow
make mlflow-ui             # Iniciar interfaz de MLflow
make model-register        # Registrar mejor modelo

# Jupyter
make jupyter-lab           # Iniciar Jupyter Lab
make jupyter-notebook      # Iniciar Jupyter Notebook
```

## 🎯 Resultados Esperados

### Mejoras vs Proyecto Base
- ✅ **Estructura más organizada** y mantenible
- ✅ **EDA más profundo** con insights accionables
- ✅ **Ingeniería de características** más sofisticada
- ✅ **Múltiples modelos** con optimización
- ✅ **Mejor performance** en métricas clave
- ✅ **Pipeline reproducible** y automatizado

### Métricas Objetivo
- 🎯 Mejorar **R²** en al menos **10%**
- 🎯 Reducir **RMSE** en al menos **15%**
- 🎯 Implementar **versionado completo** de datos y modelos
- 🎯 Lograr **reproducibilidad 100%** de experimentos

## 👥 Equipo 43

**Integrante:**
- [Rafael Sánchez Marmolejo] - [Site Reliability Engineer]

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**Proyecto desarrollado para MNA - Maestría en Inteligencia Artificial Aplicada**  
**Equipo 43 - 2025**
>>>>>>> main

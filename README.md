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

## 0. Prerequisitos

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

### C. Modelo y Resultados

Se utilizó el algoritmo **RandomForestRegressor** con hiperparámetros específicos (ej. `n_estimators=700`, `max_features=3`).

| Etapa | Métrica | Resultado |
| :--- | :--- | :--- |
| **Validación Cruzada** | RMSE (Repetido K-Fold) | $864.586 \pm 21.037$ |
| **Evaluación Final (Test)** | RMSE (Error Cuadrático Medio Raíz) | $3736.559$ |
| **Evaluación Final (Test)** | MAPE (Error Porcentual Absoluto Medio) | $11.222\%$ |

**Nota sobre los Resultados:** La diferencia entre el RMSE de Cross-Validation y el RMSE de la evaluación final del Test Set sugiere una posible **sobreestimación** del rendimiento durante el entrenamiento, o que el conjunto de prueba (los últimos meses del año) presenta patrones de consumo más difíciles de predecir.
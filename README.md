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

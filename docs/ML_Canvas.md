# Machine Learning Canvas - Power Consumption Prediction
## Equipo 43

---

## 1. OBJETIVO

### Proposición de Valor
**¿Qué estamos tratando de hacer? ¿Por qué es importante? ¿Quién lo usará o será impactado?**

- **Objetivo:** Predecir el consumo de energía eléctrica en tres zonas de distribución de la ciudad de Tetouan, Marruecos, basándose en variables climáticas y temporales.

- **Importancia:**
  - Optimizar la distribución y generación de energía eléctrica
  - Reducir costos operativos de las compañías eléctricas
  - Mejorar la planificación de demanda energética
  - Contribuir a la sostenibilidad energética mediante mejor gestión de recursos

- **Usuarios e Impactados:**
  - Compañías eléctricas y operadores de red
  - Planificadores energéticos municipales
  - Ciudadanos (beneficiados por servicio más eficiente)
  - Reguladores del sector energético

---

## 2. APRENDER (Data Preparation)

### 2.1 Fuentes de Datos
**¿De dónde provienen los datos?**

- **Dataset Principal:** UCI Machine Learning Repository
  - Nombre: Power Consumption of Tetouan City
  - Origen: Abdelmalek Essaadi University, Morocco
  - Período: Año completo 2017
  - Frecuencia: Mediciones cada 10 minutos
  - Instancias originales: 52,416 registros
  - Licencia: Creative Commons Attribution 4.0 International (CC BY 4.0)

### 2.2 Recolección de Datos
**¿Cómo obtenemos nuevos datos para aprendizaje?**

- Descarga directa desde UCI ML Repository
- Dataset estático para este proyecto académico
- En producción: integración con sistemas SCADA de distribución eléctrica
- Datos climáticos de estaciones meteorológicas locales

### 2.3 Features (Características)
**Inputs derivados de los datos crudos**

#### Variables de Entrada:
1. **Temperature** (°C): Temperatura ambiental
2. **Humidity** (%): Humedad relativa
3. **Wind Speed** (m/s): Velocidad del viento
4. **General Diffuse Flows** (W/m²): Radiación solar difusa general
5. **Diffuse Flows** (W/m²): Flujos de radiación difusa

#### Variables Temporales Derivadas:
6. **Day**: Día del mes (1-31)
7. **Month**: Mes del año (1-12)
8. **Hour**: Hora del día (0-23)
9. **Minute**: Minuto de la hora (0, 10, 20, 30, 40, 50)
10. **Day of Week**: Día de la semana (1-7)
11. **Quarter of Year**: Trimestre del año (1-4)
12. **Day of Year**: Día del año (1-365)

#### Variables Target:
- **Zone 1 Power Consumption** (kW)
- **Zone 2 Power Consumption** (kW)
- **Zone 3 Power Consumption** (kW)

*Nota: Para este proyecto nos enfocamos en predecir Zone 2 Power Consumption*

### 2.4 Construcción del Modelo
**¿Cuándo y cómo crear/actualizar modelos?**

- **Frecuencia de entrenamiento:** Inicial para el proyecto académico
- **En producción:** Reentrenamiento mensual o cuando MAPE > 15%
- **Pipeline de datos:**
  1. Limpieza de valores faltantes
  2. Detección y tratamiento de outliers (IQR method)
  3. Imputación de valores faltantes con mediana
  4. Ingeniería de features temporales
  5. Normalización MinMax (rango 1-2)
  6. Split temporal 80/20 train/test

---

## 3. PREDECIR (Machine Learning Tasks)

### 3.1 Tareas ML
**Definir inputs, output de predicción y tipo de algoritmo**

- **Tipo de tarea:** Regresión (predicción de valores continuos)
- **Input:** Variables climáticas + características temporales
- **Output:** Consumo de energía en kW para Zone 2
- **Algoritmos evaluados:**
  1. Random Forest Regressor
  2. ElasticNet
  3. Gradient Boosting Regressor
  4. XGBoost Regressor
  5. Support Vector Regressor (SVR)

### 3.2 Decisiones
**¿Cómo usaremos las predicciones para crear valor?**

- **Planificación de demanda:** Ajustar generación eléctrica anticipadamente
- **Gestión de recursos:** Optimizar distribución entre zonas
- **Alertas tempranas:** Notificar picos de demanda predichos
- **Optimización de costos:** Reducir compra de energía en horarios pico
- **Mantenimiento preventivo:** Planificar mantenimiento en períodos de baja demanda

### 3.3 Haciendo Predicciones
**Timing y restricciones de las predicciones**

- **Latencia requerida:** < 5 segundos
- **Frecuencia:** Predicciones cada 10 minutos (sincronizado con mediciones)
- **Horizonte de predicción:**
  - Corto plazo: próximas 24 horas
  - Mediano plazo: próxima semana (futuro trabajo)
- **Restricciones:**
  - Disponibilidad de datos climáticos en tiempo real
  - Capacidad computacional para inferencia rápida

### 3.4 Evaluación Offline
**Métricas para evaluación pre-producción**

#### Métricas Principales:
1. **RMSE (Root Mean Squared Error):**
   - Penaliza errores grandes
   - Mismas unidades que el target (kW)
   - Meta: RMSE < 4,000 kW

2. **MAPE (Mean Absolute Percentage Error):**
   - Error porcentual, fácil de interpretar
   - Meta: MAPE < 12%

3. **MSE (Mean Squared Error):**
   - Métrica cuadrática estándar
   - Para comparación entre modelos

#### Validación:
- **Repeated K-Fold Cross-Validation** (5 folds, 3 repeticiones)
- **Hold-out temporal** (80% train, 20% test)
- Respeto de temporalidad de los datos

---

## 4. EVALUAR (Live Monitoring)

### 4.1 Monitoreo en Vivo
**Métricas y métodos para evaluar el modelo en producción**

#### Métricas de Rendimiento:
- **MAPE en tiempo real:** Comparar predicciones vs valores reales
- **RMSE rolling (ventana 24h):** Detectar degradación del modelo
- **Bias detection:** Verificar si el modelo sobre/subestima sistemáticamente

#### Métricas de Calidad de Datos:
- **Datos faltantes:** Porcentaje de missing values en inputs
- **Drift de features:** Distribución de variables vs datos de entrenamiento
- **Outliers rate:** Frecuencia de valores atípicos

#### Alertas y Umbrales:
- 🟢 MAPE < 12%: Rendimiento óptimo
- 🟡 MAPE 12-15%: Revisar modelo
- 🔴 MAPE > 15%: Reentrenamiento urgente

#### Sistema de Monitoreo:
- Dashboard en tiempo real con métricas clave
- Logging de predicciones y errores
- Comparación semanal de rendimiento
- A/B testing para nuevas versiones del modelo

---

## 5. CONSIDERACIONES ADICIONALES

### Riesgos y Limitaciones:
- **Data drift:** Patrones de consumo pueden cambiar (nuevas industrias, población)
- **Eventos extremos:** El modelo puede no capturar eventos climáticos inusuales
- **Granularidad temporal:** 10 minutos puede ser insuficiente para picos súbitos
- **Variables faltantes:** No incluye días festivos, eventos especiales, etc.

### Mejoras Futuras:
- Incorporar variables de calendario (festivos, vacaciones)
- Incluir datos históricos de consumo (lags)
- Modelos específicos por zona de distribución
- Predicción multi-horizonte (1h, 6h, 24h)
- Incorporar datos de precios de energía

### Ethical Considerations:
- Privacidad: Datos agregados, sin información de consumidores individuales
- Transparencia: Modelo interpretable para stakeholders
- Equidad: Predicciones justas para todas las zonas de distribución

---

## 6. REFERENCIAS

- Dataset: https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city
- Metodología ML Canvas: https://ignaciogavilan.com/metodologia-para-machine-learning-ii-machine-learning-canvas/
- Paper: "Comparison of Machine Learning Algorithms for the Power Consumption Prediction" - Salam & El Hibaoui

---

**Fecha de creación:** Octubre 2025
**Equipo 43 - MLOps**
**Tecnológico de Monterrey**

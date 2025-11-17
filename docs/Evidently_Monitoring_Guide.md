# Guía de Monitoreo con Evidently.ai

## Descripción General

Esta guía explica cómo usar Evidently.ai para el monitoreo integral de data drift y seguimiento de rendimiento del modelo en el proyecto MLOps.

**Implementado por**: Fields (Equipo 43)
**Fecha**: Noviembre 2025

## ¿Qué es Evidently?

Evidently es una biblioteca Python de código abierto para evaluar, probar y monitorear modelos de ML en producción. Ayuda a detectar:

- **Data Drift**: Cambios en las distribuciones de features a lo largo del tiempo
- **Target Drift**: Cambios en la distribución de la variable objetivo
- **Problemas de Calidad de Datos**: Valores faltantes, inconsistencias de tipo, outliers
- **Degradación del Rendimiento del Modelo**: Calidad de predicciones a lo largo del tiempo

## Instalación

```bash
# Activar ambiente virtual
source venv/bin/activate

# Instalar Evidently
pip install evidently

# Verificar instalación
python -c "import evidently; print(evidently.__version__)"
```

## Inicio Rápido

### Ejecutar el Script de Monitoreo

```bash
python scripts/monitor_data_drift_evidently.py
```

Esto realizará:
1. Cargar datos de referencia (conjunto de entrenamiento)
2. Generar datos de monitoreo (con drift simulado)
3. Crear reportes comprehensivos
4. Ejecutar tests automatizados
5. Extraer métricas de drift

### Ver Reportes

Los reportes se guardan en `reports/evidently/`:

```bash
# Abrir en navegador (macOS)
open reports/evidently/data_drift_report.html

# O usar Python
python -m http.server 8080
# Navegar a: http://localhost:8080/reports/evidently/
```

## Reportes Generados

### 1. Reporte de Data Drift

**Archivo**: `data_drift_report.html`

**Contiene**:
- Detección de drift a nivel de dataset (drift general: Sí/No)
- Análisis de drift por feature con tests estadísticos
- Comparaciones de distribución (histogramas, gráficos KDE)
- Scores de drift y p-values
- Visualizaciones interactivas

**Tests Estadísticos Utilizados**:
- **Kolmogorov-Smirnov (KS)** para features numéricos
- **Chi-cuadrado** para features categóricos
- **Umbral**: p-value < 0.05 indica drift

**Ejemplo de Salida**:
```
Dataset Drift: Detectado
Features con Drift: 3/12 (25%)
- Temperature: KS statistic = 0.45, p-value = 0.001 [DRIFT]
- Humidity: KS statistic = 0.12, p-value = 0.234 [OK]
- WindSpeed: KS statistic = 0.08, p-value = 0.512 [OK]
```

### 2. Reporte de Calidad de Datos

**Archivo**: `data_quality_report.html`

**Contiene**:
- Análisis de valores faltantes
- Consistencia de tipos de datos
- Validación de rangos de valores
- Detección de duplicados
- Matrices de correlación

**Caso de Uso**: Identificar problemas en el pipeline de datos antes del análisis de drift

### 3. Suite de Tests

**Archivo**: `drift_test_suite.html`

**Contiene**:
- Tests automatizados pass/fail
- Resumen de resultados de tests
- Razones detalladas de fallos
- Alertas y recomendaciones

**Caso de Uso**: Integración CI/CD para detección automática de drift

### 4. Métricas JSON

**Archivo**: `data_drift_report.json`

**Contiene**:
- Métricas de drift legibles por máquina
- Acceso programático a resultados
- Integración con sistemas de monitoreo

**Caso de Uso**: Alertas, logging, integración con dashboards

## Configuración del Script

### Tipos de Simulación de Drift

Editar `scripts/monitor_data_drift_evidently.py` para cambiar el tipo de drift:

```python
# Línea ~390
monitoring_data = generate_monitoring_data(
    validation_data,
    drift_type="temperature"  # Opciones: 'temperature', 'humidity', 'mixed', 'none'
)
```

**Opciones**:
- `"temperature"`: Desplazamiento de +5°C (simula cambio climático)
- `"humidity"`: Incremento de +15% (cambio estacional)
- `"mixed"`: Múltiples features con drift simultáneamente
- `"none"`: Sin drift (test de control)

### Configuración de Tests Estadísticos

```python
# Línea ~210
report = Report(metrics=[
    DataDriftPreset(
        stattest='ks',           # Opciones: 'ks', 'wasserstein', 'psi'
        stattest_threshold=0.05  # Umbral de p-value
    ),
    ...
])
```

**Tests Disponibles**:
- `ks`: Kolmogorov-Smirnov (por defecto, recomendado)
- `wasserstein`: Distancia de Wasserstein
- `psi`: Índice de Estabilidad Poblacional
- `chisquare`: Chi-cuadrado (para categóricos)

### Mapeo de Columnas

El script detecta automáticamente:

**Features Numéricos**:
- Temperature, Humidity, WindSpeed
- GeneralDiffuseFlows, DiffuseFlows
- PowerConsumption_Zone1, PowerConsumption_Zone3

**Features Categóricos**:
- Day, Month, Hour, Minute
- DayWeek, QuarterYear, DayYear

**Target**:
- PowerConsumption_Zone2

Modificar en la función `create_column_mapping()` si es necesario.

## Integración con Producción

### 1. Monitoreo Programado

Crear un cron job o programador:

```bash
# Ejecutar diariamente a las 2 AM
0 2 * * * cd /path/to/MNA_MLOps && /path/to/venv/bin/python scripts/monitor_data_drift_evidently.py
```

### 2. Integración CI/CD

Agregar a `.github/workflows/monitor.yml`:

```yaml
name: Data Drift Monitoring

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:     # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install evidently
      - name: Run monitoring
        run: python scripts/monitor_data_drift_evidently.py
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: evidently-reports
          path: reports/evidently/
```

### 3. Sistema de Alertas

Extraer métricas y enviar alertas:

```python
import json

# Cargar métricas de drift
with open('reports/evidently/data_drift_report.json') as f:
    metrics = json.load(f)

# Verificar drift
if metrics['dataset_drift_detected']:
    # Enviar alerta (email, Slack, PagerDuty, etc.)
    send_alert(
        title="¡Data Drift Detectado!",
        features=metrics['drifted_features'],
        severity="high"
    )
```

## Comparación: Test K-S vs. Evidently

| Aspecto | Test K-S (Actual) | Evidently.ai |
|--------|-------------------|--------------|
| **Complejidad** | Simple, test único | Suite comprehensiva |
| **Visualización** | Gráficos manuales | Reportes HTML interactivos |
| **Features** | Variable única | Todas las features analizadas |
| **Reportes** | Código custom necesario | Reportes automatizados |
| **Listo para Producción** | Bueno para casos simples | Nivel empresarial |
| **Tiempo de Setup** | 30 min | 1-2 horas |
| **Mantenimiento** | Bajo | Bajo (librería bien mantenida) |

**Recomendación**: ¡Usar ambos!
- Test K-S para verificaciones rápidas
- Evidently para análisis comprehensivo y monitoreo en producción

## Guía de Interpretación

### Dataset Drift Detectado

**Qué significa**:
- La distribución general de datos ha cambiado significativamente
- Múltiples features pueden haber experimentado drift
- El rendimiento del modelo puede degradarse

**Acciones**:
1. Revisar scores de drift por feature
2. Investigar causa raíz (¿pipeline de datos? ¿cambios del mundo real?)
3. Considerar reentrenamiento del modelo
4. Actualizar preprocesamiento de features si es necesario

### Drift en Feature Específico

**Ejemplo**: Drift detectado en Temperature

**Causas Posibles**:
- Cambios estacionales (esperado)
- Cambio climático (tendencia a largo plazo)
- Problema de calibración del sensor (calidad de datos)
- Cambio en distribución geográfica (deployment)

**Acciones**:
1. Determinar si el drift es esperado o anómalo
2. Si es esperado: Reentrenar modelo con datos recientes
3. Si es anómalo: Corregir problema en el pipeline de datos

### Sin Drift Detectado

**Qué significa**:
- La distribución de datos es estable
- El modelo debe funcionar consistentemente
- No se requiere acción inmediata

**Mejor Práctica**:
- Continuar monitoreo regular
- Archivar reportes para cumplimiento
- Rastrear tendencias a lo largo del tiempo

## Solución de Problemas

### Error de Importación: evidently

```bash
pip install evidently
# o
pip install evidently==0.7.14  # Versión específica
```

### Problemas de Memoria con Datasets Grandes

```python
# Muestrear los datos antes del análisis
reference_sample = reference_df.sample(n=10000, random_state=42)
current_sample = current_df.sample(n=10000, random_state=42)
```

### Reportes No Abren

```bash
# Iniciar servidor local
cd reports/evidently
python -m http.server 8000
# Abrir: http://localhost:8000/data_drift_report.html
```

### Errores de Parseo JSON

Asegurar que se usa una versión reciente de Evidently:

```bash
pip install --upgrade evidently
```

## Uso Avanzado

### Métricas Personalizadas

```python
from evidently.metrics import ColumnDriftMetric

report = Report(metrics=[
    ColumnDriftMetric(column_name='Temperature'),
    ColumnDriftMetric(column_name='Humidity'),
    # Agregar más métricas personalizadas
])
```

### Múltiples Ventanas de Referencia

```python
# Comparar contra múltiples períodos históricos
for period in ['semana1', 'semana2', 'semana3']:
    reference = load_period_data(period)
    report.run(reference_data=reference, current_data=current)
    report.save_html(f'drift_report_{period}.html')
```

### Integración con MLflow

```python
import mlflow

# Registrar métricas de drift en MLflow
with mlflow.start_run():
    mlflow.log_metric("dataset_drift", int(drift_detected))
    mlflow.log_metric("num_drifted_features", num_drifted)
    mlflow.log_artifact("reports/evidently/data_drift_report.html")
```

## Mejores Prácticas

1. **Selección de Baseline**
   - Usar datos de entrenamiento como referencia
   - Actualizar baseline después de reentrenar
   - Considerar patrones estacionales

2. **Frecuencia de Monitoreo**
   - Tiempo real: Cada batch de predicciones
   - Diario: Para aplicaciones estables
   - Semanal: Para datos de cambio lento

3. **Ajuste de Umbrales**
   - Comenzar con p-value < 0.05
   - Ajustar basado en tasa de falsos positivos
   - Considerar impacto del negocio

4. **Retención de Reportes**
   - Archivar reportes para cumplimiento
   - Mantener historial de análisis de tendencias
   - Guardar JSON para acceso programático

5. **Planificación de Acciones**
   - Definir procedimientos de escalación
   - Automatizar triggers de reentrenamiento
   - Documentar proceso de investigación

## Recursos

- [Documentación Evidently](https://docs.evidentlyai.com/)
- [Evidently GitHub](https://github.com/evidentlyai/evidently)
- [Tutorial: ML Monitoring](https://www.evidentlyai.com/blog/ml-monitoring-do-i-need-data-drift)
- [Tests Estadísticos Explicados](https://docs.evidentlyai.com/reference/all-tests)

## Soporte

Para problemas o preguntas:
1. Revisar documentación de Evidently
2. Consultar esta guía
3. Contactar miembros del Equipo 43

---

**Equipo 43** - Tecnológico de Monterrey
**Proyecto MLOps - Entrega Final**
**Noviembre 2025**

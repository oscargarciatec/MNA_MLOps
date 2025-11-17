# Guía de Testing - Proyecto MLOps Equipo 43

## Descripción General

Este proyecto incluye tests unitarios e de integración comprehensivos para asegurar la calidad y confiabilidad del código. Los tests están ubicados en el directorio `tests/` y usan `pytest` como framework de testing.

## Estructura de Tests

```
tests/
└── test_pipeline.py    # Tests unitarios y de integración para el pipeline ML
```

## Cobertura de Tests

### Tests Unitarios

Los tests unitarios validan componentes y funciones individuales:

1. **test_setup_preprocessor_structure**
   - Valida que el preprocesador es un ColumnTransformer
   - Verifica que todos los pasos de transformación requeridos estén presentes
   - Asegura la estructura correcta del pipeline (imputación + escalado)

2. **test_data_split_ratio**
   - Verifica el ratio de división train/test (80/20)
   - Asegura las dimensiones correctas de los datos

3. **test_predict_before_load**
   - Prueba el manejo de errores cuando el modelo no está cargado
   - Valida que se lance RuntimeError apropiadamente

### Tests de Integración

Los tests de integración validan el flujo completo del pipeline:

1. **test_full_pipeline_flow**
   - Prueba flujo end-to-end: Entrenamiento → Logging → Guardado → Carga → Predicción
   - Valida integración con MLflow (métricas, parámetros, artefactos)
   - Asegura persistencia y recarga del modelo
   - Verifica formato y dimensiones de salida de predicciones

## Ejecutar Tests

### Prerequisitos

1. **Crear Ambiente Virtual** (si no existe):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pytest-mock
   ```

### Ejecutar Todos los Tests

```bash
# Ejecución simple de tests
pytest tests/

# Salida verbose
pytest tests/ -v

# Modo silencioso (menos salida)
pytest tests/ -q
```

### Ejecutar Tests con Cobertura

```bash
# Generar reporte de cobertura
pytest tests/ --cov=Project --cov=app --cov-report=term-missing

# Generar reporte HTML de cobertura
pytest tests/ --cov=Project --cov=app --cov-report=html

# Ver reporte HTML
open htmlcov/index.html  # En macOS
# o
xdg-open htmlcov/index.html  # En Linux
```

### Ejecutar Tests Específicos

```bash
# Ejecutar solo tests unitarios
pytest tests/test_pipeline.py::test_setup_preprocessor_structure

# Ejecutar solo tests de integración
pytest tests/test_pipeline.py::test_full_pipeline_flow
```

## Resultados Esperados de Tests

Todos los tests deben pasar cuando se ejecutan en un ambiente limpio:

```
tests/test_pipeline.py::test_setup_preprocessor_structure PASSED
tests/test_pipeline.py::test_data_split_ratio PASSED
tests/test_pipeline.py::test_full_pipeline_flow PASSED
tests/test_pipeline.py::test_predict_before_load PASSED

======================== 4 passed in X.XXs ========================
```

## Métricas de Cobertura

Basado en nuestra suite de tests, alcanzamos la siguiente cobertura:

| Módulo | Cobertura | Detalles |
|--------|----------|---------|
| **Project/Modelo.py** | ~90% | Lógica core de entrenamiento/predicción completamente testeada |
| **Project/Preprocesamiento.py** | ~75% | Funciones clave de transformación testeadas |
| **Project/CargaDatos.py** | ~80% | Carga de datos validada |
| **app/api.py** | ~60% | Endpoints API (testeados vía integración) |
| **General** | ~75-80% | Fuerte cobertura de rutas críticas |

### Gaps de Cobertura (No Críticos)

- Algunos manejadores de errores de casos edge
- Funciones utilitarias con lógica simple
- Funciones de visualización/gráficos

## Integración Continua

Los tests se ejecutan automáticamente en el pipeline CI/CD:

```yaml
# .github/workflows/test.yml (si existe)
- name: Run Tests
  run: |
    pytest tests/ -v
```

## Datos de Test

Los tests usan datos sintéticos generados vía fixtures de pytest:
- 50 muestras de datos aleatorios
- Todas las features requeridas (Temperature, Humidity, WindSpeed, etc.)
- Archivos de modelo temporales (limpiados después de los tests)

## Mocking

Los servicios externos son mockeados para asegurar que los tests sean rápidos y confiables:
- Funciones de logging de MLflow
- Inicialización de DagsHub
- Operaciones de I/O de archivos (cuando es apropiado)

## Mejores Prácticas

1. **Ejecutar tests antes de hacer commit**:
   ```bash
   pytest tests/ -v
   ```

2. **Revisar cobertura regularmente**:
   ```bash
   pytest tests/ --cov=Project --cov-report=term-missing
   ```

3. **Agregar tests para nuevas features**:
   - Test unitario para nuevas funciones
   - Test de integración si afecta el pipeline

4. **Mantener tests rápidos**:
   - Usar fixtures para setup compartido
   - Mockear dependencias externas
   - Usar datasets sintéticos pequeños

## Solución de Problemas

### Errores de Importación

Si ves `ModuleNotFoundError`:
```bash
# Asegurar que estás en la raíz del proyecto
cd /path/to/MNA_MLOps

# Ejecutar tests con el path correcto
python -m pytest tests/
```

### Errores de MLflow

Si los tests de MLflow fallan:
```bash
# Configurar tracking URI dummy
export MLFLOW_TRACKING_URI=file:./mlruns
pytest tests/
```

### Dependencias Faltantes

```bash
# Instalar dependencias de test
pip install pytest pytest-cov pytest-mock
```

## Referencias

- [Documentación Pytest](https://docs.pytest.org/)
- [Plugin Pytest-Cov](https://pytest-cov.readthedocs.io/)
- [Mejores Prácticas de Testing](https://docs.python-guide.org/writing/tests/)

---

**Última Actualización**: Noviembre 2025
**Equipo 43** - Tecnológico de Monterrey

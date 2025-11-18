# 🧪 Validación de Reproducibilidad

La reproducibilidad es un componente crítico en cualquier pipeline de Machine Learning orientado a producción. Para garantizar que los resultados del modelo sean **consistentes**, independientemente del entorno en el que se ejecuten, se diseñó un proceso completo de validación basado en contenedores Docker.

Este proceso asegura que:

- El modelo entrenado sea **determinístico** bajo las mismas versiones de librerías.  
- El pipeline completo pueda ejecutarse en un entorno limpio y aislado.  
- Las métricas, parámetros y artefactos generados sean equivalentes a los del entrenamiento original.

---

## 📦 Enfoque de Validación

El equipo desarrolló un contenedor Docker con:

- Las **mismas dependencias** y versiones utilizadas en el proyecto base.  
- El **pipeline completo de MLOps**, incluyendo preprocesamiento, entrenamiento y evaluación.  
- Scripts adicionales para comparar:
  - Parámetros del modelo  
  - Métricas registradas  
  - Tamaño del modelo serializado  
  - Artefactos generados  

Al finalizar la ejecución:

- Si se detecta alguna diferencia significativa, el sistema **falla la validación** e imprime el detalle de la discrepancia.  
- Si todo coincide, el sistema imprime:  

```
REPRODUCIBILITY PASSED!
```

---

## 🐳 Dockerfile para Reproducibilidad

Este Dockerfile crea un entorno completamente aislado y limpio para ejecutar el pipeline de extremo a extremo.


Incluye:

- Instalación de dependencias base  
- Copia del proyecto  
- Ejecución automática del pipeline  
- Verificación final de reproducibilidad  

---

## 🛠️ Makefile para Ejecución Automática

El Makefile orquesta la creación del contenedor, la construcción de la imagen y la ejecución del flujo completo de verificación.

El target principal es `full`, que ejecuta la validación completa.

---

## ▶️ Ejecución del Pipeline de Reproducibilidad

Una vez que el **Dockerfile** y el **Makefile** se encuentran en la carpeta `/reproducibility`, basta con ejecutar:

```bash
make full
```

Este comando:

1. Construye la imagen Docker correspondiente.  
2. Carga dentro del contenedor los datos necesarios.  
3. Ejecuta el pipeline completo dentro del contenedor.  
4. Compara los artefactos con los resultados oficiales registrados en MLflow.  
5. Imprime el resultado de la validación.

---

## 📁 Ubicación del Desarrollo

Todo el proceso descrito se encuentra en:

```
/reproducibility
```

> Nota: Esta carpeta se incluye únicamente con fines demostrativos.  
> En un entorno productivo real, la duplicación de artefactos y archivos debe evitarse mediante:
> - DVC  
> - Pipelines automatizados  
> - Builds reproducibles basados en CI/CD  
> - Storage centralizado de datasets y modelos 

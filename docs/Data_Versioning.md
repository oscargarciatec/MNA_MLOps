# Guía de Versionamiento de Datos

## Equipo 43 - MLOps Project

Este documento describe el proceso de versionamiento de datos para el proyecto de predicción de consumo energético de Tetouan.

---

## 1. Estrategia de Versionamiento

### 1.1 Herramientas Utilizadas

#### Git (Control de Versiones de Código)
- **Propósito**: Versionar código, notebooks, y documentación
- **Repositorio**: GitHub
- **Archivos versionados**:
  - Notebooks (`.ipynb`)
  - Scripts de Python (`.py`)
  - Documentación (`.md`)
  - Configuración del proyecto

#### DVC (Data Version Control)
- **Propósito**: Versionar datasets grandes
- **Storage backend**: Puede ser local, Google Drive, S3, etc. (En este caso por problemas técnicos se está trabajando local cada quien)
- **Archivos versionados**:
  - Datasets crudos (raw)
  - Datasets procesados (processed)
  - Modelos entrenados (`.pkl`, `.joblib`)

---

## 2. Estructura de Directorios

```
MNA_MLOps/
│
├── data/
│   ├── raw/                          # Datos originales (inmutables)
│   │   ├── power_tetouan_city_original.csv
│   │   └── power_tetouan_city_modified.csv
│   │
│   └── processed/                    # Datos procesados (versionados)
│       └── power_tetouan_city_processed.csv
│
├── models/                           # Modelos entrenados (futuro)
│   └── [modelos serializados]
│
├── notebooks/
│   └── Fase 1_Equipo43.ipynb
│
├── docs/
│   ├── ML_Canvas.md
│   └── Data_Versioning.md
│
├── .gitignore                        # Archivos excluidos de Git
├── .dvc/                             # Configuración DVC (si se usa)
├── .dvcignore                        # Archivos excluidos de DVC
└── README.md
```

---

## 3. Configuración de Git

### 3.1 Inicializar Repositorio

```bash
# En el directorio raíz del proyecto
git init
git add .
git commit -m "Initial commit: Project structure"
```

### 3.2 Archivo .gitignore

Crear un archivo `.gitignore` para excluir archivos pesados y temporales:

```gitignore
# Datos crudos y procesados (versionar con DVC)
data/raw/*.csv
data/processed/*.csv

# Modelos entrenados
models/*.pkl
models/*.joblib
models/*.h5

# Notebooks checkpoints
.ipynb_checkpoints/
*/.ipynb_checkpoints/*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# DVC
/data/.dvc
```

---

## 4. Versionamiento con DVC

### 4.1 Instalación de DVC

```bash
pip install dvc
# O con conda:
conda install -c conda-forge dvc
```

### 4.2 Inicializar DVC

```bash
# En el directorio raíz del proyecto
dvc init
git add .dvc .dvcignore
git commit -m "Initialize DVC"
```

### 4.3 Configurar Storage Remoto

#### Opción 1: Local (para desarrollo)
```bash
mkdir -p /path/to/dvc-storage
dvc remote add -d local /path/to/dvc-storage
```

#### Opción 2: Google Drive
```bash
dvc remote add -d gdrive gdrive://YOUR_FOLDER_ID
```

#### Opción 3: AWS S3
```bash
dvc remote add -d s3remote s3://your-bucket/path
dvc remote modify s3remote region us-west-2
```

```bash
# Guardar configuración
git add .dvc/config
git commit -m "Configure DVC remote storage"
```

### 4.4 Agregar Datos a DVC

```bash
# Versionar datos crudos
dvc add data/raw/power_tetouan_city_original.csv
dvc add data/raw/power_tetouan_city_modified.csv

# Versionar datos procesados
dvc add data/processed/power_tetouan_city_processed.csv

# Commit archivos .dvc al repositorio Git
git add data/raw/*.csv.dvc data/processed/*.csv.dvc .gitignore
git commit -m "Track datasets with DVC"

# Subir datos al storage remoto
dvc push
```

### 4.5 Recuperar Datos con DVC

Cuando otro miembro del equipo clona el repositorio:

```bash
# Clonar repositorio
git clone <repository-url>
cd MNA_MLOps

# Descargar datos
dvc pull
```

---

## 5. Convenciones de Versionamiento

### 5.1 Nomenclatura de Archivos

#### Datasets
```
# Formato: {nombre}_{version}_{fecha}.csv
power_tetouan_city_processed_v1_20251009.csv
power_tetouan_city_processed_v2_20251015.csv
```

#### Modelos
```
# Formato: {algoritmo}_{version}_{metrica}.pkl
random_forest_v1_rmse3715.pkl
xgboost_v2_rmse3200.pkl
```

### 5.2 Tags en Git

Usar tags para marcar versiones importantes:

```bash
# Crear tag para Fase 1
git tag -a v1.0-fase1 -m "Fase 1: EDA y Modelado Inicial"
git push origin v1.0-fase1

# Crear tag para dataset procesado
git tag -a data-v1.0 -m "Dataset procesado - Versión 1.0"
git push origin data-v1.0
```

### 5.3 Commits Descriptivos

Usar convenciones de commit messages:

```bash
# Formato: [tipo] descripción breve

# Tipos:
# - feat: Nueva funcionalidad
# - fix: Corrección de bug
# - data: Cambios en datos
# - model: Cambios en modelos
# - docs: Documentación
# - refactor: Refactorización de código

# Ejemplos:
git commit -m "[data] Add processed dataset v1.0 with IQR outlier treatment"
git commit -m "[model] Add XGBoost and SVR models for comparison"
git commit -m "[docs] Update ML Canvas with production monitoring section"
```

---

## 6. Proceso de Versionamiento del Dataset

### 6.1 Dataset Original (Inmutable)

Los datos originales **NUNCA** se modifican:

```bash
# Estos archivos se descargan UNA VEZ y no se modifican
data/raw/power_tetouan_city_original.csv
data/raw/power_tetouan_city_modified.csv
```

### 6.2 Dataset Procesado (Versionado)

Cada vez que se genera un nuevo dataset procesado:

```bash
# 1. Ejecutar notebook hasta la celda de guardado
# 2. Se genera: data/processed/power_tetouan_city_processed.csv

# 3. Versionar con DVC
dvc add data/processed/power_tetouan_city_processed.csv

# 4. Commit en Git
git add data/processed/power_tetouan_city_processed.csv.dvc
git commit -m "[data] Update processed dataset - Applied temporal feature engineering"

# 5. Push datos a DVC remote
dvc push

# 6. Push commits a GitHub
git push origin main
```

### 6.3 Registro de Versiones (CHANGELOG)

Mantener un archivo `CHANGELOG.md` en `docs/`:

```markdown
# Changelog - Datasets

## [v1.1] - 2025-10-15
### Changed
- Aplicado feature scaling MinMaxScaler (1-2)
- Agregadas 7 features temporales derivadas

### Fixed
- Corregidos 1,045 timestamps duplicados
- Tratados outliers con método IQR + mediana local

## [v1.0] - 2025-10-09
### Added
- Dataset inicial procesado
- Imputación de valores faltantes con mediana
- Eliminación de columna mixed_type_col
```

---

## 7. Workflow Completo de Versionamiento

### Escenario 1: Primera vez (Setup Inicial)

```bash
# 1. Inicializar repositorio
git init
git add .
git commit -m "Initial commit"

# 2. Crear repositorio en GitHub
# 3. Conectar con remoto
git remote add origin https://github.com/usuario/MNA_MLOps.git
git push -u origin main

# 4. Inicializar DVC (opcional)
dvc init
git add .dvc .dvcignore
git commit -m "Initialize DVC"

# 5. Configurar DVC remote
dvc remote add -d storage /path/to/storage
git add .dvc/config
git commit -m "Configure DVC remote"

# 6. Versionar datos
dvc add data/raw/*.csv
dvc add data/processed/*.csv
git add data/**/*.dvc .gitignore
git commit -m "Track datasets with DVC"
dvc push
git push
```

### Escenario 2: Actualizar Dataset Procesado

```bash
# 1. Ejecutar notebook con nuevas transformaciones
# 2. Se genera nuevo archivo en data/processed/

# 3. Actualizar DVC tracking
dvc add data/processed/power_tetouan_city_processed.csv

# 4. Commit cambios
git add data/processed/*.dvc
git commit -m "[data] Update processed dataset v1.1 - Add temporal features"

# 5. Push
dvc push
git push
```

### Escenario 3: Clonar Proyecto (Nuevo Miembro del Equipo)

```bash
# 1. Clonar repositorio
git clone https://github.com/usuario/MNA_MLOps.git
cd MNA_MLOps

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar datos con DVC (si aplica)
dvc pull

# 5. Ejecutar notebook
jupyter notebook
```

---

## 8. Mejores Prácticas

### DO (Hacer)

1. **Versionar cambios incrementales**: Commit frecuente con mensajes descriptivos
2. **Documentar transformaciones**: Cada cambio en datos debe documentarse
3. **Usar branches para experimentos**:
   ```bash
   git checkout -b feature/new-preprocessing
   ```
4. **Mantener datos raw inmutables**: Nunca modificar archivos en `data/raw/`
5. **Sincronizar DVC y Git**: Siempre hacer `dvc push` después de `dvc add`

### DON'T (No hacer)

1. **No versionar archivos grandes con Git**: Usar DVC para CSVs > 10MB
2. **No commitear datos sensibles**: Verificar que `.gitignore` esté bien configurado
3. **No sobrescribir datos raw**: Siempre trabajar con copias en `processed/`
4. **No olvidar documentar**: Cada versión debe tener un registro de cambios
5. **No usar paths absolutos**: Usar paths relativos para portabilidad

---

## 9. Troubleshooting

### Problema: Archivo CSV muy grande para Git
```bash
# Solución: Usar DVC
dvc add data/large_file.csv
git add data/large_file.csv.dvc
```

### Problema: Conflictos en archivos .dvc
```bash
# Solución: Resolver manualmente y actualizar
git checkout --ours data/file.csv.dvc  # O --theirs
dvc checkout
```

### Problema: DVC push falla
```bash
# Verificar configuración de remote
dvc remote list
dvc remote -v

# Verificar conectividad
dvc status -c
```

---

## 10. Recursos Adicionales

- **DVC Documentation**: https://dvc.org/doc
- **Git Best Practices**: https://git-scm.com/book/en/v2
- **Semantic Versioning**: https://semver.org/
- **Conventional Commits**: https://www.conventionalcommits.org/

---

**Última actualización**: Octubre 2025
**Equipo 43 - Tecnológico de Monterrey**

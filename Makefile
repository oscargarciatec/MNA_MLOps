#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = MNA_MLOps
PYTHON_VERSION = 3.13.7
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format





## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	@bash -c "if [ ! -z `which virtualenvwrapper.sh` ]; then source `which virtualenvwrapper.sh`; mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); else mkvirtualenv.bat $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); fi"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
=======
.PHONY: help install install-dev clean lint format test run-pipeline train evaluate deploy

# Variables
PYTHON := python
PIP := pip
PROJECT_NAME := prediccion-energia-tetouan

help: ## Mostrar los comandos disponibles
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias del proyecto
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

install-dev: ## Instalar dependencias de desarrollo
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

clean: ## Limpiar cachés y archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

lint: ## Ejecutar linting
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Formatear código
	black src/ tests/
	isort src/ tests/

test: ## Ejecutar pruebas unitarias con cobertura
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# MLOps Pipeline Comandos	
setup-dvc: ## Inicializar DVC y configurar almacenamiento remoto
	dvc init --no-scm
	dvc remote add -d local_storage data/dvc_storage

data-download: ## Descargar y preparar datos
	$(PYTHON) scripts/download_data.py

data-process: ## Procesar datos en bruto
	dvc repro data_processing

train: ## Entrenar modelos
	$(PYTHON) src/main_pipeline.py --stage train
	dvc repro model_training

evaluate: ## Evaluar modelos
	$(PYTHON) src/main_pipeline.py --stage evaluate
	dvc repro model_evaluation

run-pipeline: ## Ejecutar pipeline completo
	$(PYTHON) src/main_pipeline.py --stage all

# MLflow Commands
mlflow-ui: ## Iniciar UI de MLflow
	mlflow ui --host 0.0.0.0 --port 5000

# Jupyter Commands
jupyter-lab: ## Iniciar Jupyter Lab
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

jupyter-notebook: ## Iniciar Jupyter Notebook
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser

# Docker Commands (for future deployment)
docker-build: ## Build Docker image
	docker build -t $(PROJECT_NAME) .

docker-run: ## Run Docker container
	docker run -p 8000:8000 $(PROJECT_NAME)

# Data versioning
data-add: ## Add data to DVC tracking
	dvc add data/raw/
	dvc add data/processed/

data-push: ## Push data to remote storage
	dvc push

data-pull: ## Pull data from remote storage
	dvc pull

# Model registry
model-register: ## Register best model in MLflow
	$(PYTHON) scripts/register_model.py

# Deployment
deploy-local: ## Deploy model locally
	$(PYTHON) scripts/deploy_local.py

# Development
dev-setup: install-dev setup-dvc ## Complete development setup
	echo "Development environment ready!"

# Quality checks
quality-check: lint test ## Run all quality checks
	echo "Quality checks completed!"
>>>>>>> main

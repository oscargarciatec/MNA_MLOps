IMAGE_NAME = reproducibility_image
MLFLOW_TRACKING_URI = https://dagshub.com/garc1a0scar/mna-mlops-team43.mlflow
OUTPUT_DIR = outputs

.PHONY: build extract train compare full

build:
	docker build -t $(IMAGE_NAME) .

# 1) Extraer métricas desde MLflow (reference) → outputs/reference_*.json
extract: build
	mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-e MLFLOW_TRACKING_URI=$(MLFLOW_TRACKING_URI) \
		-v $(OUTPUT_DIR):/app/outputs \
		$(IMAGE_NAME) \
		Project/extract_reference_from_mflow.py

# 2) Entrenar pipeline y producir test model + test metrics
train: build
	docker run --rm \
		-v $(OUTPUT_DIR):/app/outputs \
		-v models:/app/models \
		$(IMAGE_NAME) \
		Project/run_full_pipeline.py --model_path_override "/app/models/test_model_pipeline.joblib"

# 3) Comparar reference vs test
compare: build
	docker run --rm \
		-v $(OUTPUT_DIR):/app/outputs \
		-v models:/app/models \
		$(IMAGE_NAME) \
		Project/compare_models.py

full: extract train compare

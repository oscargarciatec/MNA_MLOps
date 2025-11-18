import mlflow
import joblib
import json
import os

RUN_ID = "3ec46a1ffdd548fb84e72267ed1fb30f"

MODEL_PATH = "/app/models/best_model_pipeline.joblib"
OUTPUT_DIR = "/app/outputs"

METRICS_OUT = f"{OUTPUT_DIR}/reference_metrics.json"
PARAMS_OUT  = f"{OUTPUT_DIR}/reference_params.json"


def make_serializable(params):
    serializable = {}
    for k, v in params.items():
        if isinstance(v, (int, float, str, bool)) or v is None:
            serializable[k] = v
        else:
            serializable[k] = str(v)
    return serializable


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = mlflow.tracking.MlflowClient()
    run = client.get_run(RUN_ID)

    # ===== Métricas =====
    metrics = run.data.metrics
    with open(METRICS_OUT, "w") as f:
        json.dump({"metrics": metrics}, f, indent=4)
    print(f"✔ reference_metrics.json creado")

    # ===== Parámetros =====
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"No se encontró el modelo en: {MODEL_PATH}")

    pipeline = joblib.load(MODEL_PATH)

    # detectar el modelo final
    if hasattr(pipeline, "named_steps"):
        if "m" in pipeline.named_steps:
            final_model = pipeline.named_steps["m"]
        else:
            final_model = list(pipeline.named_steps.values())[-1]
    else:
        final_model = pipeline

    params = final_model.get_params()
    clean_params = make_serializable(params)

    with open(PARAMS_OUT, "w") as f:
        json.dump(clean_params, f, indent=4)

    print(f"✔ reference_params.json creado correctamente")


if __name__ == "__main__":
    main()

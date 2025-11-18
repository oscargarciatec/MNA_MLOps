import mlflow
import json
import os
import joblib
from pathlib import Path

RUN_ID = "aa9c15cc1c444b57b18907671c37a323"
OUTPUT_DIR = "/app/outputs"
REFERENCE_METRICS = f"{OUTPUT_DIR}/reference_metrics.json"
REFERENCE_PARAMS  = f"{OUTPUT_DIR}/reference_params.json"
LOCAL_MODEL = "/app/models/best_model_pipeline.joblib"   # <-- TU MODELO LOCAL


def make_serializable(params):
    clean = {}
    for k, v in params.items():
        if isinstance(v, (int, float, str, bool)) or v is None:
            clean[k] = v
        else:
            clean[k] = str(v)
    return clean


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = mlflow.tracking.MlflowClient()

    # ==============================
    # 1. Guardar métricas del RUN
    # ==============================
    run = client.get_run(RUN_ID)
    with open(REFERENCE_METRICS, "w") as f:
        json.dump({"metrics": run.data.metrics}, f, indent=4)
    print("✔ reference_metrics.json creado")

    # ==============================
    # 2. Usar modelo local
    # ==============================
    if not os.path.exists(LOCAL_MODEL):
        raise FileNotFoundError(f"No existe modelo local: {LOCAL_MODEL}")

    print(f"📦 Cargando modelo local como referencia: {LOCAL_MODEL}")
    pipeline = joblib.load(LOCAL_MODEL)

    if hasattr(pipeline, "named_steps"):
        model = pipeline.named_steps.get("m") or list(pipeline.named_steps.values())[-1]
    else:
        model = pipeline

    params = make_serializable(model.get_params())

    with open(REFERENCE_PARAMS, "w") as f:
        json.dump({"params": params}, f, indent=4)

    print("✔ reference_params.json creado (usando modelo local)")


if __name__ == "__main__":
    main()

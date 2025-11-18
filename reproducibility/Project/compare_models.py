#!/usr/bin/env python3
import json
from pathlib import Path
import sys

# Rutas dentro del contenedor
REFERENCE_METRICS = "/app/outputs/reference_metrics.json"
REFERENCE_PARAMS  = "/app/outputs/reference_params.json"

ACTUAL_METRICS = "/app/outputs/actual_metrics.json"
ACTUAL_PARAMS  = "/app/outputs/actual_params.json"

REF_MODEL = "/app/models/best_model_pipeline.joblib"
ACT_MODEL = "/app/models/test_model_pipeline.joblib"

METRIC_ATOL = 1e-6


def load_json(path: str, label: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"❌ No se encontró {label}: {path}")
        sys.exit(1)
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Error leyendo JSON en {label} ({path}): {e}")
        sys.exit(1)


def norm_metrics(data: dict) -> dict:
    """
    Soporta:
      - {"metrics": {...}}  (forma recomendada)
      - {...}              (plano)
    """
    if "metrics" in data and isinstance(data["metrics"], dict):
        return data["metrics"]
    return data


def norm_params(data: dict) -> dict:
    """
    Soporta:
      - {"params": {...}}  (lo que estás generando en referencia)
      - {...}              (plano, lo que generas en actual)
    """
    if "params" in data and isinstance(data["params"], dict):
        return data["params"]
    return data


def compare_metrics(ref_data: dict, act_data: dict) -> list:
    errors = []
    ref = norm_metrics(ref_data)
    act = norm_metrics(act_data)

    all_keys = set(ref.keys()) | set(act.keys())
    for k in all_keys:
        if k not in ref:
            errors.append(f"Métrica extra en modelo actual: '{k}' (no está en referencia)")
            continue
        if k not in act:
            errors.append(f"Métrica faltante en modelo actual: '{k}'")
            continue

        try:
            r = float(ref[k])
            a = float(act[k])
            if abs(r - a) > METRIC_ATOL:
                errors.append(f"Diferencia en métrica '{k}': ref={r} vs actual={a}")
        except (TypeError, ValueError):
            # No numérica → comparar como string
            if str(ref[k]) != str(act[k]):
                errors.append(f"Diferencia en métrica no numérica '{k}': ref={ref[k]} vs actual={act[k]}")

    return errors


def compare_params(ref_data: dict, act_data: dict):
    """
    Devuelve (errors, param_diffs):
      - errors: lista de mensajes
      - param_diffs: lista de tuplas (key, ref_val, act_val) para impresión
    """
    errors = []
    diffs = []

    ref = norm_params(ref_data)
    act = norm_params(act_data)

    all_keys = set(ref.keys()) | set(act.keys())

    for k in all_keys:
        ref_val = ref.get(k, None)
        act_val = act.get(k, None)

        if k not in ref:
            errors.append(f"Extra parameter in actual model: {k}")
            diffs.append((k, None, act_val))
        elif k not in act:
            errors.append(f"Missing parameter: {k}")
            diffs.append((k, ref_val, None))
        else:
            # Comparación por string para ser robustos
            if str(ref_val) != str(act_val):
                errors.append(f"Parameter mismatch: {k}: {ref_val} vs {act_val}")
                diffs.append((k, ref_val, act_val))

    return errors, diffs, ref, act


def compare_model_size(ref_model: str, act_model: str) -> list:
    errors = []
    ref_p = Path(ref_model)
    act_p = Path(act_model)

    if not ref_p.exists():
        errors.append(f"Modelo de referencia no encontrado: {ref_p}")
        return errors
    if not act_p.exists():
        errors.append(f"Modelo actual no encontrado: {act_p}")
        return errors

    ref_size = ref_p.stat().st_size
    act_size = act_p.stat().st_size

    if ref_size != act_size:
        errors.append(
            f"Model binary size mismatch: ref={ref_size} bytes vs actual={act_size} bytes"
        )

    return errors


def print_param_summary(ref_params: dict, act_params: dict):
    print("\n📌 PARÁMETROS DEL MODELO DE REFERENCIA:")
    for k, v in sorted(ref_params.items()):
        print(f" - {k}: {v}")

    print("\n📌 PARÁMETROS DEL MODELO ACTUAL:")
    for k, v in sorted(act_params.items()):
        print(f" - {k}: {v}")


def print_param_differences(param_diffs):
    if not param_diffs:
        print("\n🔍 No hay diferencias en parámetros.")
        return

    print("\n🔍 DIFERENCIAS EN PARÁMETROS DETECTADAS:")
    for key, ref_val, act_val in param_diffs:
        print(f" - {key}: referencia={ref_val}, actual={act_val}")


def main():
    print("\n📊 Comparando modelos de REFERENCIA vs ACTUAL...\n")

    errors = []

    # ---------- Cargar JSON ----------
    ref_metrics_raw = load_json(REFERENCE_METRICS, "reference_metrics.json")
    act_metrics_raw = load_json(ACTUAL_METRICS, "actual_metrics.json")

    ref_params_raw  = load_json(REFERENCE_PARAMS,  "reference_params.json")
    act_params_raw  = load_json(ACTUAL_PARAMS,     "actual_params.json")

    # ---------- Comparar métricas ----------
    errors += compare_metrics(ref_metrics_raw, act_metrics_raw)

    # ---------- Comparar parámetros ----------
    param_errors, param_diffs, ref_params, act_params = compare_params(
        ref_params_raw, act_params_raw
    )
    errors += param_errors

    # ---------- Comparar tamaño de binarios ----------
    errors += compare_model_size(REF_MODEL, ACT_MODEL)

    # ---------- Imprimir parámetros y difs ----------
    print_param_summary(ref_params, act_params)
    print_param_differences(param_diffs)

    # ---------- Resultado final ----------
    if errors:
        print("\n❌ REPRODUCIBILITY FAILED\n")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("\n✅ REPRODUCIBILITY PASSED!")
    sys.exit(0)


if __name__ == "__main__":
    main()

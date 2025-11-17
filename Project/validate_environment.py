#!/usr/bin/env python3
"""
Script de validación de ambiente para el proyecto MLOps.
Verifica que todas las dependencias y configuraciones estén correctas.

Uso:
    python scripts/validate_environment.py
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Verifica que la versión de Python sea compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro}"
    return False, f"✗ Python {version.major}.{version.minor}.{version.micro} (requiere 3.8+)"


def check_required_packages() -> List[Tuple[bool, str]]:
    """Verifica que los paquetes requeridos estén instalados."""
    required = [
        'pandas',
        'numpy',
        'sklearn',
        'mlflow',
        'dvc',
        'joblib',
        'fastapi',
        'mlflow',
        'joblib',
        'uvicorn',
        'pydantic'
    ]

    results = []
    for package in required:
        try:
            __import__(package)
            results.append((True, f"✓ {package}"))
        except ImportError:
            results.append((False, f"✗ {package} (faltante)"))

    return results


def check_project_structure() -> List[Tuple[bool, str]]:
    """Verifica que la estructura del proyecto Cookiecutter esté presente."""
    base_dir = Path.cwd()
    required_dirs = [
        'data/raw',
        'data/processed',
        'Project',
        'notebooks',
        'models',
        'reports',
    ]

    results = []
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            results.append((True, f"✓ {dir_path}/"))
        else:
            results.append((False, f"✗ {dir_path}/ (faltante)"))

    return results


def check_dvc_config() -> Tuple[bool, str]:
    """Verifica que DVC esté inicializado."""
    dvc_dir = Path.cwd() / '.dvc'
    if dvc_dir.exists() and dvc_dir.is_dir():
        return True, "✓ DVC inicializado"
    return False, "✗ DVC no inicializado"


def check_mlflow_setup() -> Tuple[bool, str]:
    """Verifica que MLflow tenga experimentos registrados."""
    mlruns_dir = Path.cwd() / 'mlruns'
    if mlruns_dir.exists():
        # Contar directorios de experimentos (ignorando 0/ que es metadata)
        experiments = [d for d in mlruns_dir.iterdir()
                      if d.is_dir() and d.name != '0' and d.name != '.trash']
        if experiments:
            return True, f"✓ MLflow con {len(experiments)} experimento(s)"
        return False, "✗ MLflow sin experimentos registrados"
    return False, "✗ MLflow no inicializado"


def check_git_repo() -> Tuple[bool, str]:
    """Verifica que el proyecto esté bajo control de Git."""
    git_dir = Path.cwd() / '.git'
    if git_dir.exists():
        return True, "✓ Repositorio Git inicializado"
    return False, "✗ No es un repositorio Git"


def print_section(title: str):
    """Imprime un separador de sección."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main():
    """Función principal de validación."""
    print("\n🔍 VALIDACIÓN DE AMBIENTE MLOps")
    print("Proyecto: Predicción de Consumo de Energía - Equipo 43\n")

    all_passed = True

    # 1. Verificar Python
    print_section("1. Versión de Python")
    passed, msg = check_python_version()
    print(msg)
    all_passed &= passed

    # 2. Verificar paquetes
    print_section("2. Paquetes Requeridos")
    package_results = check_required_packages()
    for passed, msg in package_results:
        print(msg)
        all_passed &= passed

    # 3. Verificar estructura
    print_section("3. Estructura del Proyecto (Cookiecutter)")
    structure_results = check_project_structure()
    for passed, msg in structure_results:
        print(msg)
        all_passed &= passed

    # 4. Verificar DVC
    print_section("4. Configuración DVC")
    passed, msg = check_dvc_config()
    print(msg)
    all_passed &= passed

    # 5. Verificar MLflow
    print_section("5. Configuración MLflow")
    passed, msg = check_mlflow_setup()
    print(msg)
    all_passed &= passed

    # 6. Verificar Git
    print_section("6. Control de Versiones")
    passed, msg = check_git_repo()
    print(msg)
    all_passed &= passed

    # Resumen final
    print_section("RESUMEN")
    if all_passed:
        print("Ambiente correctamente configurado")
        print("El proyecto está listo para desarrollo MLOps\n")
        return 0
    else:
        print("Hay problemas de configuración")
        print("Revisa los errores marcados con ✗ arriba\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash

# Script de configuración de ambiente virtual para MLOps Project
# Equipo 43 - Tecnológico de Monterrey

echo "=================================================="
echo "  MLOps Project - Configuración de Ambiente"
echo "  Equipo 43"
echo "=================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "Error: No se encontró requirements.txt"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar versión de Python
echo "🔍 Verificando versión de Python..."
python3 --version
echo ""

# Crear ambiente virtual
echo "Creando ambiente virtual..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error al crear el ambiente virtual"
    exit 1
fi

echo "Ambiente virtual creado exitosamente"
echo ""

# Activar ambiente virtual
echo "Activando ambiente virtual..."
source venv/bin/activate

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo ""
echo "Instalando dependencias del proyecto..."
echo "   Esto puede tomar varios minutos..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error al instalar dependencias"
    exit 1
fi

echo ""
echo "=================================================="
echo "  Configuración completada exitosamente!"
echo "=================================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Activar el ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Iniciar Jupyter Notebook:"
echo "   jupyter notebook"
echo ""
echo "3. Navegar a: notebooks/Fase 1_Equipo43.ipynb"
echo ""
echo "4. Para desactivar el ambiente cuando termines:"
echo "   deactivate"
echo ""
echo "=================================================="

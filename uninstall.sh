#!/usr/bin/env bash
set -euo pipefail

PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
CONFIG_DIR="$HOME/.config/doctomd"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "DocToMD - Desinstalador"
echo "========================"
echo "Esto eliminará:"
echo "  - Todas las dependencias instaladas (PyQt6, markitdown, docling, torch…)"
echo "  - El perfil de hardware ($CONFIG_DIR)"
echo "  - Archivos temporales del detector"
echo ""
read -rp "¿Continuar? (s/n): " CONFIRM
if [[ "${CONFIRM,,}" != "s" ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "Desinstalando paquetes..."
"$PYTHON" -m pip uninstall -y \
    PyQt6 PyQt6-Qt6 PyQt6-sip \
    PyQt6-WebEngine PyQt6-WebEngine-Qt6 PyQt6-WebEngine-Qt6-sip \
    markitdown markdown-it-py mdurl linkify-it-py \
    docling docling-core docling-ibm-models docling-parse \
    torch torchvision torchaudio \
    2>/dev/null || true

echo ""
echo "Eliminando perfil de hardware..."
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    echo "  Eliminado: $CONFIG_DIR"
else
    echo "  No encontrado, omitiendo."
fi

echo ""
echo "Eliminando archivos temporales del detector..."
[ -d "$SCRIPT_DIR/detector/build" ] && rm -rf "$SCRIPT_DIR/detector/build" && echo "  Eliminado: detector/build/"
[ -d "$SCRIPT_DIR/requirements"   ] && rm -rf "$SCRIPT_DIR/requirements"   && echo "  Eliminado: requirements/"

echo ""
echo "Desinstalación completada."
echo "Puedes borrar la carpeta del proyecto manualmente si lo deseas."

#!/usr/bin/env bash
set -euo pipefail

PYTHON=$(command -v python3 || command -v python)

if ! "$PYTHON" -c "import PyQt6" 2>/dev/null; then
    echo "Instalando dependencias base..."
    "$PYTHON" -m pip install -r requirements/base.txt
fi

"$PYTHON" -m doctomd

@echo off
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias base...
    pip install -r requirements\base.txt
    if errorlevel 1 (
        echo Error al instalar dependencias. Presiona cualquier tecla para salir.
        pause >nul
        exit /b 1
    )
)
python -m doctomd

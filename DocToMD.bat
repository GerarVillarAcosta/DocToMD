@echo off
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias base...
    pip install -r requirements\base.txt
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudieron instalar las dependencias.
        pause
        exit /b 1
    )
)
python -m doctomd
if errorlevel 1 (
    echo.
    echo ERROR: La aplicacion cerro con un error.
    pause
)

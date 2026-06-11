@echo off
echo DocToMD - Desinstalador
echo ========================
echo Esto eliminara:
echo   - Todas las dependencias instaladas (PyQt6, markitdown, docling, torch...)
echo   - El perfil de hardware (%USERPROFILE%\.config\doctomd\)
echo   - Archivos temporales del detector
echo.
set /p CONFIRM=¿Continuar? (s/n):
if /i not "%CONFIRM%"=="s" (
    echo Cancelado.
    exit /b 0
)

echo.
echo Desinstalando paquetes...
pip uninstall -y ^
    PyQt6 PyQt6-Qt6 PyQt6-sip ^
    PyQt6-WebEngine PyQt6-WebEngine-Qt6 PyQt6-WebEngine-Qt6-sip ^
    markitdown markdown-it-py mdurl linkify-it-py ^
    docling docling-core docling-ibm-models docling-parse ^
    torch torchvision torchaudio ^
    2>nul

echo.
echo Eliminando perfil de hardware...
if exist "%USERPROFILE%\.config\doctomd\" (
    rmdir /s /q "%USERPROFILE%\.config\doctomd\"
    echo   Eliminado: %USERPROFILE%\.config\doctomd\
) else (
    echo   No encontrado, omitiendo.
)

echo.
echo Eliminando archivos temporales del detector...
if exist "detector\build\" (
    rmdir /s /q "detector\build\"
    echo   Eliminado: detector\build\
)
if exist "requirements\" (
    rmdir /s /q "requirements\"
    echo   Eliminado: requirements\
)

echo.
echo Desinstalacion completada.
echo Puedes borrar la carpeta del proyecto manualmente si lo deseas.
pause >nul

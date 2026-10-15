@echo off
rem Abre la interfaz grafica de la rotacion de residentes.
cd /d "%~dp0"
python main_grafico.py
if errorlevel 1 (
    py main_grafico.py
    if errorlevel 1 (
        echo.
        echo No se pudo abrir la interfaz. Verifica que Python 3.10 o superior este instalado.
        pause
    )
)

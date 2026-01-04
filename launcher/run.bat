@echo off
echo === Toolkit Recon iniciado ===

if "%1"=="" (
    echo Uso: run.bat example.com
    pause
    exit /b
)

set TARGET=%1
set ROOT=%~dp0..

echo Target: %TARGET%
echo Root: %ROOT%

python -c "import sys; sys.path.insert(0, r'%ROOT%'); from recon.domain_enum.domain_enum import run; print(run('%TARGET%'))"

echo === Fin ===
pause

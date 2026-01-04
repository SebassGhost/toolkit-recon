param (
    [string]$Target
)

Write-Host ">>> Toolkit Recon iniciado"

if (-not $Target) {
    Write-Host "Uso: .\run.ps1 example.com"
    Read-Host "Presiona ENTER para salir"
    exit
}

$projectRoot = Split-Path -Parent $PSScriptRoot

$code = @"
import sys
sys.path.insert(0, r"$projectRoot")

from recon.domain_enum.domain_enum import run

result = run("$Target")
print(result)
"@

python -c $code

Write-Host ">>> Ejecución finalizada"
Read-Host "Presiona ENTER para salir"

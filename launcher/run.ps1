param (
    [string]$Target
)

Write-Host ">>> run.ps1 iniciado"
Write-Host ">>> Target:" $Target

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Write-Host ">>> Project root:" $ProjectRoot

$pythonCode = @"
import sys
sys.path.insert(0, r"$ProjectRoot")

from recon.domain_enum.domain_enum import run
import json

result = run("$Target")
print(json.dumps(result, indent=2))
"@

python -c $pythonCode

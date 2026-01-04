Write-Host ">>> run.ps1 iniciado"

param (
    [string]$Target
)

if (-not $Target) {
    Write-Host "Usage: .\run.ps1 <target>"
    exit 1
}

$pythonCode = @"
from recon.domain_enum.domain_enum import run
import json

result = run("$Target")
print(json.dumps(result, indent=2))
"@

python -c $pythonCode


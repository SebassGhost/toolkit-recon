param (
    [string]$Target
)

if (-not $Target) {
    Write-Host "Uso: ./run.ps1 <target>"
    exit
}

Write-Host "[*] Ejecutando toolkit-recon contra $Target"

python - <<EOF
from recon.domain_enum.domain_enum import run

result = run("$Target")
print(result)
EOF

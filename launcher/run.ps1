param (
    [string]$Target
)

if (-not $Target) {
    Write-Host "Uso: .\run.ps1 example.com"
    exit 1
}

python - << EOF
from recon.domain_enum.domain_enum import run
result = run("$Target")
print(result)
EOF

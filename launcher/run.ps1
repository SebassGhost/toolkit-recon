Write-Host "=== Toolkit Recon iniciado ==="

if ($args.Count -eq 0) {
    Write-Host "Uso: .\run.ps1 example.com"
    exit
}

$Target = $args[0]
$Root = Resolve-Path "$PSScriptRoot\.."

Write-Host "Target: $Target"
Write-Host "Root: $Root"

python -c "
import sys
sys.path.insert(0, r'$Root')
from recon.domain_enum.domain_enum import run
print(run('$Target'))
"

Write-Host "=== Fin ==="

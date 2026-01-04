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
from recon.recon_all import run_all
print(run_all('$Target'))

"

Write-Host "=== Fin ==="

#!/bin/bash

if [ -z "$1" ]; then
  echo "Uso: ./run.sh example.com"
  exit 1
fi

python3 - << EOF
from recon.domain_enum.domain_enum import run
result = run("$1")
print(result)
EOF


# Toolkit-Recon
##Toolkit-Recon — Framework modular de reconnaissance y OSINT para pentesting educativo

Toolkit-Recon está diseñado para automatizar la fase de reconocimiento de pruebas de penetración en entornos autorizados. Su filosofía es modularidad, ética y análisis reproducible, permitiendo correlación de datos entre módulos y almacenamiento histórico para análisis en profundidad. (aun se encuentra en etapa de desarrollo)

## Aviso legal

Este toolkit fue creado únicamente con fines educativos y de aprendizaje.

Úsalo solo en activos propios o con autorización explícita.

El autor no se hace responsable del uso indebido.



## Características principales

·Arquitectura modular y escalable

·Orquestador central (recon_all.py)

·Ejecución multiplataforma

·Resultados persistentes en JSON

·Diseño orientado a portafolio profesional




## Instalación

git clone https://github.com/SebassGhost/toolkit-recon

cd toolkit-recon

pip install -r requirements.txt

## Uso
PowerShell:
.\launcher\run.ps1 example.com

CMD:
launcher\run.bat example.com

Bash:
chmod +x launcher/run.sh
./launcher/run.sh example.com

## Output

Los resultados se almacenan automáticamente en:
output/<target>/recon.json

## Módulos implementados
 ### Domain Enumeration

·Resolución DNS

·Obtención de IPs

###  Subdomain Enumeration

·Fuerza bruta con wordlist

·Resolución DNS

 ### Endpoint Discovery

·Descubrimiento de rutas comunes

·Validación HTTP

 ### Tech Fingerprint (en progreso)

·Identificación de tecnologías

·Headers HTTP

### nota final

Este proyecto está pensado como base real de crecimiento hacia un toolkit de nivel profesional. Cada módulo añadido representa una habilidad práctica en pentesting




## License

This project is licensed under the MIT License.
See the LICENSE file for details.

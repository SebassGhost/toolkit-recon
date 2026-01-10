# Toolkit-Recon
## Toolkit-Recon — Framework modular de reconnaissance y OSINT para pentesting educativo

**Framework modular de reconocimiento (Reconnaissance) orientado a pentesting**, escrito en Python, con lanzadores multiplataforma (PowerShell, CMD y Bash).
Este proyecto está diseñado como toolkit personal y educativo, siguiendo prácticas reales usadas en frameworks profesionales de seguridad ofensiva.

## Aviso legal

Este toolkit fue creado únicamente con fines educativos y de aprendizaje.  
Úsalo solo en activos propios o con autorización explícita.  
El autor no se hace responsable del uso indebido.


## Filosofía del proyecto

Toolkit-Recon está diseñado con **modularidad, escalabilidad y profesionalismo** en mente:

- **Arquitectura modular:** Cada módulo funciona de forma independiente, permitiendo agregar nuevas funcionalidades sin afectar el núcleo
- **Orquestador central (`recon_all.py`):** Coordina la ejecución de todos los módulos y almacena los resultados
- **Persistencia de resultados:** JSON estructurado en `output//recon.json` para análisis histórico y correlación de datos 
- **Multiplataforma:** Compatible con PowerShell, CMD y Bash.  
- **En proceso:** Módulos OSINT planeados para análisis de infraestructura pública (ASN, CIDR, proveedores cloud) y subdominios pasivos mediante fuentes OSINT


## Características principales

- Arquitectura modular y escalable  
- Orquestador central (`recon_all.py`)  
- Ejecución multiplataforma  
- Resultados persistentes en JSON  
- Base para crecimiento hacia un toolkit de nivel profesional  


## Instalación

git clone https://github.com/SebassGhost/toolkit-recon

cd toolkit-recon

pip install -r requirements.txt

##  Uso

Toolkit-Recon se ejecuta como un **módulo Python**, siguiendo una estructura de paquete profesional.

Desde la raíz del proyecto, ejecuta:

python -m toolkit_recon.main


## Output

Los resultados se almacenan automáticamente en:
output/<target>/recon.json

Módulos implementados

### Domain Enumeration
- Resolución DNS  
- Obtención de IPs

### Subdomain Enumeration
- Fuerza bruta con wordlist  
- Resolución DNS

### Endpoint Discovery
- Descubrimiento de rutas comunes  
- Validación HTTP

### Tech Fingerprint (en progreso)
- Identificación de tecnologías  
- Headers HTTP

### OSINT (en proceso)
- Infraestructura pública (ASN, rangos IP, proveedores cloud)  
- Subdominios pasivos mediante fuentes públicas

Contribución y ética

Solo contribuye si los módulos respetan el principio de uso autorizado y educativo

Cada módulo debe devolver resultados normalizados y no incluir exploits ni técnicas invasivas

Documenta siempre el módulo antes de integrarlo al core


### nota final

Este proyecto está pensado como base real de crecimiento hacia un toolkit de nivel profesional. Cada módulo añadido representa una habilidad práctica en pentesting




## License

This project is licensed under the MIT License.
See the LICENSE file for details.

## Output

Los resultados se almacenan automáticamente en:
output/<target>/recon.json

Módulos implementados

### Domain Enumeration
- Resolución DNS  
- Obtención de IPs

### Subdomain Enumeration
- Fuerza bruta con wordlist  
- Resolución DNS

### Endpoint Discovery
- Descubrimiento de rutas comunes  
- Validación HTTP

### Tech Fingerprint (en progreso)
- Identificación de tecnologías  
- Headers HTTP

### OSINT (en proceso)
- Infraestructura pública (ASN, rangos IP, proveedores cloud)  
- Subdominios pasivos mediante fuentes públicas

Contribución y ética

Solo contribuye si los módulos respetan el principio de uso autorizado y educativo

Cada módulo debe devolver resultados normalizados y no incluir exploits ni técnicas invasivas

Documenta siempre el módulo antes de integrarlo al core


### nota final

Este proyecto está pensado como base real de crecimiento hacia un toolkit de nivel profesional. Cada módulo añadido representa una habilidad práctica en pentesting




## License

This project is licensed under the MIT License.
See the LICENSE file for details.

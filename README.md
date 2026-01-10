# Toolkit-Recon
## Toolkit-Recon — Framework modular de reconnaissance y OSINT para pentesting educativo

Toolkit-Recon está diseñado para automatizar la fase de reconocimiento de pruebas de penetración en entornos autorizados. Su filosofía es modularidad, ética y análisis reproducible, permitiendo correlación de datos entre módulos y almacenamiento histórico para análisis en profundidad. (aun se encuentra en etapa de desarrollo)

## Aviso legal

Este toolkit fue creado únicamente con fines educativos y de aprendizaje.

Úsalo solo en activos propios o con autorización explícita.

El autor no se hace responsable del uso indebido.

## Filosofía del proyecto

Toolkit-Recon está diseñado para automatizar la **fase de reconocimiento en pruebas de penetración**, respetando siempre la ética y el uso autorizado. Su filosofía se basa en tres pilares:

1. **Modularidad** – Cada componente del toolkit funciona de forma independiente y escalable, permitiendo agregar nuevos módulos sin afectar los existentes
2. **Reproducibilidad** – Todos los resultados se almacenan de forma estructurada (JSON / SQLite) para análisis histórico y correlación de datos entre módulos
3. **Ética y seguridad** – El toolkit solo procesa información pública o de entornos autorizados; no incluye exploits ni técnicas invasivas

Este proyecto permite a investigadores y pentesters educativos realizar un **reconocimiento organizado y profesional**, facilitando la comprensión de la superficie de ataque de objetivos propios o autorizados


## Funcionalidades principales

- **Enumeración de dominios y subdominios**  
- **Resolución de IPs y detección de ASN / proveedores cloud**  
- **Descubrimiento de endpoints HTTP comunes**  
- **Fingerprinting de tecnologías (headers y servicios visibles)**  
- **Almacenamiento de resultados en JSON y SQLite**  
- **Arquitectura modular**, fácil de ampliar con nuevos módulos OSINT o integraciones externas  



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

Contribución y ética

Solo contribuye si los módulos respetan el principio de uso autorizado y educativo

Cada módulo debe devolver resultados normalizados y no incluir exploits ni técnicas invasivas

Documenta siempre el módulo antes de integrarlo al core


### nota final

Este proyecto está pensado como base real de crecimiento hacia un toolkit de nivel profesional. Cada módulo añadido representa una habilidad práctica en pentesting




## License

This project is licensed under the MIT License.
See the LICENSE file for details.


# Tech Fingerprint

Modulo para identificar tecnologias visibles del objetivo.

## Deteccion

- Encabezados HTTP (`server`, `x-powered-by`, `via`).
- Cookies comunes para inferencia de framework/lenguaje.
- Sonda opcional de GraphQL segun perfil.

## Salida

Retorna tecnologias detectadas, encabezados y metricas de ejecucion.

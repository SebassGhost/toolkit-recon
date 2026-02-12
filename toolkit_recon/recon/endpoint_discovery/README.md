
# Endpoint Discovery

Modulo de descubrimiento de rutas HTTP sobre un objetivo.

## Implementacion

- Escaneo asincrono con `asyncio + httpx`.
- Control de tasa de peticiones (`max_rps`).
- Reintentos con backoff para errores transitorios.

## Salida

Retorna `results` y `metrics` con conteos de rutas, errores, reintentos y rendimiento.

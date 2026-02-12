
# Metodologia

## Objetivos

- Mantener el reconocimiento modular.
- Preservar un formato de salida consistente entre modulos.
- Usar perfiles para balancear velocidad y sigilo.

## Flujo De Ejecucion

1. Enumeracion de subdominios con filtrado de wildcard.
2. Descubrimiento de endpoints por objetivo/subdominio con sondeo HTTP asincrono.
3. Fingerprinting de tecnologias por objetivo/subdominio.
4. Consolidacion en `recon.json` con metricas por modulo.

## Decisiones De Diseno

- `schema_version` se incluye en todas las salidas de modulos.
- Se capturan metricas por modulo para analisis y ajuste.
- Endpoints incluye reintentos y backoff para redes inestables.
- Los artefactos de salida se guardan localmente y no se suben a Git.

## Controles De Calidad

- Las pruebas unitarias validan configuracion y estructura de salida.
- CI ejecuta tests en cada push y pull request.

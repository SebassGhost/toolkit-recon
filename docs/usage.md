
# Guia De Uso

## Comandos

Desde la raiz del proyecto:

```bash
python -m toolkit_recon.main subdomain example.com --profile passive
python -m toolkit_recon.main endpoints example.com --profile balanced
python -m toolkit_recon.main tech example.com --profile balanced
python -m toolkit_recon.main osint-user nombre_usuario --profile balanced
python -m toolkit_recon.main recon-all example.com --profile aggressive
python -m toolkit_recon.main recon-all example.com --profile balanced --osint-user nombre_usuario
```

## Perfiles

- `passive`: evita sondeo agresivo y usa una tasa de peticiones baja.
- `balanced`: opcion recomendada con concurrencia moderada.
- `aggressive`: escaneos mas amplios, mayor concurrencia y mayor tasa de peticiones.

## Archivos De Salida

Se generan en `output/<target>/`:

- `subdomains.json`
- `endpoints.json`
- `tech_fingerprint.json`
- `recon.json`
- `osint_username.json` (opcional)

Cada archivo incluye `schema_version` para mantener compatibilidad.

## Metricas De Endpoints

`endpoint_discovery` devuelve:

- `total_paths`
- `attempted`
- `completed`
- `errors`
- `retried_requests`
- `duration_seconds`
- `throughput_rps`

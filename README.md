# Toolkit-Recon

Toolkit modular de reconocimiento y OSINT para flujos de pentesting educativo.

## Aviso Legal

Usa este proyecto solo sobre activos propios o con autorizacion explicita.
Los autores no se hacen responsables del uso indebido.

## Caracteristicas

- Arquitectura modular (`domain`, `subdomain`, `endpoint`, `tech`, `osint_username`)
- Comandos CLI para ejecuciones puntuales y recon completo
- Perfiles de ejecucion: `passive`, `balanced`, `aggressive`
- Esquema de salida versionado (`schema_version`)
- Salida JSON por modulo y consolidado en `recon.json`
- Lanzadores multiplataforma (`.ps1`, `.bat`, `.sh`)

## Instalacion

```bash
git clone https://github.com/SebassGhost/toolkit-recon
cd toolkit-recon
pip install -r requirements.txt
```

## Uso

Ejecuta como modulo de Python desde la raiz del proyecto:

```bash
python -m toolkit_recon.main subdomain example.com
python -m toolkit_recon.main endpoints example.com
python -m toolkit_recon.main tech example.com
python -m toolkit_recon.main osint-user nombre_usuario
python -m toolkit_recon.main recon-all example.com --profile balanced
python -m toolkit_recon.main recon-all example.com --profile balanced --osint-user nombre_usuario
```

## Salida

Los resultados se guardan en:

```text
output/<target>/
```

Archivos principales:

- `output/<target>/subdomains.json`
- `output/<target>/endpoints.json`
- `output/<target>/tech_fingerprint.json`
- `output/<target>/recon.json`
- `output/<target>/osint_username.json` (si usas `osint-user`)

Los archivos incluyen `schema_version` para mantener compatibilidad hacia adelante.

Estructura base de `recon.json`:

```json
{
  "schema_version": "1.0.0",
  "target": "example.com",
  "profile": "balanced",
  "timestamp": "2026-02-12T00:00:00Z",
  "modules": {
    "subdomain_enum": {},
    "endpoint_discovery": {},
    "tech_fingerprint": {}
  },
  "metrics": {
    "subdomain_enum": {},
    "endpoint_discovery": {},
    "tech_fingerprint": {}
  }
}
```

## Perfiles

- `passive`: sondeo minimo, menor tasa de peticiones y metodos conservadores
- `balanced`: perfil recomendado para uso diario
- `aggressive`: mayor volumen de rutas, mas concurrencia y mayor tasa de peticiones

## Metricas

Cada modulo expone metricas:

- `subdomain_enum`: intentos DNS, filtrado por wildcard, duracion
- `endpoint_discovery`: rutas intentadas/completadas, reintentos, errores, rendimiento
- `tech_fingerprint`: intentos/exitos HTTP, intentos GraphQL, duracion
- `osint_username`: perfiles encontrados, errores y duracion de ejecucion

## Desarrollo

Instala dependencias de pruebas y ejecuta tests:

```bash
pip install -r tests/requirements.txt
python -m pytest -q
```

## Contribucion

Revisa `CONTRIBUTING.md` para flujo de trabajo, estandares de modulos y definicion de "done".

## Higiene Del Repositorio

Los resultados de escaneo en `output/` estan ignorados por Git (`.gitignore`) y no deben subirse.

## Licencia

MIT. Revisa `LICENSE`.

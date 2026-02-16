# Toolkit-Recon

Framework modular de reconocimiento y OSINT para practicas de pentesting educativo.

Diseñado para ejecutar flujos reales de recon con:
- CLI rapido y menu interactivo
- perfiles de agresividad
- salida JSON normalizada
- metricas por modulo

## Aviso legal

Usa este proyecto solo en activos propios o con autorizacion explicita.
El autor no se hace responsable del uso indebido.

## Inicio rapido (60 segundos)

```bash
git clone https://github.com/SebassGhost/toolkit-recon
cd toolkit-recon
pip install -r requirements.txt
python -m toolkit_recon.main
```

`python -m toolkit_recon.main` abre el menu interactivo con opciones numeradas.

## Modos de uso

### 1) Modo interactivo (recomendado para empezar)

```bash
python -m toolkit_recon.main
# o
python -m toolkit_recon.main menu
```

Menu principal:
- `1` Recon completo
- `2` Subdominios
- `3` Endpoints
- `4` Tech fingerprint
- `5` OSINT username
- `0` Salir

### 2) Modo CLI (automatizacion/scripts)

Comandos mas usados:

```bash
python -m toolkit_recon.main example.com
python -m toolkit_recon.main recon-all example.com --profile balanced
python -m toolkit_recon.main r -t example.com --profile passive
python -m toolkit_recon.main subdomain example.com
python -m toolkit_recon.main endpoints example.com
python -m toolkit_recon.main tech example.com
python -m toolkit_recon.main osint-user octocat
python -m toolkit_recon.main recon-all example.com --osint-user octocat
```

## Referencia de comandos

| Comando | Alias | Descripcion |
|---|---|---|
| `recon-all <dominio>` | `recon`, `r` | Ejecuta flujo completo |
| `subdomain <dominio>` | `sub`, `s` | Enumera subdominios |
| `endpoints <dominio/subdominio>` | `ep`, `e` | Descubre rutas HTTP |
| `tech <dominio/subdominio>` | `t` | Fingerprint de tecnologias |
| `osint-user <username>` | `osint`, `o` | Busca perfiles publicos por username |
| `menu` | `m` | Abre menu interactivo |

Opciones utiles:
- `--profile {passive,balanced,aggressive}`
- `-t, --target <objetivo>`
- `--osint-user <username>` (solo en `recon-all`)

## Perfiles

| Perfil | Objetivo | Comportamiento |
|---|---|---|
| `passive` | Minimizar ruido | Menos concurrencia y sondeo conservador |
| `balanced` | Uso diario | Balance entre cobertura y sigilo |
| `aggressive` | Maxima cobertura | Mas rutas, concurrencia y tasa de peticiones |

## Arquitectura

```text
toolkit_recon/
  main.py
  config/
  recon/
    domain_enum/
    subdomain_enum/
    endpoint_discovery/
    tech_fingerprint/
    osint_username/
  utils/
  schema/
```

Puntos clave:
- Orquestador: `toolkit_recon/recon/recon_all.py`
- Contrato de salida: `toolkit_recon/schema/recon.schema.json`
- Persistencia: `toolkit_recon/utils/output.py`

## Salida y esquema

Todos los modulos devuelven JSON con `schema_version`.

Archivos generados en:

```text
output/<target>/
```

Principales:
- `subdomains.json`
- `endpoints.json`
- `tech_fingerprint.json`
- `recon.json`
- `osint_username.json` (si aplica)

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

## Calidad y CI

Validaciones recomendadas antes de commit:

```bash
python -m ruff check .
python -m pytest -q
```

CI ejecuta:
- lint (`ruff`)
- tests (`pytest`)

## Sherlock (OSINT username)

`osint-user` funciona como integracion opcional.

Si Sherlock no esta instalado:
- no rompe el flujo
- devuelve error controlado en JSON (`command_available: false`)

## Troubleshooting rapido

### `--profile` no se aplica como esperas
Usa siempre:
```bash
python -m toolkit_recon.main recon-all example.com --profile balanced
```
o
```bash
python -m toolkit_recon.main --profile balanced recon-all example.com
```

### Error "Debes indicar target..."
Falta objetivo. Usa positional o `-t`:
```bash
python -m toolkit_recon.main subdomain example.com
python -m toolkit_recon.main subdomain -t example.com
```

### Los JSON de `output/` aparecen en Git
Si estaban trackeados antes, quitalos del indice y commitea:
```bash
git rm -r --cached output
git commit -m "chore: stop tracking output files"
git push
```

## Contribucion

Revisa `CONTRIBUTING.md` para:
- estandar de modulos
- definicion de done
- convenciones de commits

## Licencia

MIT. Ver `LICENSE`.

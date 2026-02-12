# Osint Username

Modulo para buscar presencia de un nombre de usuario en plataformas publicas usando Sherlock.

## Uso

Se ejecuta desde CLI con:

```bash
python -m toolkit_recon.main osint-user <username>
```

## Notas

- Es opcional: si Sherlock no esta instalado, devuelve error controlado.
- Retorna salida normalizada con `schema_version`, `results` y `metrics`.

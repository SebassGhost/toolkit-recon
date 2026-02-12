# Guia De Contribucion

Gracias por contribuir a Toolkit-Recon.

## Requisitos Minimos

1. El modulo debe respetar el uso autorizado y educativo.
2. La salida debe incluir `schema_version`.
3. Toda funcionalidad nueva debe incluir pruebas.
4. El codigo debe pasar lint y tests.

## Flujo Recomendado

1. Crea una rama: `feat/<descripcion-corta>` o `fix/<descripcion-corta>`.
2. Implementa cambios pequenos y comprobables.
3. Ejecuta:

```bash
python -m ruff check .
python -m pytest -q
```

4. Abre Pull Request con contexto tecnico claro.

## Estandar Para Modulos

Cada modulo nuevo debe:

1. Exponer funcion `run(target: str, profile: str = "balanced") -> dict`.
2. Incluir campos base:
- `schema_version`
- `module`
- `target`
- `profile`
- `metrics`
3. Ser tolerante a errores de red y devolver estructura consistente.

## Definicion De Done

Una tarea se considera terminada cuando:

1. Cumple requerimientos funcionales.
2. Incluye pruebas automáticas relevantes.
3. Pasa `ruff` y `pytest`.
4. Actualiza documentacion (`README` o `docs/`) cuando cambie contrato o uso.

## Commits

Formato sugerido:

- `feat: ...`
- `fix: ...`
- `refactor: ...`
- `docs: ...`
- `test: ...`
- `ci: ...`

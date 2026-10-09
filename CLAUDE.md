# Gestor de inventario "La Esquina" — reto de refactorización

Aplicación de consola en Python para inventario y ventas de una tienda pequeña.
El objetivo del reto es **mejorar la calidad del código sin cambiar su
comportamiento**: los 20 tests de `tests/` son de caja negra y deben pasar
siempre.

## Estructura

- `src/gestor.py` — estado global (`INVENTARIO`, `VENTAS`, `contadorVentas`,
  `ultimo_error`), alta/baja de productos, stock, ventas, ticket y cotización.
- `src/almacen.py` — guardado y carga del estado en JSON.
- `src/reportes.py` — stock bajo, inventario, total vendido, más vendidos, resumen.
- `src/main.py` — menú interactivo de consola (sin tests).
- `tests/` — suite pytest; `conftest.py` agrega `src/` al `sys.path` y reinicia
  el sistema antes y después de cada prueba.

## Comandos

```bash
.venv/bin/pytest -q            # deben pasar los 20 tests
.venv/bin/ruff check src       # meta final: 0 errores
.venv/bin/ruff check src --fix # solo para los errores triviales marcados [*]
python src/main.py             # app interactiva, ejecutar desde la raíz
```

## Restricciones inviolables

- **No modificar `tests/` ni `pyproject.toml`.** No desactivar reglas de ruff
  con `# noqa` para "hacer pasar" el linter.
- **Conservar la API pública** que usan los tests y los otros módulos:
  `agregarProducto`, `buscarProducto` (conservan su nombre camelCase),
  `reiniciar_sistema`, `eliminar_producto`, `actualizar_stock`,
  `registrar_venta`, `cotizar`, `INVENTARIO`, `VENTAS`, `ultimo_error`,
  `guardar_datos`, `cargar_datos`, `productos_stock_bajo`,
  `reporte_inventario`, `total_vendido`, `mas_vendidos`, `resumen_ventas`.
- **Conservar valores de retorno y efectos**: `True`/`False`/`None` según el
  caso, el motivo en `ultimo_error` con el mismo texto, los mismos `print`.
- **No cambiar formatos de salida**: ticket y reportes usan `str(float)`
  (`600.0`, no `600.00`); no sustituir por `:.2f`.
- **No simplificar algebraicamente las fórmulas**: mantener el mismo orden de
  operaciones de punto flotante (p. ej. no cambiar `x - x*0.07` por `x*0.93`).
- **Respetar las diferencias entre `cotizar` y `registrar_venta`**: `cotizar`
  no aplica el extra VIP, no valida stock y revisa existencia del producto
  antes que la cantidad; `registrar_venta` revisa primero el código vacío.
- **Regla VIP**: aplica si el cliente empieza con `"VIP"` y
  `subtotal - descuento > 200`; el extra es 2 % del **subtotal**.
- **`INVENTARIO` y `VENTAS` se modifican en sitio** (`clear`, `update`,
  `extend`), nunca se reasignan.
- Si se renombra `contadorVentas`, actualizar `almacen.py` en el mismo cambio.
- No hacer commit de cambios en `datos_ejemplo.json` (la opción 8 del menú lo
  sobrescribe).

## Metodología incremental

1. Una refactorización a la vez, pequeña y con un único propósito.
2. Antes de cambiar código, leerlo completo y localizar todos sus usos (`grep`).
3. Después de **cada** cambio ejecutar `pytest` y `ruff check src`. Si algo
   falla, corregir o revertir antes de continuar.
4. Si el cambio toca código sin cobertura de tests (`main.py`, formato del
   ticket, `resumen_ventas`, `hayArchivo`, mensajes de `ultimo_error`), comparar
   la salida antes/después con un script temporal fuera del repositorio.
5. Un commit atómico por refactorización, con prefijo `refactor:` y solo cuando
   el usuario lo pida.
6. Registrar cada refactorización en `BITACORA.md` (prompt, cambio,
   justificación, resultado de tests).

## Convenciones de código

- Compatible con Python 3.10+ (`target-version = "py310"`): type hints con
  `X | None`, `dict[str, dict]`, `list[dict]`; nada de sintaxis 3.12+.
- `snake_case` descriptivo para funciones y variables; evitar `temp2`, `aux`,
  `x`, `t`, `d`. Excepciones: `agregarProducto` y `buscarProducto`.
- Constantes de negocio en MAYÚSCULAS al inicio del módulo (IVA, umbrales de
  descuento, stock mínimo, prefijo VIP).
- Retornos tempranos en lugar de `if` anidados; complejidad ciclomática ≤ 10.
- Una función, una responsabilidad: separar validación, cálculo, formato e I/O.
- Archivos siempre con `with open(..., encoding="utf-8")`.
- Sin código muerto ni código comentado; sin imports sin usar.
- f-strings o `"".join(...)` en lugar de concatenar en bucles.
- Docstrings y comentarios en español, breves; líneas de máximo 88 caracteres.

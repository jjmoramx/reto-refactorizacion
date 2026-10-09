# Gestor de inventario "La Esquina" — reto de refactorización

Aplicación de consola en Python para inventario y ventas de una tienda pequeña.
El objetivo del reto es **mejorar la calidad del código sin cambiar su
comportamiento**: los 20 tests de `tests/` son de caja negra y deben pasar
siempre.

## Estructura

- `src/gestor.py` — estado global (`INVENTARIO`, `VENTAS`, `contadorVentas`,
  `ultimo_error`), constantes de negocio (`TASA_IVA`, umbrales y tasas de
  descuento, `PREFIJO_VIP`, `MONTO_MINIMO_VIP`, `TASA_DESCUENTO_VIP`),
  alta/baja de productos, stock, ventas, ticket y cotización.
  Auxiliares privadas: `_descuento_por_volumen`, `_calcular_iva`,
  `_es_cliente_vip`.
- `src/almacen.py` — guardado y carga del estado en JSON; `hay_archivo`.
- `src/reportes.py` — stock bajo, inventario, total vendido, más vendidos, resumen.
- `src/main.py` — menú interactivo de consola (sin tests). `menu()` despacha
  con `ACCIONES_MENU` a funciones privadas `_agregar_producto`,
  `_registrar_venta`, `_cotizar`, `_reporte_inventario`, `_resumen_ventas`,
  `_mas_vendidos`, `_alertas_stock_bajo`; `OPCION_SALIR` llama a
  `_guardar_y_salir`.
- `tests/` — suite pytest; `conftest.py` agrega `src/` al `sys.path` y reinicia
  el sistema antes y después de cada prueba.
- `docs/bitacora.md` — bitácora de refactorizaciones; `docs/reflexion.md` —
  reflexión técnica del proceso.

## Comandos

```bash
.venv/bin/python -m pytest -v  # deben pasar los 20 tests
.venv/bin/ruff check src       # debe dar "All checks passed!"
.venv/bin/ruff check src --fix # solo para los errores triviales marcados [*]
python src/main.py             # app interactiva, ejecutar desde la raíz
```

## API pública (no cambiar nombre, firma ni comportamiento)

- `gestor`: `INVENTARIO`, `VENTAS`, `contadorVentas`, `ultimo_error`,
  `reiniciar_sistema`, `agregarProducto`, `eliminar_producto`,
  `actualizar_stock`, `buscarProducto`, `registrar_venta`, `cotizar`.
- `almacen`: `guardar_datos`, `cargar_datos`, `hay_archivo` y su alias de
  compatibilidad `hayArchivo` (resuelto por `__getattr__` del módulo).
- `reportes`: `hacer_cosa`, `productos_stock_bajo`, `reporte_inventario`,
  `total_vendido`, `mas_vendidos`, `resumen_ventas`.
- `main`: `menu`, `pedir_numero`, `ARCHIVO`.

Nombres camelCase que se conservan a propósito:

| Nombre | Por qué | Cómo cumple Ruff |
|---|---|---|
| `agregarProducto`, `buscarProducto` | Los usan los tests | `ignore-names` en `pyproject.toml` |
| `contadorVentas` | `almacen.py` y código externo lo leen y escriben | `# noqa: N816` en su única línea de definición, con comentario |
| `hayArchivo` | Compatibilidad con llamadas existentes | Alias vía `__getattr__` del módulo; el nombre real es `hay_archivo` |

## Restricciones inviolables

- **No modificar `tests/` ni `pyproject.toml`.**
- **No silenciar reglas de Ruff** globalmente ni por archivo. Solo se admite un
  `# noqa: <REGLA>` en una línea concreta cuando lo exige la compatibilidad de
  la API pública, con comentario que lo justifique (caso actual: `contadorVentas`).
- **Conservar valores de retorno y efectos**: `True`/`False`/`None` según el
  caso, el motivo en `ultimo_error` con el mismo texto, los mismos `print`.
- **No cambiar formatos de salida**: ticket y reportes usan `str(float)`
  (`600.0`, no `600.00`); no sustituir por `:.2f`. Textos y orden del menú
  idénticos.
- **No simplificar algebraicamente las fórmulas**: mantener el mismo orden de
  operaciones de punto flotante (p. ej. no cambiar `x - x*0.07` por `x*0.93`).
- **Respetar las diferencias entre `cotizar` y `registrar_venta`**: `cotizar`
  no aplica el extra VIP, no valida stock y revisa existencia del producto
  antes que la cantidad; `registrar_venta` revisa primero el código vacío.
- **Regla VIP**: aplica si el cliente empieza con `"VIP"` (sensible a
  mayúsculas) y `subtotal - descuento > 200`; el extra es 2 % del **subtotal**.
- **`INVENTARIO` y `VENTAS` se modifican en sitio**, nunca se reasignan.
- **Conservar las excepciones**: `cargar_datos` atrapa `Exception` al leer el
  JSON; las claves faltantes (`KeyError`) y errores de E/S se propagan.
- No hacer commit de cambios en `datos_ejemplo.json` (la opción 8 del menú lo
  sobrescribe); para probar el menú, usar una copia en un directorio temporal.

## Metodología incremental

1. Una refactorización a la vez, pequeña y con un único propósito.
2. Antes de cambiar código, leerlo completo y localizar todos sus usos (`grep`).
3. Después de **cada** cambio ejecutar `pytest` y `ruff check src`. Si algo
   falla, corregir o revertir antes de continuar.
4. Si el cambio toca código sin cobertura de tests (`main.py`, formato del
   ticket, `resumen_ventas`, `hay_archivo`, mensajes de `ultimo_error`),
   comparar la versión anterior (`git archive HEAD src`) y la nueva con un
   script temporal fuera del repositorio.
5. Preferir la solución más simple que conserve la compatibilidad; evitar
   metaprogramación solo para satisfacer al linter.
6. Un commit atómico por refactorización, con prefijo `refactor:` y solo cuando
   el usuario lo pida. No hacer push ni abrir PR sin autorización.
7. Registrar cada refactorización en `docs/bitacora.md` (prompt exacto, cambio,
   justificación, resultado real de tests y Ruff).

## Convenciones de código

- Compatible con Python 3.10+ (`target-version = "py310"`): type hints con
  `X | None`, `dict[str, dict]`, `list[dict]`; nada de sintaxis 3.12+.
- `snake_case` descriptivo para funciones y variables; evitar `temp2`, `aux`,
  `x`, `t`, `d`. Excepciones: las de la tabla de nombres camelCase.
- Auxiliares internas con prefijo `_`.
- Constantes de negocio en MAYÚSCULAS al inicio del módulo.
- Retornos tempranos en lugar de `if` anidados; complejidad ciclomática ≤ 10.
- Una función, una responsabilidad: separar validación, cálculo, formato e I/O.
- Archivos siempre con `with open(..., encoding="utf-8")`.
- Sin código muerto ni código comentado; sin imports sin usar.
- f-strings o `"".join(...)` en lugar de concatenar en bucles.
- Docstrings y comentarios en español, breves; líneas de máximo 88 caracteres.

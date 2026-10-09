# Reflexión técnica: refactorización asistida por IA

> Este documento resume hechos verificables del proceso (comandos, cifras,
> decisiones registradas en `docs/bitacora.md` y en el historial de git).
> Las secciones marcadas con **[COMPLETAR POR EL ALUMNO]** requieren la
> experiencia y opinión personal de quien entrega el reto y no deben
> rellenarse con texto generado.

## 1. Punto de partida

- Aplicación de consola de inventario y ventas: `gestor.py` (lógica y estado
  global), `almacen.py` (JSON), `reportes.py` (reportes), `main.py` (menú).
- Línea base: **20/20 tests aprobados** y **20 errores de Ruff** (UP009 ×4,
  SIM102 ×3, SIM115 ×3, C901 ×2, N802 ×2, SIM108, N816, SIM103, UP015, I001,
  F401).
- Restricciones: no modificar `tests/` ni `pyproject.toml`, comportamiento
  observable idéntico.
- Entorno: Python 3.14.4, pytest 9.1.1 y Ruff 0.16.10; el código se mantiene
  compatible con Python 3.10 (`target-version = "py310"`).
- Ciclo por refactorización: leer el código y localizar usos con `grep` →
  aplicar un único cambio → `python -m pytest -v` y `ruff check src` →
  comparar versión anterior y nueva con un script temporal fuera del
  repositorio → revisar el diff → registrar en la bitácora → commit atómico.

## 2. Resultado

| Paso | Cambio principal | Tests | Ruff |
|------|------------------|-------|------|
| Base | — | 20/20 | 20 |
| R1 | Eliminar código muerto, import sin usar y declaraciones UTF-8 | 20/20 | 13 |
| R2 | Constantes de negocio y funciones de descuento por volumen e IVA compartidas | 20/20 | 11 |
| R3 | Condición VIP en una sola expresión (`_es_cliente_vip`) | 20/20 | 8 |
| R4 | `with open`, `hay_archivo` con alias `hayArchivo` | 20/20 | 3 |
| R5 | `menu()` de complejidad 17 a 4, imports ordenados, `contadorVentas` | 20/20 | 0 |

## 3. Beneficios observados

- **Diagnóstico rápido y priorizado**: el análisis inicial relacionó cada
  error de Ruff con un *code smell* y un archivo concreto, y propuso un orden
  de menor a mayor riesgo.
- **Detección de reglas implícitas** que los tests no cubren: `cotizar` no
  aplica VIP y valida en otro orden que `registrar_venta`; el extra VIP se
  calcula sobre el subtotal; los formatos usan `str(float)`; el orden de las
  operaciones de punto flotante afecta los centavos.
- **Validación más allá de los tests**: para cada cambio se compararon la
  versión anterior (`git archive`) y la nueva con scripts temporales fuera del
  repositorio:
  - R2: 2640 combinaciones de precio, cantidad y cliente.
  - R3: 2964 ventas con 26 valores de cliente (incluye `None`, `""`,
    minúsculas, tipos no cadena) y la frontera exacta de $200.
  - R4: 22 escenarios de E/S (archivo inexistente, JSON inválido, archivo
    vacío, bytes no UTF-8, claves faltantes, directorio, datos no
    serializables) y `ResourceWarning`, que mostró que la versión anterior
    dejaba un archivo abierto al fallar `json.dump`.
  - R5: 15 guiones del menú (opciones válidas e inválidas, EOF, `1e400`,
    `nan`) comparando stdout, código de salida, excepción y JSON guardado; y
    18 pasos de sincronización de `contadorVentas`.

## 4. Riesgos identificados

- **La suite es de caja negra y parcial**: `main.py`, el ticket,
  `resumen_ventas`, los mensajes de `ultimo_error` y varios casos límite no
  tienen tests. Que pasen 20/20 no basta para afirmar que el comportamiento es
  idéntico.
- **Cambios "obvios" que alteran el comportamiento**: sustituir
  `cliente[0:3] == "VIP"` por `startswith` cambia las excepciones ante tipos
  no cadena; acotar `except Exception` a `ValueError` cambia qué errores se
  atrapan; simplificar fórmulas cambia redondeos; usar `:.2f` cambia la salida.
- **Satisfacer al linter a cualquier costo**: la primera solución para N816
  (ver sección 5) eliminó el error pero agregó complejidad mayor que el
  problema original.
- **Efectos sobre datos versionados**: la opción 8 del menú sobrescribe
  `datos_ejemplo.json`; las pruebas manuales se hicieron con copias en
  directorios temporales.

## 5. Dificultades y decisiones técnicas

- **Alias `hayArchivo` (R4)**: un alias directo (`hayArchivo = hay_archivo`)
  cambia N802 por N816. Se resolvió con `__getattr__` de módulo (PEP 562),
  que conserva `almacen.hayArchivo` y `from almacen import hayArchivo`.
- **`contadorVentas` (R5 y auditoría)**: el contador se reasigna con `global`
  dentro de `gestor` y se escribe desde `almacen`, así que un alias de solo
  lectura quedaría desincronizado. La primera solución usó una `property` en
  la clase del módulo creada con `type(...)` para evitar N816/N815/N802.
  Funcionaba, pero en la auditoría final se evaluó como innecesariamente
  compleja (metaprogramación, cambio del tipo del módulo, ~25 líneas) y se
  sustituyó por conservar el nombre original con `# noqa: N816` localizado y
  documentado, criterio equivalente al `ignore-names` que `pyproject.toml` ya
  aplica a `agregarProducto` y `buscarProducto`. Se verificó que el
  comportamiento es idéntico a la versión previa a R5.
- **Alcance de cada paso**: cuando una corrección pertenecía a otra
  refactorización (p. ej. UP015 e I001 durante R1, o N816 durante R4 por
  restricción de no tocar `gestor.py`) se pospuso en lugar de mezclarla.

## 6. Pendientes y límites conocidos

- No se refactorizó `reportes.py` (`hacer_cosa`, constante de stock mínimo,
  ordenamiento de burbuja, concatenación de cadenas).
- No se agregaron type hints.
- El estado global y el canal de errores `ultimo_error` se mantienen porque
  cambiarlos alteraría la API que usan los tests.
- `ARCHIVO = "datos_ejemplo.json"` es relativo al directorio de trabajo; el
  README sugiere `cd src && python main.py`, que no encuentra los datos de
  ejemplo. Se documentó, no se cambió.

## 7. Aprendizajes técnicos

- Antes de refactorizar código sin cobertura conviene escribir una prueba de
  caracterización temporal (versión anterior contra versión nueva) en lugar
  de confiar solo en la suite existente.
- "Ruff sin errores" es una condición necesaria, no el objetivo: una excepción
  localizada y justificada puede ser más mantenible que una solución ingeniosa.
- Commits atómicos y una bitácora con resultados reales permiten auditar y
  revertir cada paso de forma independiente.

## 8. Reflexión personal **[COMPLETAR POR EL ALUMNO]**

Responder con experiencia propia (10-15 líneas, según el README):

- ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
  **[COMPLETAR]**
- ¿Qué propuso la IA que no habías notado? **[COMPLETAR]**
- ¿En qué casos tuviste que corregir o rechazar sus sugerencias? (p. ej. la
  decisión sobre `contadorVentas`, la ubicación de la bitácora o el nombre de
  la rama) **[COMPLETAR]**
- ¿Qué aprendiste sobre refactorizar con apoyo de IA? **[COMPLETAR]**

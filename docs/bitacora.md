# Bitácora de refactorización

**Nombre:**
**Matrícula:**
**Fecha:** 2026-10-08

Registro de cada refactorización realizada con Claude Code. Después de cada
cambio se ejecutan `python -m pytest -v` y `ruff check src`.

**Línea base (antes de refactorizar):** 20 tests aprobados, 20 errores de Ruff.

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| R1 | "Realiza la primera refactorización (R1): eliminación de código muerto. Tareas: 1. Elimina el import os sin utilizar en src/reportes.py. 2. Identifica y elimina comentarios obsoletos o código muerto cuya eliminación sea demostrablemente segura. 3. Elimina las declaraciones de codificación UTF-8 innecesarias señaladas por Ruff (UP009). 4. No modifiques la lógica de negocio ni las API públicas. 5. No modifiques tests/, pyproject.toml ni datos_ejemplo.json. 6. Ejecuta python -m pytest -v. 7. Ejecuta ruff check src. 8. Informa cuántos tests pasaron, cuántos errores de Ruff quedan y qué archivos modificaste. 9. Si falla algún test, corrige el problema antes de continuar. No realices otras refactorizaciones. No hagas commit todavía." | Se eliminaron: `import os` sin usar (`reportes.py`); `reporteViejoCSV()` (`reportes.py`); `calcular_descuento_viejo()`, la función comentada `exportar_txt` y la variable `MODO_DEBUG` (`gestor.py`); la declaración `# -*- coding: utf-8 -*-` de los 4 módulos de `src/`. Solo eliminaciones: 35 líneas borradas, 0 agregadas. | El código muerto confunde a quien lee y se mantiene sin aportar nada. Antes de borrar se verificó con `grep` que ningún elemento tiene llamadas en `src/`, `tests/` ni el README, y que no hay acceso dinámico (`getattr`, `globals()`, `import *`). En Python 3 la codificación por defecto ya es UTF-8, así que la declaración es redundante. Las API públicas documentadas en `CLAUDE.md` se conservan intactas. | ✅ 20/20 aprobados. Ruff: 20 → 13 errores |

## Reflexión final

*(Pendiente: se completará al terminar todas las refactorizaciones.)*

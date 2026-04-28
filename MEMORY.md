# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-28 (sesión 4)

## Fase actual
**Fase 4 — EN PROGRESO** — catálogos completos multi-motor, rama `fase-4`.
**WP activo: WP3** — Mercury multi-motor

---

## Resultado de WP1 Fase 4 (cerrado)

| Métrica | Valor |
|---|---|
| Registros enviados | 1.201 |
| Engine models detectados | 1 (VF150A 2018) |
| Articles únicos | 599 |
| Errores | 0 |

### Componentes entregados
- `adapters/pdf_adapter.py` — soporte `data_dir` + `_detect_page1_model` con normalización de whitespace
- `manufacturers/yamaha.py` — `data_dir=data/yamaha`, `page1_model_re`
- `common/normalizer.py` — engine_models dinámicos (misma lógica que serial_ranges en Fase 3)

---

## Resultado de WP2 Fase 4 (cerrado)

| Métrica | Valor |
|---|---|
| Registros enviados (validación) | 24.867 |
| Categorías cubiertas | 5 (diesel, genset, gasolina, transmisiones, accesorios) |
| Engine models (test 3×5) | 15 |
| Errores | 0 |

### Componentes entregados
- `manufacturers/volvo.py` — navegación dinámica de 5 categorías; warm-up Blazor; `engine_model_name` en source_fields
- `run.py` — log de rechazados limitado a 10 + contador
- `max_products_per_category` — parámetro opcional para tests (no presente en producción)

### Notas de producción
- Para scraping completo (870+ motores): eliminar `max_products_per_category` del CONFIG
- Tiempo estimado producción: ~3h por 18 motores → ~150h para los 870. Ejecutar por categorías separadas

---

## Próximo paso concreto

**WP3 — Mercury multi-motor:** ampliar `manufacturers/mercruiser.py` para navegar dinámicamente todas las categorías de mercruiserparts.com.
- Actualmente: `variant_path` hardcodeado a `350 MAG MPI Alpha/Bravo`
- Objetivo: scrapear dinámicamente desde las categorías (gas sterndrive, diesel sterndrive, inboard, towsports, etc.)
- `engine_model` = nombre de la variante en la página
- La estructura de mercruiserparts.com tiene 5 niveles de navegación (ver Fase 3 en PLAN_IMPLEMENTACION.md)
- Validar en Docker con subset antes de producción

---

## Resultado de Fase 2

| Métrica | Valor |
|---|---|
| Registros enviados | 3.653 |
| Articles únicos | 1.825 |
| Rechazados (sin part_no) | 502 |
| Errores | 0 |

### Componentes entregados
- `adapters/web_adapter.py` — `WebAdapter(BaseAdapter)` con Playwright Chromium headless
- `manufacturers/volvo.py` — config Volvo Penta TAMD72P-A (marinepartseurope.com)
- `Dockerfile` — `ENV PYTHONUNBUFFERED=1`

---

## Resultado de Fase 3

| Métrica | Valor |
|---|---|
| Registros enviados | 9.389 |
| Engine configurations | 10 |
| Articles únicos | 1.533 |
| Compatibilities | 7.844 |
| Errores | 0 |

### Componentes entregados
- `manufacturers/mercruiser.py` — Mercury Marine 350 MAG MPI Alpha/Bravo
- `common/normalizer.py` — soporte dinámico de N engine_configurations por serial range

---

## Contexto de integración

- **Endpoint Odoo:** `nautical.catalog.import` / `process_batch`
- **Auth:** `catalog-sync@nautica.internal` / `catalog-sync-2026!`
- **URL:** `http://host.docker.internal:8069` (Docker) / DB: `nautica`
- **Batch size:** 1.000 registros por llamado
- **Orden de envío requerido:** brand → engine_model → engine_configuration → article → compatibility

---

## Protocolos operativos (Agency)

- Sesión: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_SESION.md`
- Work Package: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_WORK_PACKAGE.md`
- Gate WP: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE_WORK_PACKAGE.md`
- Gate Fase: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE.md`
- Experiencias: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/docs/experiencias/catalog-scraper/`

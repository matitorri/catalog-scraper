# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-29 (sesión 5 — cierre)

## Fase actual
**Fase 5 — CERRADA** — merge a main completado 2026-04-29.
**Fase 6 en espera** — producción completa bloqueada hasta que sistema-gestion-nautica esté listo para producción. No hay rama activa.

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

## Resultado de WP3 Fase 4 (cerrado)

| Métrica | Valor |
|---|---|
| Registros enviados | 51.783 |
| Engine models detectados | 38 |
| Engine configurations | 61 |
| Articles únicos | 10.552 |
| Compatibilities | 41.131 |
| Errores | 0 |

### Componentes entregados
- `manufacturers/mercruiser.py` — navegación dinámica 5 categorías; `_collect_families`, `_collect_variants`, `_extract_variant`, `_parse_table` con `engine_model_name` en source_fields; `max_variants_per_family=1` para tests
- `common/normalizer.py` — soporte 4 modos: engine_model_name+serial_ranges (Mercury multi), engine_model sin serial (Yamaha/Volvo), serial sin engine_model (Mercruiser single Fase 3), estático

### Notas de producción
- Para scraping completo: eliminar `max_variants_per_family` del CONFIG
- Tiempo test (1 variante/familia, 5 categorías): ~2h

---

## Resultado WP1 Fase 5 (cerrado)

| Métrica | Valor |
|---|---|
| Mercury dry-run | 3.439 válidos, 0 errores |
| Volvo dry-run | 10.831 válidos, 0 errores |

Componentes: error handling en `_collect_families`, `_collect_variants`, `_extract_variant` (mercruiser) y `_collect_products`, `_extract_product`, warm-up (volvo); logging de progreso global en ambos; params de test renombrados a `_test_*`.

## Resultado WP2 Fase 5 (cerrado)

| Métrica | Valor |
|---|---|
| Mercury dry-run | 3.497 válidos, 3 lotes, 0 errores |
| Volvo dry-run | 11.891 válidos, 5 lotes, 0 errores |

### Componentes entregados
- `adapters/web_adapter.py` — `extract_streaming(config, on_batch)`: itera generador con browser abierto
- `manufacturers/mercruiser.py` — `extract_mercruiser` es generador: yield por familia completa
- `manufacturers/volvo.py` — `extract_volvo` es generador: yield por motor
- `run.py` — detecta `extract_streaming` → normaliza+envía por lote; fallback batch clásico para PDF

### Notas
- Yamaha (PDF adapter) usa el path clásico sin cambios — backward compatible
- Crash a hora N preserva las primeras N horas en Odoo; re-run es seguro por upsert

## Próximo paso concreto

**Cuando sistema-gestion-nautica esté listo para producción:**
1. Abrir rama `fase-6`
2. Remover `_test_max_*` de CONFIGs de Mercury y Volvo
3. Correr producción completa: Mercury (~870 motores), Volvo (~870 motores), Yamaha (PDFs)
4. Tiempo estimado: varios días en corridas secuenciales por categoría

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

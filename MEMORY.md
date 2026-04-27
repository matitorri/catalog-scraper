# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 3 — EN PROGRESO** — Mercury Marine (mercruiserparts.com), rama `fase-3`.
**WP activo: WP1** — `manufacturers/mercruiser.py`

---

## Resultado de Fase 2

| Métrica | Valor |
|---|---|
| Registros enviados | 3.653 |
| Articles únicos | 1.825 |
| Rechazados (sin part_no) | 502 |
| Errores | 0 |
| Commit de merge | 895bed0 (main) |

### Componentes entregados
- `adapters/web_adapter.py` — `WebAdapter(BaseAdapter)` con Playwright Chromium headless
- `manufacturers/volvo.py` — config Volvo Penta TAMD72P-A (marinepartseurope.com)
- `Dockerfile` — `ENV PYTHONUNBUFFERED=1`

---

## Próximo paso concreto

Implementar `manufacturers/mercruiser.py`:
- Navegar desde variante → serial ranges → subsistemas → tabla
- URL de prueba: `/5-7l-350-cu-in-v8-gm-350-mag-mpi-alpha-bravo`
- Brand: `Mercury Marine` | Engine model: `350 MAG MPI Alpha/Bravo`
- Engine configuration: una por rango serial, `serial_from`/`serial_to` del slug

---

## Contexto de integración

- **Endpoint Odoo:** `nautical.catalog.import` / `process_batch`
- **Auth:** `catalog-sync@nautica.internal` / `catalog-sync-2026!`
- **URL:** `http://localhost:8069` / DB: `nautica`
- **Batch size:** 1.000 registros por llamado
- **Orden de envío requerido:** brand → engine_model → engine_configuration → article → compatibility

---

## Protocolos operativos (Agency)

- Sesión: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_SESION.md`
- Work Package: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_WORK_PACKAGE.md`
- Gate WP: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE_WORK_PACKAGE.md`
- Gate Fase: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE.md`
- Experiencias: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/docs/experiencias/catalog-scraper/`

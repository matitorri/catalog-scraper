# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 2 — Web Adapter + Volvo — EN CURSO**
**WP activo: WP2 — Volvo config (navegación + parser)**

---

## Secuencia de WPs — Fase 2

| WP | Descripción | Estado |
|---|---|---|
| WP1 | WebAdapter scaffold (Playwright) | ✓ Completado |
| WP2 | Volvo config (navegación + parser) | En curso |
| WP3 | Integración end-to-end contra Odoo | Pendiente |

---

## Próximo paso concreto

Implementar WP2:
- `manufacturers/volvo.py`: config con `ADAPTER = WebAdapter`, `extract_fn` con lógica de navegación marinepartseurope.com (categoría → producto → explodedview → tabla)
- Adaptar lógica del POC (`/Users/matiastorrilla/projects/Prueba de catalogo/scraper_marine.py`) al patrón Strategy
- Criterio de cierre: extracción real de partes Volvo funcionando, shape del output conocido

---

## Contexto técnico Fase 2

- **Sitio:** `https://marinepartseurope.com` — Blazor Server (.NET/SignalR), sin Cloudflare, sin anti-bot
- **Stack:** Playwright headless Chromium (sync_api)
- **Flujo:** categoría → `/product/` → `/explodedview/?header=` → `table tbody tr`
- **POC de referencia:** `/Users/matiastorrilla/projects/Prueba de catalogo/scraper_marine.py`
- **WebAdapter es genérico** — la lógica de navegación y parseo vive en `manufacturers/volvo.py`, no en el adapter

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

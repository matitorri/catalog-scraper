# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 2 — Web Adapter + Volvo — EN CURSO**
**WP activo: WP1 — WebAdapter scaffold (Playwright)**

---

## Secuencia de WPs — Fase 2

| WP | Descripción | Estado |
|---|---|---|
| WP1 | WebAdapter scaffold (Playwright) | En curso |
| WP2 | Volvo config (navegación + parser) | Pendiente |
| WP3 | Integración end-to-end contra Odoo | Pendiente |

---

## Próximo paso concreto

Implementar WP1:
- `adapters/web_adapter.py`: `WebAdapter(BaseAdapter)` — recibe config con `extract_fn` callable, lanza Playwright Chromium headless, ejecuta callable con la page, retorna lista de dicts
- `requirements.txt`: agregar `playwright`
- `Dockerfile`: agregar `RUN playwright install chromium --with-deps`
- Criterio de cierre: adapter lanza y cierra browser sin errores con callable de prueba

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

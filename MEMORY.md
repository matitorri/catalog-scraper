# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 2 — Web Adapter + Volvo — EN CURSO**
**WP activo: WP3 — Integración end-to-end contra Odoo**

---

## Secuencia de WPs — Fase 2

| WP | Descripción | Estado |
|---|---|---|
| WP1 | WebAdapter scaffold (Playwright) | ✓ Completado |
| WP2 | Volvo config (navegación + parser) | ✓ Completado |
| WP3 | Integración end-to-end contra Odoo | En curso |

---

## Próximo paso concreto

Implementar WP3:
- Levantar Odoo local (`http://localhost:8069`)
- Ejecutar `python run.py --manufacturer volvo` (sin dry-run)
- Verificar 3.653 registros procesados, 0 errores en Odoo
- Ajustar normalizer solo si hay gaps reales con el schema de Odoo

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

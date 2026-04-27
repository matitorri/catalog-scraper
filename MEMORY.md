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

WP3 en curso — pipeline local ya validado (3.653 procesados, 0 errores). Pendiente: validar en Docker.

Próximo paso al abrir sesión:
1. Abrir Docker Desktop (computadora fue reiniciada)
2. Levantar Odoo: `cd /ruta/sistema-gestion-nautica && docker compose up -d`
3. Ejecutar en Docker:
```bash
docker run --rm \
  -e ODOO_URL=http://host.docker.internal:8069 \
  -e ODOO_DB=nautica \
  -e ODOO_USER=catalog-sync@nautica.internal \
  -e ODOO_PASS=catalog-sync-2026! \
  catalog-scraper --manufacturer volvo
```
4. Si la imagen no existe (reinicio limpia cache a veces): `docker build -t catalog-scraper . && docker run ...`

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

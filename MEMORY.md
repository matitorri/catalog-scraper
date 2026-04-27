# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 1 — Scaffold y primer adaptador — EN CURSO**
**WP activo: WP2 — PDF Adapter + Yamaha**

---

## Secuencia de WPs — Fase 1

| WP | Descripción | Estado |
|---|---|---|
| WP1 | Scaffold y contratos | ✓ Completado |
| WP2 | PDF Adapter + Yamaha | En curso |
| WP3 | Common layer (normalizer + sender) | Pendiente |
| WP4 | Runner + CLI | Pendiente |

---

## Próximo paso concreto

Implementar WP2:
1. El usuario provee el PDF de Yamaha
2. Explorar estructura del PDF con pdfplumber (tablas, páginas, campos disponibles)
3. Implementar `adapters/pdf_adapter.py` genérico
4. Implementar `manufacturers/yamaha.py` con config + field_mapping

---

## Contexto de integración

- **Endpoint Odoo:** `nautical.catalog.import` / `process_batch`
- **Auth:** `catalog-sync@nautica.internal` / `catalog-sync-2026!`
- **URL:** `http://localhost:8069` / DB: `nautica`
- **Contrato:** `sistema-gestion-nautica/docs/INTEGRACION_SCRAPER.md`
- **Batch size:** 1.000 registros por llamado
- **Orden de envío requerido:** brand → engine_model → engine_configuration → article → compatibility

---

## Protocolos operativos (Agency)

- Sesión: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_SESION.md`
- Work Package: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_WORK_PACKAGE.md`
- Gate WP: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE_WORK_PACKAGE.md`
- Gate Fase: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE.md`
- Experiencias: `/Users/matiastorrilla/projects/Meta-Agentic-Agency/docs/experiencias/catalog-scraper/`

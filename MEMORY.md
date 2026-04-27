# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 1 — Scaffold y primer adaptador — EN CURSO**
**Próximo paso: confirmar diseño de WPs y arrancar WP1**

---

## Secuencia de WPs — Fase 1

| WP | Descripción | Estado |
|---|---|---|
| WP1 | Scaffold y contratos | Pendiente |
| WP2 | Common layer (sender + normalizer) | Pendiente |
| WP3 | PDF Adapter + Yamaha | Pendiente |
| WP4 | Runner + CLI | Pendiente |

---

## Próximo paso concreto

Confirmar diseño de fase con el usuario y arrancar WP1:
- Estructura de carpetas + base.py + requirements.txt
- PDF de Yamaha real disponible para WP3

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

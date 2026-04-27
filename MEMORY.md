# MEMORY — Estado de la sesión

> Actualizar al cerrar cada sesión. Leer al abrir la siguiente.

---

## Última actualización
2026-04-27

## Fase actual
**Fase 1 — Scaffold y primer adaptador — EN CURSO**
**WP activo: WP4 — Runner + CLI**

---

## Secuencia de WPs — Fase 1

| WP | Descripción | Estado |
|---|---|---|
| WP1 | Scaffold y contratos | ✓ Completado |
| WP2 | PDF Adapter + Yamaha | ✓ Completado |
| WP3 | Common layer (normalizer + sender) | ✓ Completado |
| WP4 | Runner + CLI | En curso |

---

## Próximo paso concreto

Implementar WP4:
- `run.py`: `--manufacturer X` → importa `manufacturers/X.py` → extrae → normaliza → envía → imprime resumen
- Flag `--dry-run`: extrae y normaliza, no envía
- Criterio de cierre: `python run.py --manufacturer yamaha` ejecuta el pipeline completo de punta a punta

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

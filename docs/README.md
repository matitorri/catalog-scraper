# catalog-scraper

Pipeline de extracción de catálogos técnicos de fabricantes náuticos hacia Odoo 17.

Extrae datos de fuentes heterogéneas (PDF, web), los normaliza al schema acordado y los envía vía XML-RPC al módulo `nautical_catalog_import` del sistema `sistema-gestion-nautica`.

---

## Documentación

- [Plan de Implementación](PLAN_IMPLEMENTACION.md) — arquitectura, WPs, decisiones de diseño
- [Contrato de integración](../../sistema-gestion-nautica/docs/INTEGRACION_SCRAPER.md) — schema JSON, endpoint XML-RPC, ejemplos

## Uso

```bash
python run.py --manufacturer yamaha
python run.py --manufacturer yamaha --dry-run
```

## Agregar un fabricante

1. Crear `manufacturers/<nombre>.py` con `ADAPTER` y `CONFIG`
2. Sin cambios en código compartido

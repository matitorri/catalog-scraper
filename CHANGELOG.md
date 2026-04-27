# Changelog — catalog-scraper

## Fase 1 — Scaffold y primer adaptador (2026-04-27)

### Nuevo
- Pipeline completo de extracción de catálogos PDF → Odoo vía XML-RPC
- `adapters/base.py` — interfaz abstracta `BaseAdapter`
- `adapters/pdf_adapter.py` — extracción genérica desde PDF con pdfplumber (texto, no tablas)
- `manufacturers/yamaha.py` — config Yamaha VF150A 2018 (PDF)
- `common/normalizer.py` — transforma output del adapter al schema de Odoo; deduplica por clave de contrato; ordena brand → engine_model → engine_configuration → article → compatibility
- `common/sender.py` — auth XML-RPC + `send_batch` con lotes de 1.000 registros
- `run.py` — CLI: `--manufacturer X` y `--dry-run`
- `Dockerfile` — imagen `python:3.13-slim`, configurable por env vars, paridad local/producción
- `.env.example` — template de credenciales Odoo

### Resultado Yamaha VF150A 2018
- 667 artículos extraídos → 599 únicos (68 duplicados eliminados)
- 1.201 registros enviados a Odoo (1 brand + 1 engine_model + 1 engine_configuration + 599 articles + 599 compatibilities)
- 0 errores

### Workarounds activos
- Ninguno

### Diferido a Fase 2
- `adapters/web_adapter.py` — scraping genérico desde HTML
- `manufacturers/mercury.py` — config Mercury (web)

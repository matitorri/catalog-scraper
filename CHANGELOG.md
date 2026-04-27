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
- `manufacturers/volvo.py` — config Volvo (web)

---

## Fase 2 — Web Adapter + Volvo (2026-04-27)

### Nuevo
- `adapters/web_adapter.py` — `WebAdapter(BaseAdapter)` genérico con Playwright Chromium headless; delega navegación y parseo a `extract_fn` configurable por fabricante
- `manufacturers/volvo.py` — config Volvo Penta TAMD72P-A; navegación marinepartseurope.com (Blazor Server): product → explodedviews → tabla; captura level, status (tooltip oculto), remarks (detalle técnico)
- `Dockerfile` — `ENV PYTHONUNBUFFERED=1` para output en tiempo real en Docker
- `requirements.txt` — `playwright>=1.44`

### Resultado Volvo Penta TAMD72P-A
- 3.988 registros crudos extraídos (170 secciones / explodedviews)
- 3.653 registros enviados a Odoo (1 brand + 1 engine_model + 1 engine_configuration + 1.825 articles + 1.825 compatibilities)
- 502 rechazados (subpartes sin número de parte — comportamiento esperado)
- 0 errores — validado en Docker (`host.docker.internal`)

### Workarounds activos
- Ninguno

### Diferido a Fase 3
- `manufacturers/mercruiser.py` — Mercury Marine (mercruiserparts.com)

---

## Fase 3 — Mercury Marine (2026-04-27)

### Nuevo
- `manufacturers/mercruiser.py` — config Mercury Marine 350 MAG MPI Alpha/Bravo; navegación mercruiserparts.com (5 niveles): variante → serial ranges → subsistemas → tabla; extrae serial_from/serial_to por rango
- `common/normalizer.py` — soporte dinámico de múltiples `engine_configuration` por rango serial; backwards-compatible con Yamaha y Volvo; deduplicación de engine_configuration por (brand, model, serial_from, serial_to)

### Resultado Mercury Marine 350 MAG MPI Alpha/Bravo
- 11.221 registros crudos extraídos (10 rangos seriales, 400+ subsistemas)
- 9.389 registros enviados a Odoo (1 brand + 1 engine_model + 10 engine_configuration + 1.533 articles + 7.844 compatibilities)
- 0 rechazados, 0 errores — validado en Docker y confirmado en Odoo

### Workarounds activos
- Ninguno

### Diferido a Fase 4
- Volvo multi-motor: ampliar volvo.py para scrapear dinámicamente motores diesel, genset y transmisiones (no solo TAMD72P-A)
- Mercury multi-motor: ampliar mercruiser.py para scrapear todos los motores del catálogo

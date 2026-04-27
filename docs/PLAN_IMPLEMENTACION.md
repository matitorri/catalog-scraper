# Plan de Implementación — catalog-scraper

Pipeline de extracción de catálogos técnicos de fabricantes náuticos hacia Odoo 17 vía XML-RPC. Produce datos normalizados y los envía al módulo `nautical_catalog_import` del sistema `sistema-gestion-nautica`.

---

## Arquitectura — patrón Strategy

```
catalog-scraper/
  adapters/
    base.py          ← interfaz abstracta: extract(config) → list[dict]
    pdf_adapter.py   ← extracción genérica desde PDF (cualquier fabricante)
    web_adapter.py   ← scraping genérico desde HTML (cualquier fabricante)
  manufacturers/
    yamaha.py        ← declara: adapter=PdfAdapter + config específica de Yamaha
    mercury.py       ← declara: adapter=WebAdapter + config específica de Mercury
  common/
    sender.py        ← cliente XML-RPC: auth + send_batch(records, batch_size=1000)
    normalizer.py    ← normaliza output del adapter al schema de Odoo
  run.py             ← runner: --manufacturer X → instancia adapter → extrae → envía
  Dockerfile         ← imagen Python standalone, configurable por env vars
  .env.example       ← template de variables de entorno
```

**Principio clave:** los adaptadores son genéricos por tipo de fuente (PDF, web). La lógica específica de cada fabricante vive únicamente en su archivo de configuración en `manufacturers/`. Agregar un fabricante nuevo no requiere cambiar código compartido.

## Estrategia de despliegue — Docker

El scraper corre como contenedor standalone. La URL de Odoo se inyecta por variable de entorno — el mismo contenedor funciona en local y en producción sin cambios.

```bash
# Local (Odoo en Docker local)
docker run --rm \
  -v /ruta/al/yamaha.pdf:/data/yamaha.pdf \
  -e ODOO_URL=http://localhost:8069 \
  -e ODOO_DB=nautica \
  -e ODOO_USER=catalog-sync@nautica.internal \
  -e ODOO_PASS=catalog-sync-2026! \
  catalog-scraper --manufacturer yamaha

# Producción (Odoo en VPS)
docker run --rm \
  -v /ruta/al/yamaha.pdf:/data/yamaha.pdf \
  --env-file .env \
  catalog-scraper --manufacturer yamaha
```

| Entorno | ODOO_URL | Contenedor |
|---|---|---|
| Desarrollo local | `http://localhost:8069` | mismo imagen |
| Producción (VPS) | `https://nautica.midominio.com` | mismo imagen |

---

## Contrato de integración con Odoo

- **Endpoint:** `nautical.catalog.import` / `process_batch`
- **Auth:** `catalog-sync@nautica.internal` / DB: `nautica`
- **URL dev:** `http://localhost:8069`
- **Contrato completo:** `sistema-gestion-nautica/docs/INTEGRACION_SCRAPER.md`
- **Batch size:** 1.000 registros por llamado XML-RPC
- **Respuesta:** lista de dicts por registro — `{status: processed|error, ...}`
- **Idempotente:** `process_batch` es seguro de re-ejecutar

### Record types y orden de envío obligatorio

```
1. brand              → nautical.vessel.brand
2. engine_model       → nautical.engine.model
3. engine_configuration → nautical.engine.configuration
4. article            → nautical.article
5. compatibility      → nautical.article.compatibility
```

Las dependencias son hacia arriba — un `engine_model` falla si su `brand` no existe.

---

## Fase 1

**Objetivo:** pipeline funcional end-to-end para un fabricante (Yamaha, PDF) con los cuatro componentes base implementados.

| WP | Descripción | Estado |
|---|---|---|
| WP1 | Scaffold y contratos | ✓ Completado |
| WP2 | PDF Adapter + Yamaha | ✓ Completado |
| WP3 | Common layer (normalizer + sender) | ✓ Completado |
| WP4 | Runner + CLI | ✓ Completado |

### WP1 — Scaffold y contratos

**Objetivo:** estructura de proyecto lista para desarrollar. Sin lógica de negocio.

- Crear estructura de carpetas con `__init__.py`
- `adapters/base.py`: clase abstracta `BaseAdapter` con método `extract(config) → list[dict]`
- `requirements.txt`: dependencias (pdfplumber, beautifulsoup4, requests)
- `Dockerfile`: imagen `python:3.13-slim`, instala dependencias, monta `/data` para PDFs, entrypoint `python run.py`
- `.env.example`: template con `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASS`
- Definir contrato interno: qué estructura de dict debe devolver cada adapter

**Criterio de cierre:** `docker build -t catalog-scraper .` exitoso. Contenedor levanta sin errores.

---

### WP2 — PDF Adapter + Yamaha

**Objetivo:** ver los datos reales del PDF antes de escribir el normalizer. El input es la incógnita — el output (schema Odoo) ya está fijo.

**pdf_adapter.py:**
- Recibe config con: `file_path`, `page_range` (opcional), estrategia de extracción (tablas, texto libre)
- Usa `pdfplumber` para extracción de tablas y texto
- Devuelve lista de dicts crudos (sin normalizar)

**manufacturers/yamaha.py:**
- Define: `ADAPTER = PdfAdapter`
- Define: `CONFIG = { file_path, page_range, field_mapping, source_id: "yamaha_pdf" }`
- Field mapping: columnas del PDF → campos internos del adapter

**Criterio de cierre:** el adapter extrae registros reales del PDF de Yamaha y los imprime. Se conoce la forma exacta del input antes de escribir el normalizer.

---

### WP3 — Common layer

**Objetivo:** `normalizer.py` y `sender.py` operativos, construidos conociendo el gap real entre input (PDF Yamaha) y output (schema Odoo).

**normalizer.py:**
- Toma output crudo del adapter → mapea al schema Odoo por record_type → valida campos requeridos → ordena (brand primero, compatibility último)
- Rechaza registros inválidos con mensaje descriptivo antes de enviar

**sender.py:**
- Auth XML-RPC contra Odoo (uid por sesión)
- `send_batch(records, batch_size=1000)`: divide en lotes de 1.000, envía secuencialmente, retorna resultados
- Log de éxitos y errores por registro

**Criterio de cierre:** datos reales de Yamaha pasan por normalizer → sender → Odoo dev con `status: processed`.

---

### WP4 — Runner + CLI

**Objetivo:** `run.py` como punto de entrada único del pipeline.

```bash
python run.py --manufacturer yamaha
python run.py --manufacturer yamaha --dry-run   # extrae y normaliza, no envía
```

**run.py:**
- `--manufacturer X` → importa `manufacturers/X.py` dinámicamente
- Instancia adapter con config del fabricante
- Extrae → normaliza → envía
- Imprime resumen: N procesados, M errores con detalle

**Criterio de cierre:** `python run.py --manufacturer yamaha` ejecuta el pipeline completo de punta a punta con datos reales.

---

## Fabricantes planificados

| Fabricante | Adapter | Fuente | Estado |
|---|---|---|---|
| Yamaha | PdfAdapter | PDF catálogo | Fase 1 |
| Volvo | WebAdapter | Web scraping | Fase 2 |

---

## Fase 2

**Objetivo:** pipeline funcional end-to-end para un fabricante web (Volvo, marinepartseurope.com) con WebAdapter basado en Playwright.

| WP | Descripción | Estado |
|---|---|---|
| WP1 | WebAdapter scaffold (Playwright) | ✓ Completado |
| WP2 | Volvo config (navegación + parser) | Pendiente |
| WP3 | Integración end-to-end contra Odoo | Pendiente |

### WP1 — WebAdapter scaffold

**Objetivo:** `WebAdapter(BaseAdapter)` genérico con Playwright. Lanza browser, crea contexto/página, ejecuta callable de extracción recibido en config, cierra browser. Actualizar dependencias y Dockerfile.

**Componentes:**
- `adapters/web_adapter.py` — clase `WebAdapter(BaseAdapter)`
- `requirements.txt` — agregar `playwright`
- `Dockerfile` — instalar Playwright + Chromium

**Criterio de cierre:** adapter instanciable, lanza y cierra browser sin errores con un callable de prueba.

---

### WP2 — Volvo config

**Objetivo:** `manufacturers/volvo.py` con lógica de navegación de marinepartseurope.com y parser de tabla. Adaptar POC al patrón Strategy.

**Flujo de navegación:** categoría → `/product/` → `/explodedview/?header=` → `table tbody tr`

**Criterio de cierre:** extracción real de partes Volvo funcionando; shape del output conocido y validado.

---

### WP3 — Integración end-to-end

**Objetivo:** verificar que output WebAdapter+Volvo pasa por normalizer y sender sin gaps. Ajustar normalizer solo si hay diferencias reales.

**Criterio de cierre:** `python run.py --manufacturer volvo` ejecuta pipeline completo, 0 errores.

---

## Decisiones de diseño

### Por qué patrón Strategy
Los fabricantes usan fuentes heterogéneas (PDF, web, API). El adapter abstrae el origen; el normalizer abstrae el destino. El runner solo orquesta. Agregar un fabricante = agregar un archivo en `manufacturers/`.

### Orden de envío
El normalizer garantiza el orden `brand → engine_model → engine_configuration → article → compatibility` antes de enviar. Opciones: (a) ordenar en un solo batch, (b) enviar un batch por tipo. Se decide en WP2 según el tamaño real de los datos.

### Re-envío de errores
`process_batch` es idempotente. Los registros con `status: error` pueden re-enviarse en la siguiente ejecución sin riesgo de duplicados.

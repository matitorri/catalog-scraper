import re
import time
from urllib.parse import parse_qs, unquote, urlparse

from adapters.web_adapter import WebAdapter

BASE_URL = "https://marinepartseurope.com"
_BLAZOR_TIMEOUT = 45000
# URL de warm-up para inicializar la app Blazor en sesión fresca
_WARMUP_URL = "/en/dealer/other/category/marine%20diesel%20engines/product/tamd72p-a"


def _wait(page, selector, timeout=_BLAZOR_TIMEOUT):
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False


def _section_from_url(ev_link):
    params = parse_qs(urlparse(ev_link).query)
    header = params.get("header", [""])[0]
    return unquote(header) if header else ev_link.rstrip("/").split("/")[-1]


def _parse_table(page, section, source_id, engine_model_name):
    records = []
    rows = page.query_selector_all("table tbody tr")

    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) < 3:
            continue

        ref = cells[0].inner_text().strip()
        if not ref or not re.match(r"^\d", ref):
            continue

        # td[1]: optional <span class="dot"> (hierarchy) + description + <a> part number + optional extra detail
        name_cell = cells[1]
        level = 1 if name_cell.query_selector("span.dot") else 0
        part_link = name_cell.query_selector("a")
        part_no = part_link.inner_text().strip() if part_link else ""
        full_text = name_cell.inner_text().strip()

        if part_no and part_no in full_text:
            idx = full_text.index(part_no)
            description = full_text[:idx].strip()
            remarks_raw = full_text[idx + len(part_no):].strip()
            remarks = remarks_raw if remarks_raw else None
        else:
            description = full_text.strip()
            remarks = None

        qty = cells[2].inner_text().strip() if len(cells) > 2 else ""

        # td[3]: status icon — text lives in <div class="tooltip-inner"> (display:none)
        # inner_text() skips hidden elements; text_content() reads raw DOM text
        status = ""
        if len(cells) > 3:
            tooltip = cells[3].query_selector(".tooltip-inner")
            if tooltip:
                status = tooltip.text_content().strip()

        records.append({
            "source_fields": {
                "part_no":           part_no,
                "description":       description,
                "category":          section,
                "ref_no":            ref,
                "qty":               qty,
                "status":            status,
                "level":             level,
                "remarks":           remarks,
                "engine_model_name": engine_model_name,
            },
            "meta": {
                "source_id":   source_id,
                "record_type": "article",
            },
        })

    return records


def _collect_products(page, engine_url):
    """Navega al listing de la categoría y retorna lista de (engine_model_name, product_path)."""
    try:
        page.goto(BASE_URL + engine_url, wait_until="domcontentloaded", timeout=60000)
        _wait(page, "a[href*='/product/']", timeout=_BLAZOR_TIMEOUT)

        products = page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]'))
                .map(a => ({href: a.href, text: a.innerText.trim()}))
                .filter(l => l.href.includes('/product/')
                          && !l.href.includes('/explodedview/')
                          && l.text.length > 0)
        """)

        seen = set()
        result = []
        for p in products:
            path = p['href'].replace(BASE_URL, "")
            if path not in seen:
                seen.add(path)
                result.append((p['text'], path))
        return result
    except Exception as e:
        print(f"    ADVERTENCIA: no se pudo cargar categoría {engine_url} — {e}")
        return []


def _extract_product(page, product_path, engine_model_name, source_id):
    """Navega al producto y extrae todas sus partes desde los explodedviews."""
    try:
        page.goto(BASE_URL + product_path, wait_until="domcontentloaded", timeout=60000)
        if not _wait(page, "a[href*='/explodedview/']"):
            print(f" ADVERTENCIA: sin explodedviews")
            return []

        # Extraer hrefs ANTES de navegar (evita stale handles)
        anchors = page.query_selector_all("a[href]")
        ev_links = []
        for a in anchors:
            href = a.get_attribute("href") or ""
            if "/explodedview/" in href:
                path = href.replace(BASE_URL, "") if href.startswith(BASE_URL) else href
                ev_links.append(path)
        ev_links = list(dict.fromkeys(ev_links))

        records = []
        for ev_link in ev_links:
            section = _section_from_url(ev_link)
            page.goto(BASE_URL + ev_link, wait_until="domcontentloaded", timeout=60000)
            if not _wait(page, "table tbody tr"):
                continue
            recs = _parse_table(page, section, source_id, engine_model_name)
            records.extend(recs)
            time.sleep(1)

        return records
    except Exception as e:
        print(f" ADVERTENCIA: motor saltado ({product_path}) — {e}")
        return []


def extract_volvo(page, config):
    source_id = config["source_id"]
    all_records = []

    # Warm-up: la app Blazor requiere al menos una navegación a un producto
    # para inicializar el estado de sesión antes de poder usar los listings
    print("  Inicializando sesión Blazor...")
    try:
        page.goto(BASE_URL + _WARMUP_URL, wait_until="domcontentloaded", timeout=60000)
        _wait(page, "a[href*='/explodedview/']")
        print("  OK")
    except Exception as e:
        print(f"  ADVERTENCIA: warm-up falló — {e}. Los listings pueden no funcionar.")

    categories = config.get("categories", [])
    n_cats = len(categories)
    _max_per_cat = config.get("_test_max_per_cat")  # solo para validación, no usar en producción

    for cat_idx, (engine_url, cat_name) in enumerate(categories, 1):
        print(f"\n  Categoría {cat_idx}/{n_cats}: {cat_name}")
        products = _collect_products(page, engine_url)
        n_prod = len(products)
        print(f"  {n_prod} motores")
        if _max_per_cat:
            products = products[:_max_per_cat]

        for prod_idx, (engine_model_name, product_path) in enumerate(products, 1):
            print(f"    [{prod_idx}/{n_prod}] {engine_model_name} — acumulado: {len(all_records)}", end="", flush=True)
            records = _extract_product(page, product_path, engine_model_name, source_id)
            print(f" → {len(records)} partes")
            all_records.extend(records)

    return all_records


ADAPTER = WebAdapter

CONFIG = {
    "source_id":        "volvo_web",
    "extract_fn":       extract_volvo,
    "_test_max_per_cat": 1,  # remover antes de producción
    "categories": [
        ("/en/dealer/other/engine/marine%20diesel%20engines",             "marine diesel engines"),
        ("/en/dealer/other/engine/marine%20diesel%20engines%20genset",    "marine diesel engines genset"),
        ("/en/dealer/other/engine/marine%20gasoline%20engines",           "marine gasoline engines"),
        ("/en/dealer/other/engine/marine%20drives%20%26%20transmissions", "marine drives & transmissions"),
        ("/en/dealer/other/engine/accessories",                           "accessories"),
    ],
    "brand": {
        "name":       "Volvo Penta",
        "brand_type": "oem",
    },
    # engine_model y engine_configuration se detectan dinámicamente por motor desde el catálogo
}

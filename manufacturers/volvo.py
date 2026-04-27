import re
import time
from urllib.parse import parse_qs, unquote, urlparse

from adapters.web_adapter import WebAdapter

BASE_URL = "https://marinepartseurope.com"
_BLAZOR_TIMEOUT = 45000


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


def _parse_table(page, section, source_id):
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
                "part_no":     part_no,
                "description": description,
                "category":    section,
                "ref_no":      ref,
                "qty":         qty,
                "status":      status,
                "level":       level,
                "remarks":     remarks,
            },
            "meta": {
                "source_id":   source_id,
                "record_type": "article",
            },
        })

    return records


def extract_volvo(page, config):
    source_id = config["source_id"]
    all_records = []

    page.goto(BASE_URL + config["product_path"], wait_until="domcontentloaded", timeout=60000)
    _wait(page, "a[href*='/explodedview/']")

    anchors = page.query_selector_all("a[href]")
    ev_links = []
    for a in anchors:
        href = a.get_attribute("href") or ""
        if "/explodedview/" in href:
            path = href.replace(BASE_URL, "") if href.startswith(BASE_URL) else href
            ev_links.append(path)
    ev_links = list(dict.fromkeys(ev_links))

    print(f"    Explodedviews encontrados: {len(ev_links)}")

    for ev_link in ev_links:
        section = _section_from_url(ev_link)
        print(f"    Sección: {section}")

        page.goto(BASE_URL + ev_link, wait_until="domcontentloaded", timeout=60000)
        if not _wait(page, "table tbody tr"):
            print(f"      ADVERTENCIA: tabla no apareció tras {_BLAZOR_TIMEOUT / 1000}s")
            continue

        records = _parse_table(page, section, source_id)
        print(f"      Partes extraídas: {len(records)}")
        all_records.extend(records)
        time.sleep(1)

    return all_records


ADAPTER = WebAdapter

CONFIG = {
    "source_id":    "volvo_web",
    "product_path": "/en/dealer/other/category/marine%20diesel%20engines/product/tamd72p-a",
    "extract_fn":   extract_volvo,

    "brand": {
        "name":       "Volvo Penta",
        "brand_type": "oem",
    },
    "engine_model": {
        "name":       "TAMD72P-A",
        "brand_name": "Volvo Penta",
    },
    "engine_configuration": {
        "brand_name":        "Volvo Penta",
        "engine_model_name": "TAMD72P-A",
        "year_from":         None,
        "year_to":           None,
        "serial_from":       None,
        "notes":             "Marine diesel engine — marinepartseurope.com",
    },
}

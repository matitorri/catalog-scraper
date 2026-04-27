import re
import time

from adapters.web_adapter import WebAdapter

BASE_URL = "https://www.mercruiserparts.com"
_TIMEOUT = 30000


def _wait_table(page):
    try:
        page.wait_for_selector("table tbody tr", timeout=_TIMEOUT)
        return True
    except Exception:
        return False


def _parse_serial_range(text):
    upper = text.upper()
    m = re.search(r'\b([0-9][A-Z0-9]{6,})\s+THRU\s+([0-9][A-Z0-9]{6,})\b', upper)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r'\b([0-9][A-Z0-9]{6,})\s*&\s*UP\b', upper)
    if m:
        return m.group(1), None
    return None, None


def _parse_table(page, section, serial_from, serial_to, source_id):
    records = []
    rows = page.query_selector_all("table tbody tr")

    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) < 3:
            continue

        ref = cells[0].inner_text().strip()
        if not ref:
            continue

        part_no = cells[1].inner_text().strip()

        desc_raw = cells[2].inner_text().strip()
        m = re.match(r'^(-{4})+', desc_raw)
        if m:
            level = len(m.group(0)) // 4
            description = desc_raw[len(m.group(0)):].strip()
        else:
            level = 0
            description = desc_raw

        superseded_from = cells[3].inner_text().strip() if len(cells) > 3 else ""
        status          = cells[4].inner_text().strip() if len(cells) > 4 else ""
        notes           = cells[5].inner_text().strip() if len(cells) > 5 else ""
        qty             = cells[8].inner_text().strip() if len(cells) > 8 else ""

        records.append({
            "source_fields": {
                "part_no":         part_no,
                "description":     description,
                "category":        section,
                "ref_no":          ref,
                "qty":             qty,
                "status":          status,
                "level":           level,
                "remarks":         notes or None,
                "superseded_from": superseded_from or None,
                "serial_from":     serial_from,
                "serial_to":       serial_to,
            },
            "meta": {
                "source_id":   source_id,
                "record_type": "article",
            },
        })

    return records


def extract_mercruiser(page, config):
    source_id = config["source_id"]
    all_records = []

    page.goto(BASE_URL + config["variant_path"], wait_until="networkidle", timeout=60000)

    anchors = page.query_selector_all("a[href]")
    serial_ranges = []
    for a in anchors:
        href = a.get_attribute("href") or ""
        text = a.inner_text().strip()
        if not href.startswith("/") or not text:
            continue
        if "thru" in href.lower() or re.search(r'-up(-\d+)?$', href.lower()):
            serial_from, serial_to = _parse_serial_range(text)
            if serial_from:
                serial_ranges.append((href, serial_from, serial_to))

    print(f"    Rangos seriales: {len(serial_ranges)}")

    for sr_href, serial_from, serial_to in serial_ranges:
        label = f"{serial_from} — {serial_to or '& Up'}"
        print(f"    Serial range: {label}")

        page.goto(BASE_URL + sr_href, wait_until="networkidle", timeout=60000)
        sub_anchors = page.query_selector_all("a[href*='/bam/subassemblydetail/']")
        # Extraer href y texto antes de navegar — los handles quedan stale tras goto
        sub_items = [
            (a.get_attribute("href") or "", a.inner_text().strip())
            for a in sub_anchors
        ]
        print(f"      Subsistemas: {len(sub_items)}")

        for sub_href, section in sub_items:
            url = BASE_URL + sub_href if sub_href.startswith("/") else sub_href
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if not _wait_table(page):
                print(f"        ADVERTENCIA: tabla no apareció en {section}")
                continue

            records = _parse_table(page, section, serial_from, serial_to, source_id)
            all_records.extend(records)

        time.sleep(1)

    return all_records


ADAPTER = WebAdapter

CONFIG = {
    "source_id":    "mercruiser_web",
    "variant_path": "/5-7l-350-cu-in-v8-gm-350-mag-mpi-alpha-bravo",
    "extract_fn":   extract_mercruiser,

    "brand": {
        "name":       "Mercury Marine",
        "brand_type": "oem",
    },
    "engine_model": {
        "name":       "350 MAG MPI Alpha/Bravo",
        "brand_name": "Mercury Marine",
    },
    "engine_configuration": {
        "brand_name":        "Mercury Marine",
        "engine_model_name": "350 MAG MPI Alpha/Bravo",
        "year_from":         None,
        "year_to":           None,
        "notes":             "Gas sterndrive engine — mercruiserparts.com",
    },
}

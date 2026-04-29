import re
import time

from adapters.web_adapter import WebAdapter

BASE_URL = "https://www.mercruiserparts.com"
_TIMEOUT = 30000

# (category_path, family_link_prefix, label)
CATEGORIES = [
    ("/sterndrive-engines-gas",         "/engines-gas-",    "Sterndrive Gas"),
    ("/sterndrive-engines-diesel",       "/engines-diesel-", "Sterndrive Diesel"),
    ("/inboard-and-towsports-gas",       "/gas-",            "Inboard Gas"),
    ("/inboard-and-towsports-diesel",    "/diesel-",         "Inboard Diesel"),
    ("/inboard-and-towsports-us-marine", "/us-marine-",      "Inboard US Marine"),
]

_FAMILY_PREFIXES = ["engines-gas-", "engines-diesel-", "gas-", "diesel-", "us-marine-"]


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


def _family_content_id(family_href):
    slug = family_href.lstrip("/")
    for prefix in _FAMILY_PREFIXES:
        if slug.startswith(prefix):
            return slug[len(prefix):]
    return slug


def _parse_table(page, section, serial_from, serial_to, source_id, engine_model_name):
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
                "part_no":           part_no,
                "description":       description,
                "category":          section,
                "ref_no":            ref,
                "qty":               qty,
                "status":            status,
                "level":             level,
                "remarks":           notes or None,
                "superseded_from":   superseded_from or None,
                "serial_from":       serial_from,
                "serial_to":         serial_to,
                "engine_model_name": engine_model_name,
            },
            "meta": {
                "source_id":   source_id,
                "record_type": "article",
            },
        })

    return records


def _collect_families(page, category_path, family_prefix):
    page.goto(BASE_URL + category_path, wait_until="networkidle", timeout=60000)
    anchors = page.query_selector_all("a[href]")
    families = []
    seen = set()
    for a in anchors:
        href = a.get_attribute("href") or ""
        name = a.inner_text().strip()
        if href.startswith(family_prefix) and name and href not in seen:
            seen.add(href)
            families.append((href, name))
    return families


def _collect_variants(page, family_href):
    page.goto(BASE_URL + family_href, wait_until="networkidle", timeout=60000)
    content_id = _family_content_id(family_href)
    variant_prefix = "/" + content_id + "-"
    anchors = page.query_selector_all("a[href]")
    variants = []
    seen = set()
    for a in anchors:
        href = a.get_attribute("href") or ""
        name = a.inner_text().strip()
        if href.startswith(variant_prefix) and name and href not in seen:
            seen.add(href)
            variants.append((href, name))
    return variants


def _extract_variant(page, variant_href, engine_model_name, source_id):
    records = []
    page.goto(BASE_URL + variant_href, wait_until="networkidle", timeout=60000)

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

    print(f"        Rangos seriales: {len(serial_ranges)}")

    for sr_href, serial_from, serial_to in serial_ranges:
        label = f"{serial_from} — {serial_to or '& Up'}"
        print(f"        Serial range: {label}")

        page.goto(BASE_URL + sr_href, wait_until="networkidle", timeout=60000)
        sub_anchors = page.query_selector_all("a[href*='/bam/subassemblydetail/']")
        sub_items = [
            (a.get_attribute("href") or "", a.inner_text().strip())
            for a in sub_anchors
        ]
        print(f"          Subsistemas: {len(sub_items)}")

        for sub_href, section in sub_items:
            url = BASE_URL + sub_href if sub_href.startswith("/") else sub_href
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if not _wait_table(page):
                print(f"          ADVERTENCIA: tabla no apareció en {section}")
                continue

            recs = _parse_table(page, section, serial_from, serial_to, source_id, engine_model_name)
            records.extend(recs)

        time.sleep(1)

    return records


def extract_mercruiser(page, config):
    source_id = config["source_id"]
    max_variants = config.get("max_variants_per_family")
    all_records = []

    for cat_path, family_prefix, cat_label in CATEGORIES:
        print(f"  Categoría: {cat_label}")
        families = _collect_families(page, cat_path, family_prefix)
        print(f"    Familias: {len(families)}")

        for fam_href, fam_name in families:
            print(f"    Familia: {fam_name}")
            variants = _collect_variants(page, fam_href)
            if max_variants:
                variants = variants[:max_variants]
            print(f"      Variantes: {len(variants)}")

            for var_href, var_name in variants:
                print(f"      Variante: {var_name}")
                recs = _extract_variant(page, var_href, var_name, source_id)
                all_records.extend(recs)

    return all_records


ADAPTER = WebAdapter

CONFIG = {
    "source_id":  "mercruiser_web",
    "extract_fn": extract_mercruiser,

    "brand": {
        "name":       "Mercury Marine",
        "brand_type": "oem",
    },
    "max_variants_per_family": 1,
}

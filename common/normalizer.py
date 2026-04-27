RECORD_ORDER = ['brand', 'engine_model', 'engine_configuration', 'article', 'compatibility']

REQUIRED_FIELDS = {
    'brand':                ['name'],
    'engine_model':         ['name', 'brand_name'],
    'engine_configuration': ['brand_name', 'engine_model_name'],
    'article':              ['ref_code', 'name'],
    'compatibility':        ['article_ref', 'brand_name', 'engine_model_name'],
}


def normalize(raw_records: list[dict], config: dict) -> tuple[list[dict], list[dict]]:
    """
    Transforma los dicts crudos del adapter al schema de Odoo.

    Retorna (valid_records, rejected_records).
    valid_records están ordenados por record_type según dependencias de Odoo.
    rejected_records incluyen el motivo de rechazo en la clave 'error'.
    """
    source_id = config['source_id']
    brand_name = config['brand']['name']
    engine_model_name = config['engine_model']['name']

    normalized = {rt: [] for rt in RECORD_ORDER}

    # 1. Registros fijos desde la config del fabricante
    normalized['brand'].append({
        'source': source_id,
        'record_type': 'brand',
        'payload': {
            'name': brand_name,
            'brand_type': config['brand'].get('brand_type', 'oem'),
        },
    })

    normalized['engine_model'].append({
        'source': source_id,
        'record_type': 'engine_model',
        'payload': {
            'name': engine_model_name,
            'brand_name': brand_name,
        },
    })

    engine_cfg = config['engine_configuration']
    normalized['engine_configuration'].append({
        'source': source_id,
        'record_type': 'engine_configuration',
        'payload': {k: v for k, v in engine_cfg.items()},
    })

    # 2. Artículos y compatibilidades desde los registros extraídos
    rejected = []

    for raw in raw_records:
        sf = raw['source_fields']
        record_type = raw['meta']['record_type']

        if record_type != 'article':
            continue

        article_payload = {
            'ref_code':      sf['part_no'],
            'name':          sf['description'],
            'brand_name':    brand_name,
            'category_name': sf.get('category'),
            'article_type':  config['brand'].get('brand_type', 'oem'),
            'business_line': config.get('business_line', 'motor'),
        }

        error = _validate(article_payload, 'article')
        if error:
            rejected.append({**raw, 'error': error})
            continue

        normalized['article'].append({
            'source': source_id,
            'record_type': 'article',
            'payload': article_payload,
        })

        compatibility_payload = {
            'article_ref':       sf['part_no'],
            'brand_name':        brand_name,
            'engine_model_name': engine_model_name,
            'serial_from':       engine_cfg.get('serial_from'),
            'serial_to':         engine_cfg.get('serial_to'),
            'notes':             sf.get('remarks') or None,
        }

        error = _validate(compatibility_payload, 'compatibility')
        if error:
            rejected.append({**raw, 'error': error})
            continue

        normalized['compatibility'].append({
            'source': source_id,
            'record_type': 'compatibility',
            'payload': compatibility_payload,
        })

    valid = []
    for rt in RECORD_ORDER:
        valid.extend(normalized[rt])

    return valid, rejected


def _validate(payload: dict, record_type: str) -> str | None:
    for field in REQUIRED_FIELDS[record_type]:
        if not payload.get(field):
            return f"Campo requerido faltante: '{field}' en {record_type}"
    return None

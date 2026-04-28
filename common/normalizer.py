RECORD_ORDER = ['brand', 'engine_model', 'engine_configuration', 'article', 'compatibility']

# Claves de deduplicación por record_type (según INTEGRACION_SCRAPER.md)
DEDUP_KEYS = {
    'engine_model':         lambda p: (p['brand_name'], p['name']),
    'engine_configuration': lambda p: (p['brand_name'], p['engine_model_name'], p.get('serial_from'), p.get('serial_to')),
    'article':              lambda p: (p['ref_code'], p['brand_name']),
    'compatibility':        lambda p: (p['article_ref'], p['brand_name'], p['engine_model_name'], p.get('serial_from'), p.get('serial_to')),
}

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

    Soporta tres modos:
      - engine_model_name en source_fields: engine_models dinámicos (Yamaha multi-PDF)
      - serial_from en source_fields: engine_configurations dinámicas (Mercruiser)
      - ninguno: engine_model + engine_configuration estáticos desde config (Volvo, Yamaha single)
    """
    source_id = config['source_id']
    brand_name = config['brand']['name']
    static_engine_model_name = config.get('engine_model', {}).get('name')
    engine_cfg = config.get('engine_configuration', {})

    normalized = {rt: [] for rt in RECORD_ORDER}

    normalized['brand'].append({
        'source': source_id,
        'record_type': 'brand',
        'payload': {
            'name': brand_name,
            'brand_type': config['brand'].get('brand_type', 'oem'),
        },
    })

    # Si hay engine_model estático en config, emitirlo ahora.
    # En modo dinámico (Yamaha multi-PDF), se emitirán después del loop.
    if static_engine_model_name:
        normalized['engine_model'].append({
            'source': source_id,
            'record_type': 'engine_model',
            'payload': {
                'name': static_engine_model_name,
                'brand_name': brand_name,
            },
        })

    rejected = []
    serial_ranges_seen = {}   # Mercruiser: (serial_from, serial_to) → True
    engine_models_seen = {}   # Yamaha multi-PDF: engine_model_name → {year, serial_code}

    for raw in raw_records:
        sf = raw['source_fields']
        record_type = raw['meta']['record_type']

        if record_type != 'article':
            continue

        # engine_model_name: dinámico desde el artículo o estático desde config
        article_engine_model = sf.get('engine_model_name') or static_engine_model_name
        if not article_engine_model:
            rejected.append({**raw, 'error': 'engine_model_name no determinable'})
            continue

        # Registrar engine_models dinámicos (Yamaha multi-PDF)
        if sf.get('engine_model_name') and sf['engine_model_name'] not in engine_models_seen:
            engine_models_seen[sf['engine_model_name']] = {
                'year': sf.get('year'),
                'serial_code': sf.get('serial_code'),
            }

        # Registrar serial ranges dinámicos (Mercruiser)
        if sf.get('serial_from'):
            serial_ranges_seen[(sf['serial_from'], sf.get('serial_to'))] = True

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

        # Compatibilidad: usa serial del artículo si está disponible, sino el del config
        serial_from = sf.get('serial_from') if sf.get('serial_from') is not None else engine_cfg.get('serial_from')
        serial_to   = sf.get('serial_to')   if sf.get('serial_from') is not None else engine_cfg.get('serial_to')

        compatibility_payload = {
            'article_ref':       sf['part_no'],
            'brand_name':        brand_name,
            'engine_model_name': article_engine_model,
            'serial_from':       serial_from,
            'serial_to':         serial_to,
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

    # Generar engine_models y engine_configurations según el modo detectado
    if engine_models_seen:
        # Modo dinámico: Yamaha multi-PDF — un engine_model + una engine_configuration por PDF
        for em_name, em_data in engine_models_seen.items():
            normalized['engine_model'].append({
                'source': source_id,
                'record_type': 'engine_model',
                'payload': {'name': em_name, 'brand_name': brand_name},
            })
            cfg_payload = {
                'brand_name': brand_name,
                'engine_model_name': em_name,
            }
            if em_data.get('year'):
                cfg_payload['year_from'] = em_data['year']
                cfg_payload['year_to'] = em_data['year']
            if em_data.get('serial_code'):
                cfg_payload['notes'] = f"Serie {em_data['serial_code']}"
            normalized['engine_configuration'].append({
                'source': source_id,
                'record_type': 'engine_configuration',
                'payload': cfg_payload,
            })
    elif serial_ranges_seen:
        # Modo Mercruiser: serial ranges dinámicos para el engine_model estático del config
        for (serial_from, serial_to) in serial_ranges_seen:
            normalized['engine_configuration'].append({
                'source': source_id,
                'record_type': 'engine_configuration',
                'payload': {
                    **{k: v for k, v in engine_cfg.items() if k not in ('serial_from', 'serial_to')},
                    'serial_from': serial_from,
                    'serial_to':   serial_to,
                },
            })
    else:
        # Modo estático: Yamaha single PDF, Volvo — engine_configuration fija desde config
        normalized['engine_configuration'].append({
            'source': source_id,
            'record_type': 'engine_configuration',
            'payload': {k: v for k, v in engine_cfg.items()},
        })

    valid = []
    for rt in RECORD_ORDER:
        if rt in DEDUP_KEYS:
            normalized[rt] = _dedup(normalized[rt], DEDUP_KEYS[rt])
        valid.extend(normalized[rt])

    return valid, rejected


def _dedup(records: list[dict], key_fn) -> list[dict]:
    seen = set()
    result = []
    for r in records:
        k = key_fn(r['payload'])
        if k not in seen:
            seen.add(k)
            result.append(r)
    return result


def _validate(payload: dict, record_type: str) -> str | None:
    for field in REQUIRED_FIELDS[record_type]:
        if not payload.get(field):
            return f"Campo requerido faltante: '{field}' en {record_type}"
    return None

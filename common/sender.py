import os
import xmlrpc.client


def _get_config():
    return {
        'url':  os.environ['ODOO_URL'],
        'db':   os.environ['ODOO_DB'],
        'user': os.environ['ODOO_USER'],
        'password': os.environ['ODOO_PASS'],
    }


def authenticate(cfg: dict) -> int:
    common = xmlrpc.client.ServerProxy(f"{cfg['url']}/xmlrpc/2/common")
    uid = common.authenticate(cfg['db'], cfg['user'], cfg['password'], {})
    if not uid:
        raise RuntimeError(f"Autenticación fallida para {cfg['user']}@{cfg['url']}")
    return uid


def send_batch(records: list[dict], batch_size: int = 1000) -> dict:
    """
    Envía records a Odoo en lotes de batch_size.
    Retorna {'processed': int, 'errors': list[dict]}.
    """
    cfg = _get_config()
    uid = authenticate(cfg)
    models = xmlrpc.client.ServerProxy(f"{cfg['url']}/xmlrpc/2/object", allow_none=True)

    processed = 0
    errors = []

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        results = models.execute_kw(
            cfg['db'], uid, cfg['password'],
            'nautical.catalog.import', 'process_batch',
            [batch],
        )
        for result in results:
            if result.get('status') == 'error':
                errors.append(result)
            else:
                processed += 1

        print(f"  Lote {i // batch_size + 1}: {len(batch)} enviados, "
              f"{sum(1 for r in results if r.get('status') == 'processed')} procesados, "
              f"{sum(1 for r in results if r.get('status') == 'error')} errores")

    return {'processed': processed, 'errors': errors}

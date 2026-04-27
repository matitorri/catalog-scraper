"""
Script de prueba del pipeline completo contra Odoo dev.
Envía un lote mínimo: brand + engine_model + engine_configuration + 5 artículos.
"""
import os
os.environ.setdefault('ODOO_URL',  'http://localhost:8069')
os.environ.setdefault('ODOO_DB',   'nautica')
os.environ.setdefault('ODOO_USER', 'catalog-sync@nautica.internal')
os.environ.setdefault('ODOO_PASS', 'catalog-sync-2026!')

from manufacturers.yamaha import ADAPTER, CONFIG
from common.normalizer import normalize
from common.sender import authenticate, send_batch, _get_config

# 1. Extraer y normalizar
print("Extrayendo datos del PDF...")
raw = ADAPTER().extract(CONFIG)
valid, rejected = normalize(raw, CONFIG)
print(f"  {len(valid)} registros válidos, {len(rejected)} rechazados")

# 2. Lote mínimo de prueba: tipos fijos + primeros 5 artículos + 5 compatibilidades
fixed = [r for r in valid if r['record_type'] in ('brand', 'engine_model', 'engine_configuration')]
articles = [r for r in valid if r['record_type'] == 'article'][:5]
compatibilities = [r for r in valid if r['record_type'] == 'compatibility'][:5]
test_batch = fixed + articles + compatibilities
print(f"\nLote de prueba: {len(test_batch)} registros")
for r in test_batch:
    print(f"  {r['record_type']}: {r['payload'].get('name') or r['payload'].get('ref_code') or r['payload'].get('article_ref')}")

# 3. Verificar auth
print("\nAutenticando contra Odoo...")
try:
    cfg = _get_config()
    uid = authenticate(cfg)
    print(f"  Auth OK — uid={uid}")
except Exception as e:
    print(f"  Auth FALLIDA: {e}")
    exit(1)

# 4. Enviar
print("\nEnviando lote de prueba...")
result = send_batch(test_batch, batch_size=1000)
print(f"\nResultado: {result['processed']} procesados, {len(result['errors'])} errores")
if result['errors']:
    print("Errores:")
    for e in result['errors']:
        print(f"  {e}")

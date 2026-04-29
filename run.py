import argparse
import importlib
import sys


def main():
    parser = argparse.ArgumentParser(description='Catalog scraper — extrae catálogos de fabricantes y los envía a Odoo.')
    parser.add_argument('--manufacturer', required=True, help='Nombre del fabricante (ej: yamaha)')
    parser.add_argument('--dry-run', action='store_true', help='Extrae y normaliza sin enviar a Odoo')
    args = parser.parse_args()

    # Cargar módulo del fabricante dinámicamente
    try:
        module = importlib.import_module(f'manufacturers.{args.manufacturer}')
    except ModuleNotFoundError:
        print(f"Error: fabricante '{args.manufacturer}' no encontrado en manufacturers/")
        sys.exit(1)

    config = module.CONFIG
    adapter = module.ADAPTER()

    # Extraer
    print(f"[1/3] Extrayendo desde {config['source_id']}...")
    raw = adapter.extract(config)
    print(f"      {len(raw)} registros crudos extraídos")

    # Normalizar
    print("[2/3] Normalizando...")
    from common.normalizer import normalize
    valid, rejected = normalize(raw, config)

    from collections import Counter
    counts = Counter(r['record_type'] for r in valid)
    print(f"      {len(valid)} registros válidos: " +
          ', '.join(f"{counts[rt]} {rt}" for rt in ['brand', 'engine_model', 'engine_configuration', 'article', 'compatibility'] if counts.get(rt)))
    if rejected:
        print(f"      {len(rejected)} rechazados:")
        for r in rejected[:10]:
            print(f"        {r['error']} — {r['source_fields'].get('part_no', '?')}")
        if len(rejected) > 10:
            print(f"        ... y {len(rejected) - 10} más")

    if args.dry_run:
        print("[3/3] Dry-run — envío omitido.")
        return

    # Enviar
    print("[3/3] Enviando a Odoo...")
    from common.sender import send_batch
    result = send_batch(valid)

    print(f"\nResumen: {result['processed']} procesados, {len(result['errors'])} errores")
    if result['errors']:
        print("Errores:")
        for e in result['errors']:
            print(f"  {e}")


if __name__ == '__main__':
    main()

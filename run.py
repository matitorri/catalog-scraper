import argparse
import importlib
import sys
from collections import Counter


def _log_valid(valid, rejected, indent="      "):
    counts = Counter(r['record_type'] for r in valid)
    print(indent + f"{len(valid)} válidos: " +
          ', '.join(f"{counts[rt]} {rt}" for rt in
                    ['brand', 'engine_model', 'engine_configuration', 'article', 'compatibility']
                    if counts.get(rt)))
    if rejected:
        print(indent + f"{len(rejected)} rechazados:")
        for r in rejected[:10]:
            print(indent + f"  {r['error']} — {r['source_fields'].get('part_no', '?')}")
        if len(rejected) > 10:
            print(indent + f"  ... y {len(rejected) - 10} más")


def main():
    parser = argparse.ArgumentParser(description='Catalog scraper — extrae catálogos de fabricantes y los envía a Odoo.')
    parser.add_argument('--manufacturer', required=True, help='Nombre del fabricante (ej: yamaha)')
    parser.add_argument('--dry-run', action='store_true', help='Extrae y normaliza sin enviar a Odoo')
    args = parser.parse_args()

    try:
        module = importlib.import_module(f'manufacturers.{args.manufacturer}')
    except ModuleNotFoundError:
        print(f"Error: fabricante '{args.manufacturer}' no encontrado en manufacturers/")
        sys.exit(1)

    config = module.CONFIG
    adapter = module.ADAPTER()

    from common.normalizer import normalize

    if hasattr(adapter, 'extract_streaming'):
        # Modo streaming: normalizar y enviar después de cada lote
        from common.sender import send_batch

        print(f"Extrayendo {config['source_id']} en modo streaming...")
        if args.dry_run:
            print("(dry-run — envío omitido)")

        total_valid = 0
        total_rejected = 0
        batch_num = 0

        def on_batch(raw_batch):
            nonlocal total_valid, total_rejected, batch_num
            if not raw_batch:
                return
            batch_num += 1
            valid, rejected = normalize(raw_batch, config)
            total_valid += len(valid)
            total_rejected += len(rejected)
            print(f"  [lote {batch_num}]", end=" ")
            _log_valid(valid, rejected, indent="")
            if not args.dry_run:
                result = send_batch(valid)
                n_err = len(result['errors'])
                print(f"    enviado: {result['processed']} procesados"
                      + (f", {n_err} errores" if n_err else ""))
                for e in result['errors'][:3]:
                    print(f"      {e}")

        adapter.extract_streaming(config, on_batch)

        print(f"\nTotal: {total_valid} válidos, {total_rejected} rechazados en {batch_num} lotes")

    else:
        # Modo batch clásico (PDF adapter)
        print(f"[1/3] Extrayendo desde {config['source_id']}...")
        raw = adapter.extract(config)
        print(f"      {len(raw)} registros crudos extraídos")

        print("[2/3] Normalizando...")
        valid, rejected = normalize(raw, config)
        _log_valid(valid, rejected)

        if args.dry_run:
            print("[3/3] Dry-run — envío omitido.")
            return

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

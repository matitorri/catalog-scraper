from adapters.pdf_adapter import PdfAdapter

ADAPTER = PdfAdapter

CONFIG = {
    'source_id': 'yamaha_pdf',
    'file_path': 'data/VF150LA (6EH6) 2018.pdf',
    'skip_until_fig': True,
    'stop_at_marker': 'NUMERICAL INDEX',

    # Metadata del fabricante y modelo — usada por el normalizer
    # para generar los records brand, engine_model y engine_configuration
    'brand': {
        'name': 'Yamaha',
        'brand_type': 'oem',
    },
    'engine_model': {
        'name': 'VF150A',
        'brand_name': 'Yamaha',
    },
    'engine_configuration': {
        'brand_name': 'Yamaha',
        'engine_model_name': 'VF150A',
        'year_from': 2018,
        'year_to': 2018,
        'serial_from': '6EH-1005185',
        'notes': 'VF150LA variant — 6EH6 series',
    },
}

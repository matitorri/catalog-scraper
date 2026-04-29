from adapters.pdf_adapter import PdfAdapter

ADAPTER = PdfAdapter

CONFIG = {
    'source_id': 'yamaha_pdf',
    'data_dir': 'data/yamaha',
    'page1_model_re': r'([A-Z0-9]+)-(\d{4})\s*\(\s*([A-Z0-9]+)\s*\)',
    'skip_until_fig': True,
    'stop_at_marker': 'NUMERICAL INDEX',
    'brand': {
        'name': 'Yamaha',
        'brand_type': 'oem',
    },
    # engine_model y engine_configuration se detectan dinámicamente desde página 1 de cada PDF
}

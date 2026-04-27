from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """
    Contrato que todo adapter debe cumplir.

    extract() recibe la config del fabricante y devuelve una lista de dicts crudos
    en el formato intermedio del adapter — sin normalizar al schema de Odoo.
    El normalizer es quien mapea ese formato al schema de destino usando
    el field_mapping definido en el archivo del fabricante.

    Formato de retorno por registro:
    {
        "source_fields": { ...campos tal como vienen de la fuente... },
        "meta": {
            "source_id": str,   # identificador de la fuente, ej: "yamaha_pdf"
            "record_type": str, # brand | engine_model | engine_configuration | article | compatibility
        }
    }
    """

    @abstractmethod
    def extract(self, config: dict) -> list[dict]:
        ...

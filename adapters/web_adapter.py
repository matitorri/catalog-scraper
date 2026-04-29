from playwright.sync_api import sync_playwright

from adapters.base import BaseAdapter

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class WebAdapter(BaseAdapter):
    """
    Adapter genérico para sitios web renderizados por JavaScript.

    Lanza un browser Playwright Chromium headless, crea un contexto con
    user-agent configurable y delega la extracción a `extract_fn` —
    una función definida en el archivo del fabricante con la lógica
    específica de navegación y parsing.

    Config keys requeridos:
        source_id  (str)       identificador de la fuente, ej: "volvo_web"
        extract_fn (callable)  fn(page, config) -> list[dict] con source_fields + meta

    Config keys opcionales:
        user_agent (str)       sobreescribe el user-agent por defecto
        viewport   (dict)      sobreescribe {"width": 1440, "height": 900}
    """

    def extract(self, config: dict) -> list[dict]:
        extract_fn = config["extract_fn"]

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = browser.new_context(
                user_agent=config.get("user_agent", DEFAULT_USER_AGENT),
                viewport=config.get("viewport", {"width": 1440, "height": 900}),
                locale="en-US",
            )
            page = context.new_page()

            try:
                records = extract_fn(page, config)
            finally:
                browser.close()

        return records

    def extract_streaming(self, config: dict, on_batch) -> None:
        """Extrae en modo streaming: llama on_batch(records) por cada lote que emite extract_fn."""
        extract_fn = config["extract_fn"]

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = browser.new_context(
                user_agent=config.get("user_agent", DEFAULT_USER_AGENT),
                viewport=config.get("viewport", {"width": 1440, "height": 900}),
                locale="en-US",
            )
            page = context.new_page()

            try:
                for batch in extract_fn(page, config):
                    on_batch(batch)
            finally:
                browser.close()

import glob
import os
import re
import pdfplumber
from adapters.base import BaseAdapter

# En-dash (U+2013) usado por Yamaha en números de parte
_PART_NO_RE = re.compile(r'^[A-Z0-9]{2,}[–\-][A-Z0-9]+[–\-][A-Z0-9]+')
_FIG_RE = re.compile(r'^FIG\.\s*\d+\s+(.+)$')
_SKIP_LINES = {'REF.', 'PART NO. DESCRIPTION', 'NO. AX AL', 'REMARKS'}


def _parse_line(line):
    """
    Parsea una línea de datos de parte. Retorna dict o None si no es parseable.

    Formatos:
      <ref_no> <part_no> [dots]<desc> <qty1> [qty2] [remarks]
      <part_no> [dots]<desc> <qty1> [qty2] [remarks]   ← parte alternativa sin ref_no
    """
    line = line.strip()
    if not line:
        return None

    ref_no = None
    tokens = line.split()

    # Si el primer token es un número, es el REF NO
    if tokens[0].isdigit():
        ref_no = tokens[0]
        tokens = tokens[1:]

    if not tokens:
        return None

    # El primer token restante debe ser un número de parte
    if not _PART_NO_RE.match(tokens[0]):
        return None

    part_no = tokens[0].replace('–', '-')  # normalizar a hyphen ASCII
    tokens = tokens[1:]

    if not tokens:
        return None

    # Separar cantidades (dígitos al final) del resto de la descripción
    # Las quantities son los tokens numéricos al final, antes de REMARKS
    qty_tokens = []
    desc_tokens = []
    remarks_tokens = []

    # Recorrer tokens de atrás hacia adelante para encontrar qty y remarks
    i = len(tokens) - 1
    while i >= 0 and not tokens[i].isdigit():
        remarks_tokens.insert(0, tokens[i])
        i -= 1
    while i >= 0 and tokens[i].isdigit():
        qty_tokens.insert(0, tokens[i])
        i -= 1
    desc_tokens = tokens[:i + 1]

    description = ' '.join(desc_tokens + remarks_tokens if not qty_tokens else desc_tokens)
    if not description:
        return None

    # Extraer nivel de jerarquía de los dots al inicio de la descripción
    hierarchy_level = 0
    while description.startswith('.'):
        hierarchy_level += 1
        description = description[1:]
    description = description.strip()

    qty1 = qty_tokens[0] if len(qty_tokens) > 0 else None
    qty2 = qty_tokens[1] if len(qty_tokens) > 1 else None
    remarks = ' '.join(remarks_tokens) if qty_tokens else None

    return {
        'ref_no': ref_no,
        'part_no': part_no,
        'description': description,
        'qty1': qty1,
        'qty2': qty2,
        'remarks': remarks,
        'hierarchy_level': hierarchy_level,
    }


def _detect_page1_model(pdf, pattern_str: str) -> dict | None:
    """Extrae engine_model_name, year y serial_code de la página 1 del PDF."""
    if not pdf.pages:
        return None
    text = pdf.pages[0].extract_text() or ''
    # Normalizar saltos de línea y espacios múltiples para que el regex funcione
    # aunque el modelo y el serial code estén en líneas separadas
    text_normalized = re.sub(r'\s+', ' ', text)
    m = re.search(pattern_str, text_normalized)
    if not m:
        return None
    return {
        'engine_model_name': m.group(1),
        'year': int(m.group(2)),
        'serial_code': m.group(3),
    }


class PdfAdapter(BaseAdapter):

    def extract(self, config: dict) -> list[dict]:
        """
        Extrae artículos desde uno o varios PDFs de catálogo de partes.

        config keys:
          file_path       str   ruta a un PDF (modo single-file)
          data_dir        str   directorio con PDFs *.pdf (modo multi-file)
          page1_model_re  str   regex para detectar modelo en página 1 (multi-file)
          source_id       str   identificador de la fuente
          skip_until_fig  bool  saltar páginas hasta la primera FIG (default True)
          stop_at_marker  str   texto que indica fin de datos (ej: "NUMERICAL INDEX")
        """
        if 'data_dir' in config:
            return self._extract_directory(config)
        return self._extract_file(config, config['file_path'], page1_meta=None)

    def _extract_directory(self, config: dict) -> list[dict]:
        data_dir = config['data_dir']
        pattern = config.get('page1_model_re')
        all_records = []
        pdf_files = sorted(glob.glob(os.path.join(data_dir, '*.pdf')))
        if not pdf_files:
            print(f"  [warn] No se encontraron PDFs en {data_dir}")
            return []
        for pdf_path in pdf_files:
            page1_meta = None
            if pattern:
                with pdfplumber.open(pdf_path) as pdf:
                    page1_meta = _detect_page1_model(pdf, pattern)
                if page1_meta is None:
                    print(f"  [skip] {os.path.basename(pdf_path)} — modelo no detectado en página 1")
                    continue
                print(f"  [pdf] {os.path.basename(pdf_path)} → {page1_meta['engine_model_name']} ({page1_meta['year']})")
            records = self._extract_file(config, pdf_path, page1_meta)
            all_records.extend(records)
        return all_records

    def _extract_file(self, config: dict, file_path: str, page1_meta: dict | None) -> list[dict]:
        source_id = config['source_id']
        skip_until_fig = config.get('skip_until_fig', True)
        stop_at_marker = config.get('stop_at_marker', 'NUMERICAL INDEX')

        records = []
        in_data_section = False
        current_category = None

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.strip().split('\n')
                first_line = lines[0].strip()

                # Detectar fin de datos
                if stop_at_marker and stop_at_marker in first_line:
                    break

                # Detectar inicio de sección de datos (primera FIG)
                fig_match = _FIG_RE.match(first_line)
                if fig_match:
                    in_data_section = True
                    current_category = fig_match.group(1).strip()

                if not in_data_section:
                    continue

                for line in lines[1:]:
                    # Actualizar categoría si hay nueva FIG en la misma página
                    fig_match = _FIG_RE.match(line.strip())
                    if fig_match:
                        current_category = fig_match.group(1).strip()
                        continue

                    if line.strip() in _SKIP_LINES:
                        continue

                    parsed = _parse_line(line)
                    if parsed is None:
                        continue

                    source_fields = {**parsed, 'category': current_category}
                    if page1_meta:
                        source_fields.update(page1_meta)

                    records.append({
                        'source_fields': source_fields,
                        'meta': {
                            'source_id': source_id,
                            'record_type': 'article',
                        },
                    })

        return records

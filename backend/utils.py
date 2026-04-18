"""
Utilidades para procesamiento de archivos de documentos.

Proporciona funciones para extraer texto de diferentes formatos de archivo,
principalmente PDFs y DOCX, para el procesamiento de CVs.
"""

import pdfplumber

def extract_text_from_pdf(file_path):
    """
    Extrae texto completo de un archivo PDF.

    Args:
        file_path (str): Ruta al archivo PDF

    Returns:
        str: Texto extraído de todas las páginas del PDF
    """
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text

def extract_text_from_docx(file_path):
    """
    Extrae texto de un archivo DOCX.

    Nota: Actualmente es un placeholder. Debería implementarse
    con la biblioteca python-docx para extracción real.

    Args:
        file_path (str): Ruta al archivo DOCX

    Returns:
        str: Texto extraído del documento
    """
    return "Texto DOCX"
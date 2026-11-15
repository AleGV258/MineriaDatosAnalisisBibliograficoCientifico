"""Saca el texto de un PDF con PyMuPDF.

Abre el documento, recorre todas sus páginas y concatena el texto
de cada una en un solo string, separando páginas con un salto de
línea.
"""

import pymupdf


def extraer_texto_PDF(rutaPDF):
    """Regresa el texto completo del PDF como un solo string."""
    textoCompleto = ""

    with pymupdf.open(rutaPDF) as documento:
        for pagina in documento:
            textoCompleto += pagina.get_text("text", sort=True)
            textoCompleto += "\n"

    return textoCompleto

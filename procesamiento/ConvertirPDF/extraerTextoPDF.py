import pymupdf


def extraer_texto_PDF(rutaPDF):
    """Regresa el texto completo del PDF como un solo string"""
    textoCompleto = ""

    with pymupdf.open(rutaPDF) as documento:
        for pagina in documento:
            textoCompleto += pagina.get_text("text", sort=True)
            textoCompleto += "\n"

    return textoCompleto

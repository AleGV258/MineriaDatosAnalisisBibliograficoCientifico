import pymupdf

# Se extrae el texto de todas las páginas de un documento PDF
def extraerTextoPDF(rutaPDF):

    # Se inicializa el texto completo
    textoCompleto = ""

    # Se abre el documento PDF
    with pymupdf.open(rutaPDF) as documento:

        # Se recorren las páginas del documento
        for pagina in documento:

            # Se extrae el texto de la página
            textoPagina = pagina.get_text("text", sort=True)

            # Se agrega el texto al contenido completo
            textoCompleto += textoPagina

            # Se agrega un separador entre páginas
            textoCompleto += "\n"

    return textoCompleto

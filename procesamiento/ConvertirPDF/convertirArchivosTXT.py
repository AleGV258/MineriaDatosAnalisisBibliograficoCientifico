"""Convierte los PDFs encontrados a archivos TXT.

Recibe la lista que devuelve 'buscarArchivosPDF.buscar_archivos_PDF',
extrae el texto de cada documento con 'extraerTextoPDF.extraer_texto_PDF'
y lo guarda como TXT en 'datos/salida' con el mismo nombre del PDF.
"""

from pathlib import Path

from procesamiento.ConvertirPDF.extraerTextoPDF import extraer_texto_PDF


def convertir_archivos_TXT(archivosPDF):
    """Convierte cada PDF de la lista a TXT en 'datos/salida'.

    Regresa la lista con los nombres de los TXT generados.
    """
    carpetaSalida = (
        Path(__file__).resolve().parents[2]
        / "datos"
        / "salida"
    )
    carpetaSalida.mkdir(parents=True, exist_ok=True)

    archivosConvertidos = []
    for archivo in archivosPDF:
        rutaPDF = Path(archivo["ruta"])
        rutaTXT = carpetaSalida / rutaPDF.with_suffix(".txt").name

        texto = extraer_texto_PDF(rutaPDF)

        with open(rutaTXT, "w", encoding="utf-8") as archivoTXT:
            archivoTXT.write(texto)

        archivosConvertidos.append(rutaTXT.name)

    return archivosConvertidos

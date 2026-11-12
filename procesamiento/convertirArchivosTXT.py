from pathlib import Path

from procesamiento.extraerTextoPDF import extraerTextoPDF

# Se convierten los documentos PDF encontrados a archivos TXT
def convertirArchivosTXT(archivosPDF):

    # Se establece la carpeta donde se guardarán los TXT
    carpetaSalida = (
        Path(__file__).resolve().parent.parent
        / "datos"
        / "salida"
    )

    # Se crea la carpeta de salida si no existe
    carpetaSalida.mkdir(parents=True, exist_ok=True)

    archivosConvertidos = []

    # Se recorren los documentos PDF
    for archivo in archivosPDF:

        # Se obtiene la ruta del documento PDF
        rutaPDF = Path(archivo["ruta"])

        # Se establece el nombre del archivo TXT
        rutaTXT = carpetaSalida / rutaPDF.with_suffix(".txt").name

        # Se extrae el texto del documento PDF
        texto = extraerTextoPDF(rutaPDF)

        # Se guarda el texto en un archivo TXT
        with open(rutaTXT, "w", encoding="utf-8") as archivoTXT:
            archivoTXT.write(texto)

        archivosConvertidos.append(rutaTXT.name)

    return archivosConvertidos

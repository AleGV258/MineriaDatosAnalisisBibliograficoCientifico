from pathlib import Path

from procesamiento.ConvertirPDF.buscarArchivosPDF import carpeta_salida
from procesamiento.ConvertirPDF.extraerTextoPDF import extraer_texto_PDF


def convertir_archivos_TXT(archivosPDF):
    """
    Convierte cada PDF de la lista a TXT en 'datos/salida'

    Regresa la lista con los nombres de los TXT generados
    """
    carpetaSalida = carpeta_salida()
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

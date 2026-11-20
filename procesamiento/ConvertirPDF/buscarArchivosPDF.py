import sys
from pathlib import Path


def carpeta_salida() -> Path:
    """
    Carpeta 'datos/salida' junto al programa o al .exe

    Se resuelve la ruta para el ejecutable y que en su misma ruta se cree la carpeta de salida
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "datos" / "salida"
    return Path(__file__).resolve().parents[2] / "datos" / "salida"


def buscar_archivos_PDF(rutaDirectorio):
    """
    Regresa la lista de PDFs del directorio como diccionarios

    Cada elemento tiene 'nombre' y 'ruta'. Si la carpeta no existe truena con ValueError
    """
    rutaDirectorio = Path(rutaDirectorio)

    if not rutaDirectorio.exists() or not rutaDirectorio.is_dir():
        raise ValueError("El directorio seleccionado no es válido")

    archivosPDF = []
    for archivo in rutaDirectorio.iterdir():
        if archivo.is_file() and archivo.suffix.lower() == ".pdf":
            archivosPDF.append({
                "nombre": archivo.name,
                "ruta": str(archivo)
            })

    archivosPDF.sort(key=lambda archivo: archivo["nombre"].lower())
    return archivosPDF

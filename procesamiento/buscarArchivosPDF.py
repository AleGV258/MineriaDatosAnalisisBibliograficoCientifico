from pathlib import Path

# Se buscan todos los archivos PDF dentro del directorio seleccionado
def buscarArchivosPDF(rutaDirectorio):

    # Se convierte la ruta en un objeto Path
    rutaDirectorio = Path(rutaDirectorio)

    # Se comprueba que el directorio exista
    if not rutaDirectorio.exists() or not rutaDirectorio.is_dir():
        raise ValueError("El directorio seleccionado no es válido")

    archivosPDF = []

    # Se recorren los archivos del directorio seleccionado
    for archivo in rutaDirectorio.iterdir():

        # Se comprueba que sea un archivo PDF
        if archivo.is_file() and archivo.suffix.lower() == ".pdf":

            # Se almacena la información del documento
            informacionArchivo = {
                "nombre": archivo.name,
                "ruta": str(archivo)
            }

            archivosPDF.append(informacionArchivo)

    # Se ordenan los documentos por nombre
    archivosPDF.sort(key=lambda archivo: archivo["nombre"].lower())

    return archivosPDF

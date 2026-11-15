import json
from pathlib import Path

NOMBRE_CITAS = "citasFiltradas.json"
NOMBRE_FRECUENCIAS = "analisisFrecuencias.json"


def _carpeta_salida(directorio=None) -> Path:
    if directorio is None:
        directorio = (
            Path(__file__).resolve().parents[2] / "datos" / "salida"
        )
    carpeta = Path(directorio)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def _escribir_JSON(datos, nombre: str, directorio=None) -> Path:
    ruta = _carpeta_salida(directorio) / nombre
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    return ruta


def exportar_citas_JSON(resultados, directorio=None) -> Path:
    """
    Exporta las citas válidas y excluidas de cada documento

    Escribe un JSON con una entrada por documento: nombre, citas válidas, excluidas con su motivo y los conteos. Regresa la ruta
    """
    datos = [
        {
            "documento": r.get("documento"),
            "validas": r.get("validas", []),
            "excluidas": r.get("excluidas", []),
            "total": r.get("total", 0),
            "n_validas": r.get("n_validas", 0),
            "n_excluidas": r.get("n_excluidas", 0),
        }
        for r in resultados
    ]
    return _escribir_JSON(datos, NOMBRE_CITAS, directorio)


def exportar_frecuencias_JSON(frecuencias: dict, directorio=None) -> Path:
    """
    Exporta las tablas de frecuencia como listas de registros

    Recibe el dict de 'analizarFrecuencias.frecuencias' y escribe un JSON donde cada tabla es una lista de {'valor': ..., 'frecuencia': ...}
    Regresa la ruta creada
    """
    datos = {
        clave: df.to_dict(orient="records")
        for clave, df in frecuencias.items()
    }
    return _escribir_JSON(datos, NOMBRE_FRECUENCIAS, directorio)

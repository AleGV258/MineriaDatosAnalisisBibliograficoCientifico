"""Exporta el análisis de frecuencias a un CSV.

Recibe los resultados de 'ExcluirCitas.extraerReferencias.analizar_documento'
y escribe en 'datos/salida' un CSV con una sección por variable
(Autores, Títulos, Años, Editoriales). En cada sección las filas son
los valores encontrados y las columnas los documentos más un total,
para comparar la bibliografía de cada protocolo.
"""

from __future__ import annotations

import csv
from pathlib import Path

from procesamiento.AnalisisFrecuencias.frecuenciaAutores import contar_autores
from procesamiento.AnalisisFrecuencias.frecuenciaTitulos import contar_titulos
from procesamiento.AnalisisFrecuencias.frecuenciaAnios import contar_anios
from procesamiento.AnalisisFrecuencias.frecuenciaEditoriales import contar_editoriales

# Sección del CSV y el contador de frecuencias que le toca
VARIABLES = [
    ("Autores", contar_autores),
    ("Títulos", contar_titulos),
    ("Años", contar_anios),
    ("Editoriales", contar_editoriales),
]

NOMBRE_ARCHIVO = "AnalisisFrecuenciasBibliograficas.csv"


def _documentos_y_citas(resultados) -> list[tuple[str, list[str]]]:
    """Normaliza la entrada a pares (nombre_documento, citas_validas).

    Acepta los dicts de 'analizar_documento' o citas sueltas en texto,
    que se agrupan todas bajo el nombre 'Citas'.
    """
    documentos = []
    for elemento in resultados:
        if isinstance(elemento, dict):
            nombre = elemento.get("documento") or Path(
                elemento.get("ruta", "documento")
            ).stem
            documentos.append((nombre, elemento.get("validas", [])))
        elif isinstance(elemento, str):
            documentos.append(("Citas", [elemento]))
    return documentos


def _matriz_frecuencias(contar, documentos) -> tuple[list[str], list[list[int]]]:
    """Arma la tabla valor × documento para una variable.

    Corre el contador sobre las citas válidas de cada documento y
    cruza los conteos: una fila por valor distinto, una columna por
    documento y al final la columna 'Total'. Las filas van ordenadas
    por total descendente. Regresa (nombres_documentos, matriz).
    """
    conteos = []
    for nombre, citas in documentos:
        df = contar(citas)
        conteos.append(
            (nombre, dict(zip(df["valor"], df["frecuencia"])))
        )

    totales: dict[str, int] = {}
    for _, mapa in conteos:
        for valor, frecuencia in mapa.items():
            totales[valor] = totales.get(valor, 0) + frecuencia
    valores = sorted(totales, key=lambda v: (-totales[v], v))

    matriz = []
    for valor in valores:
        fila = [valor] + [mapa.get(valor, 0) for _, mapa in conteos]
        fila.append(totales[valor])
        matriz.append(fila)
    return [nombre for nombre, _ in conteos], matriz


def _escribir_seccion(escritor, titulo, contar, documentos) -> None:
    """Escribe una sección del CSV: encabezado, filas y línea vacía."""
    nombres, matriz = _matriz_frecuencias(contar, documentos)
    escritor.writerow([titulo] + nombres + ["Total"])
    escritor.writerows(matriz)
    escritor.writerow([])


def exportar_frecuencias_CSV(resultados, directorio=None) -> Path:
    """Genera el CSV del análisis de frecuencias en 'datos/salida'.

    Recibe los resultados de 'analizar_documento' y escribe
    'AnalisisFrecuenciasBibliograficas.csv'. Regresa la ruta creada.
    """
    if directorio is None:
        directorio = (
            Path(__file__).resolve().parents[2] / "datos" / "salida"
        )
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)

    ruta = directorio / NOMBRE_ARCHIVO
    documentos = _documentos_y_citas(resultados)
    # utf-8-sig para que Excel abra los acentos sin pedir importar
    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo)
        for titulo, contar in VARIABLES:
            _escribir_seccion(escritor, titulo, contar, documentos)
    return ruta

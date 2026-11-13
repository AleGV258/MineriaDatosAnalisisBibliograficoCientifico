"""Extracción de la sección de referencias de un protocolo.

Dado el TXT de un protocolo F-50-01, separa el
cuerpo del documento de su sección de referencias (en el corpus real es
"XI. REFERENCIAS BIBLIOGRÁFICAS"; la numeración puede variar entre
protocolos) y ejecuta el filtro de citas APA 7 de ``filtrarCitas``.
"""

from __future__ import annotations

import re
from pathlib import Path

from procesamiento.filtrarCitas import extraer_citas, filtrar_citas

# Encabezado de la sección de referencias: admite numeración romana o
# árabe y mayúsculas o mixtas ("XI. REFERENCIAS BIBLIOGRÁFICAS",
# "Referencias", "Bibliografía"). Debe ocupar una línea corta, completa.
_RE_ENCABEZADO = re.compile(
    r"^\s*(?:[IVXLC]{1,6}|\d{1,2})?\.?\s*-?\s*"
    r"(?:REFERENCIAS?\s*(?:BIBLIOGR[ÁA]FICAS?)?|BIBLIOGRAF[ÍI]A)"
    r"\s*$",
    re.IGNORECASE,
)

# Un encabezado es una línea corta; una frase larga que contenga la
# palabra "referencias" no lo es.
_MAX_LINEA_ENCABEZADO = 60


def _indice_seccion_referencias(lineas: list[str]) -> int:
    """Devuelve el índice de la última línea que parece el encabezado.

    Se usa la última coincidencia porque el índice o tabla de contenido
    del protocolo también menciona "Referencias" páginas antes de la
    sección real (en C1: la línea del índice y el encabezado real están a
    pocas líneas de distancia, y el índice puede aparecer antes).
    """
    candidatos = [
        i
        for i, linea in enumerate(lineas)
        if len(linea) <= _MAX_LINEA_ENCABEZADO and _RE_ENCABEZADO.match(linea)
    ]
    return candidatos[-1] if candidatos else -1


def separar_documento(texto: str) -> tuple[str, str]:
    """Divide el TXT en ``(cuerpo, seccion_referencias)``.

    Si no se encuentra la sección, el cuerpo es el texto completo y la
    sección queda vacía (el análisis de ese documento reporta cero citas).
    """
    lineas = texto.splitlines()
    idx = _indice_seccion_referencias(lineas)
    if idx == -1:
        return texto, ""
    cuerpo = "\n".join(lineas[:idx])
    seccion = "\n".join(lineas[idx + 1 :])
    return cuerpo, seccion


def analizar_documento(ruta_txt: str | Path) -> dict:
    """Analiza un protocolo convertido a TXT.

    Lee el TXT, separa la sección de referencias y aplica el filtro de
    APA 7 + citación en cuerpo (``filtrarCitas.filtrar_citas``).
    Devuelve::

        {
            "documento": "C1",
            "ruta": "...",
            "validas": [...],                       # citas que pasan todo
            "excluidas": [{"cita": ..., "motivo": ...}, ...],
            "total": 26,
            "n_validas": 22,
            "n_excluidas": 4,
        }

    El análisis de frecuencias consume ``validas``; ``excluidas`` alimenta el
    reporte de limpieza de la GUI.
    """
    ruta = Path(ruta_txt)
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    cuerpo, seccion = separar_documento(texto)
    resultado = filtrar_citas(extraer_citas(seccion), cuerpo)
    return {
        "documento": ruta.stem,
        "ruta": str(ruta),
        "validas": resultado["validas"],
        "excluidas": resultado["excluidas"],
        "total": len(resultado["validas"]) + len(resultado["excluidas"]),
        "n_validas": len(resultado["validas"]),
        "n_excluidas": len(resultado["excluidas"]),
    }

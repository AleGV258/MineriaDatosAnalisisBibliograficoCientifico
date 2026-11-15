"""Extracción de la sección de referencias de un protocolo.

Dado el TXT de un protocolo F-50-01, separa el
cuerpo del documento de su sección de referencias (en el corpus real es
"XI. REFERENCIAS BIBLIOGRÁFICAS"; la numeración puede variar entre
protocolos) y ejecuta el filtro de citas APA 7 de 'filtrarCitas'.
"""


from __future__ import annotations

import re
from pathlib import Path

from procesamiento.ExcluirCitas.filtrarCitas import extraer_citas, filtrar_citas

# Encabezado de la sección: "XI. REFERENCIAS BIBLIOGRÁFICAS", "Referencias",
# "Bibliografía", con numeración romana o árabe opcional
_RE_ENCABEZADO = re.compile(
    r"^\s*(?:[IVXLC]{1,6}|\d{1,2})\.?\s*-?\s*"
    r"(?:REFERENCIAS?\s*(?:BIBLIOGR[ÁA]FICAS?)?|BIBLIOGRAF[ÍI]A)"
    r"\s*$",
    re.IGNORECASE,
)

# Un encabezado ocupa una línea corta; una frase larga que mencione
# "referencias" en medio del texto no cuenta
_MAX_LINEA_ENCABEZADO = 60


def _indice_seccion_referencias(lineas: list[str]) -> int:
    """Regresa el índice de la línea del encabezado de referencias.

    Se usa la última coincidencia porque el índice del protocolo
    también menciona "Referencias" páginas antes de la sección real.
    """
    candidatos = [
        i
        for i, linea in enumerate(lineas)
        if len(linea) <= _MAX_LINEA_ENCABEZADO and _RE_ENCABEZADO.match(linea)
    ]
    return candidatos[-1] if candidatos else -1


def separar_documento(texto: str) -> tuple[str, str]:
    """Divide el TXT en '(cuerpo, seccion_referencias)'.

    Si no encuentra la sección, el cuerpo es el texto completo y la
    sección queda vacía (ese documento reporta cero citas).
    """
    lineas = texto.splitlines()
    idx = _indice_seccion_referencias(lineas)
    if idx == -1:
        return texto, ""
    cuerpo = "\n".join(lineas[:idx])
    seccion = "\n".join(lineas[idx + 1 :])
    return cuerpo, seccion


def analizar_documento(rutaTXT: str | Path) -> dict:
    """Analiza un protocolo en TXT y regresa sus citas válidas y excluidas.

    Lee el TXT, separa cuerpo y referencias, extrae las citas y les
    aplica el filtro APA 7 + citación en cuerpo. Devuelve un dict con
    'documento', 'ruta', 'validas', 'excluidas' (cada una con su
    'motivo'), 'total', 'n_validas' y 'n_excluidas'.
    """
    ruta = Path(rutaTXT)
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

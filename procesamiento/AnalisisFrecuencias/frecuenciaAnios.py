"""Cuenta cuántas citas se publicaron en cada año.

Cada cita se divide con 'dividirCita.dividir_cita', que extrae el año
del paréntesis y homologa las fechas imprecisas ('n.d.' / 's.f.')
como '"s/f"'.
"""

from __future__ import annotations

from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import dividir_cita


def contar_anios(citas: list[str]) -> pd.DataFrame:
    """Cuenta la frecuencia de cada año en la lista de citas.

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado
    de mayor a menor frecuencia. Las citas sin año se ignoran.
    """
    conteo: Counter = Counter(
        dividir_cita(cita)["anio"]
        for cita in citas
        if dividir_cita(cita)["anio"]
    )
    df = pd.DataFrame(
        conteo.most_common(), columns=["valor", "frecuencia"]
    )
    return df.reset_index(drop=True)

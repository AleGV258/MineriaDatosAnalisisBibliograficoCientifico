"""Cuenta cuántas veces aparece cada editorial o revista en las citas.

Cada cita se divide con 'dividirCita.dividir_cita', que saca la fuente
que va después del título hasta el enlace, cortada en la primera coma
para quitar volumen, número y páginas.
"""

from __future__ import annotations

from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import dividir_cita


def contar_editoriales(citas: list[str]) -> pd.DataFrame:
    """Cuenta la frecuencia de cada editorial en la lista de citas.

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado
    de mayor a menor frecuencia. Las citas sin fuente se ignoran.
    """
    conteo: Counter = Counter(
        dividir_cita(cita)["editorial"]
        for cita in citas
        if dividir_cita(cita)["editorial"]
    )
    df = pd.DataFrame(
        conteo.most_common(), columns=["valor", "frecuencia"]
    )
    return df.reset_index(drop=True)

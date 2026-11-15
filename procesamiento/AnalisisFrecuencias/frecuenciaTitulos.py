"""Cuenta cuántas veces se repite cada título en las citas válidas.

Cada cita se divide con 'dividirCita.dividir_cita', que saca el título
como el primer segmento después del año de publicación.
"""

from __future__ import annotations

from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import dividir_cita


def contar_titulos(citas: list[str]) -> pd.DataFrame:
    """Cuenta la frecuencia de cada título en la lista de citas.

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado
    de mayor a menor frecuencia. Las citas sin título se ignoran.
    """
    conteo: Counter = Counter(
        dividir_cita(cita)["titulo"]
        for cita in citas
        if dividir_cita(cita)["titulo"]
    )
    df = pd.DataFrame(
        conteo.most_common(), columns=["valor", "frecuencia"]
    )
    return df.reset_index(drop=True)

from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import tokenizar_cita


def contar_titulos(citas: list[str]) -> pd.DataFrame:
    """
    Cuenta la frecuencia de cada título en la lista de citas

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado de mayor a menor frecuencia. Las citas sin título se ignoran
    """
    conteo: Counter = Counter(
        tokenizar_cita(cita)["titulo"]
        for cita in citas
        if tokenizar_cita(cita)["titulo"]
    )
    df = pd.DataFrame(
        conteo.most_common(), columns=["valor", "frecuencia"]
    )
    return df.reset_index(drop=True)

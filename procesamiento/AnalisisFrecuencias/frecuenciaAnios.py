from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import tokenizar_cita


def contar_anios(citas: list[str]) -> pd.DataFrame:
    """
    Cuenta la frecuencia de cada año en la lista de citas

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado de mayor a menor frecuencia. Las citas sin año se ignoran
    """
    conteo: Counter = Counter(
        tokenizar_cita(cita)["anio"]
        for cita in citas
        if tokenizar_cita(cita)["anio"]
    )
    df = pd.DataFrame(
        conteo.most_common(), columns=["valor", "frecuencia"]
    )
    return df.reset_index(drop=True)

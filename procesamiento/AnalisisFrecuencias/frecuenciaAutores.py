from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import tokenizar_cita


def contar_autores(citas: list[str]) -> pd.DataFrame:
    """
    Cuenta la frecuencia del autor principal (el primero) de cada cita

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado de mayor a menor frecuencia. Los coautores no se cuentan: la variable autores se define por el primer autor de cada referencia
    """
    conteo: Counter = Counter()
    for cita in citas:
        autores = tokenizar_cita(cita)["autores"]
        if autores and autores[0]:
            conteo[autores[0]] += 1
    return _a_dataframe(conteo)


def _a_dataframe(conteo: Counter) -> pd.DataFrame:
    df = pd.DataFrame(
        [(valor, frecuencia) for valor, frecuencia in conteo.most_common()],
        columns=["valor", "frecuencia"],
    )
    return df.reset_index(drop=True)

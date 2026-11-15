from collections import Counter
import pandas as pd

from procesamiento.AnalisisFrecuencias.dividirCita import dividir_cita


def contar_autores(citas: list[str]) -> pd.DataFrame:
    """
    Cuenta la frecuencia de cada autor en la lista de citas

    Regresa un DataFrame con columnas 'valor' y 'frecuencia', ordenado de mayor a menor frecuencia. Si un autor sale repetido dentro de la misma cita solo cuenta una vez
    """
    conteo: Counter = Counter()
    for cita in citas:
        for autor in dict.fromkeys(dividir_cita(cita)["autores"]):
            if autor:
                conteo[autor] += 1
    return _a_dataframe(conteo)


def _a_dataframe(conteo: Counter) -> pd.DataFrame:
    df = pd.DataFrame(
        [(valor, frecuencia) for valor, frecuencia in conteo.most_common()],
        columns=["valor", "frecuencia"],
    )
    return df.reset_index(drop=True)

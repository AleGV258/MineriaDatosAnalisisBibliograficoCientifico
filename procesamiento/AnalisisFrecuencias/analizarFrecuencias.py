from procesamiento.AnalisisFrecuencias.frecuenciaAutores import contar_autores
from procesamiento.AnalisisFrecuencias.frecuenciaTitulos import contar_titulos
from procesamiento.AnalisisFrecuencias.frecuenciaAnios import contar_anios
from procesamiento.AnalisisFrecuencias.frecuenciaEditoriales import contar_editoriales


def _recolectar_citas(resultados) -> list[str]:
    citas: list[str] = []
    for elemento in resultados:
        if isinstance(elemento, dict):
            citas.extend(elemento.get("validas", []))
        elif isinstance(elemento, str):
            citas.append(elemento)
    return citas


def frecuencias(resultados) -> dict:
    """
    Calcula las frecuencias de las cuatro variables

    Regresa un dict con las claves 'autores', 'titulos', 'anios' y 'editoriales', donde cada valor es un DataFrame con columnas 'valor' y 'frecuencia'. Es la entrada que espera 'Graficas.graficarFrecuencias.generar_graficas'
    """
    # Etapa de análisis de frecuencias: cada variable usa su propio contador
    citas = _recolectar_citas(resultados)
    return {
        "autores": contar_autores(citas),
        "titulos": contar_titulos(citas),
        "anios": contar_anios(citas),
        "editoriales": contar_editoriales(citas),
    }

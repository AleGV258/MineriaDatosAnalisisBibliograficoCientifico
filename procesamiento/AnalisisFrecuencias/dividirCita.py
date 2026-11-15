"""
Divide una cita APA 7 en sus cuatro partes

Recibe una cita ya validada por 'ExcluirCitas.filtrarCitas' y la separa en autores, año, título y editorial/revista. El resultado es un diccionario que usan los contadores de 'AnalisisFrecuencias' para sacar los valores a contabilizar
"""

import re

# Año entre paréntesis: (2021), (2020, enero), (n.d.) o (s.f.)
_RE_ANIO = re.compile(
    r"\(\s*(?P<anio>\d{4}|n\.?\s*d\.?|s\.?\s*f\.?)"
    r"(?:\s*,\s*[A-Za-zÁÉÍÓÚÜÑáéíóúñü]+)?\s*\)",
    re.IGNORECASE,
)

# URL, DOI u ORCID: todo lo que sigue a la fuente no forma parte de ella
_RE_URL = re.compile(r"https?://|doi\.org|orcid\.org", re.IGNORECASE)

# Fecha de consulta ("Retrieved December 1, 2021 from ..."): tampoco es fuente
_RE_CONSULTA = re.compile(r"\bRetrieved\b", re.IGNORECASE)

# Cada autor APA es una unidad "Apellido(s), I." — con esto se agarran todos los autores del bloque, no solo el primero y el último
_RE_SEPARADOR_AUTORES = re.compile(
    r"([A-ZÁÉÍÓÚÜÑ][^,()]*?),\s*((?:[A-ZÁÉÍÓÚÜÑ]\.\s*)+)"
)

# Abreviaturas con punto que no deben cortar el título (Vol., Núm., Issue, etc.)
_RE_ABREV = re.compile(r"\b(?:Vol|Núm|Num|Issue|pp?|Ed|et al)\. ")

# Cuando lo que sigue al título es solo un volumen o número (10(2), 4, 3(1)) en realidad la cita no trae editorial y hay que dejarla vacía
_RE_VOLUMEN = re.compile(r"\d+(?:\(\d+\))?(?:[.,]\s*\d+)*")

# Paréntesis de volumen o número pegado al título o a la fuente
_RE_PAREN_DATOS = re.compile(r"\((?:Vol|Issue|Núm|Num)\b[^)]*\)")


def _normalizar(texto: str) -> str:
    return " ".join(texto.split())


def dividir_cita(cita: str) -> dict:
    """
    Parte una cita APA 7 en autores, año, título y editorial

    La estructura que se espera es: Apellido, I., & Apellido, I. (Año). Título. Fuente, vol(núm), págs. URL
    El proceso se basa en localizar el año entre paréntesis, todo lo anterior es el bloque de autores; lo que sigue al año se parte por puntos y el primer segmento es el título, el resto es la fuente de donde se saca la editorial (se corta en el enlace y en la primera coma para quitar volumen, número y páginas)
    Regresa un diccionario con las claves 'autores' (lista de apellidos), 'anio', 'titulo' y 'editorial'. Las fechas sin año ('n.d.' / 's.f.') se homologan como '"s/f"'. Si alguna parte no se puede extraer queda vacía; los contadores ignoran los vacíos
    """
    cita = _normalizar(cita)

    anio = _RE_ANIO.search(cita)
    if anio is None:
        return {"autores": [], "anio": "", "titulo": "", "editorial": ""}

    # Autores: todo lo que está antes del año. El bloque se ve así: "Cabello, J. M., Bru, E., & Junco, S." y cada unidad "Apellido, I." se reduce a su apellido -> ["Cabello", "Bru", "Junco"]
    bloqueAutores = cita[: anio.start()].rstrip(".").strip()
    unidades = [m.group(0).strip() for m in _RE_SEPARADOR_AUTORES.finditer(bloqueAutores)]
    # Si no hay iniciales se conserva el bloque completo (autor institucional)
    autores = (
        [_nombre_autor(parte) for parte in unidades]
        if unidades
        else [_nombre_autor(bloqueAutores)] if bloqueAutores else []
    )

    # Las fechas sin dígitos (n.d., s.f.) se unifican como "s/f"
    anioValor = anio.group("anio").strip()
    if not anioValor.isdigit():
        anioValor = "s/f"

    # Lo que sigue al año arranca con el punto que cierra el paréntesis
    resto = cita[anio.end():].lstrip()
    if resto.startswith("."):
        resto = resto[1:].strip()

    # Truco para partir el texto por ". " sin cortar abreviaturas como "Vol." o "et al.": se les cambia el punto por \x00, se parte y luego se restaura
    resto_protegido = _RE_ABREV.sub(lambda m: m.group(0)[:-1] + "\x00", resto)

    # El título es el primer segmento tras el año, lo demás es la fuente
    segmentos = [
        s.replace("\x00", " ") for s in re.split(r"\.\s+", resto_protegido) if s
    ]
    titulo = segmentos[0].strip() if segmentos else ""
    # Por si el enlace o la fecha de consulta quedaron pegados al título
    cortes_titulo = [
        m.start()
        for m in (_RE_URL.search(titulo), _RE_CONSULTA.search(titulo))
        if m is not None
    ]
    if cortes_titulo:
        titulo = titulo[: min(cortes_titulo)].strip()
    titulo = _RE_PAREN_DATOS.sub("", titulo).strip().rstrip(".")
    fuente = " ".join(segmentos[1:]) if len(segmentos) > 1 else ""

    # La editorial es la fuente hasta el enlace, cortada en la primera coma (así se quitan volumen, número y páginas)
    cortes = [
        m.start()
        for m in (_RE_URL.search(fuente), _RE_CONSULTA.search(fuente))
        if m is not None
    ]
    if cortes:
        fuente = fuente[: min(cortes)]
    editorial = fuente.split(",")[0].strip().rstrip(".")
    editorial = _RE_PAREN_DATOS.sub("", editorial).strip().rstrip(".")
    # Si lo extraído como fuente es puro volumen/número, no hay editorial
    if _RE_VOLUMEN.fullmatch(editorial):
        editorial = ""

    return {
        "autores": autores,
        "anio": anioValor,
        "titulo": titulo,
        "editorial": editorial,
    }


def _nombre_autor(parte: str) -> str:
    """
    Reduce un autor a su apellido o conserva el nombre institucional

    En 'Apellido, I.' se toma lo anterior a la primera coma ('Trujillo Romero, U.' -> 'Trujillo Romero'), en autores institucionales sin iniciales se conserva la frase completa ('Comisión Nacional de Bioética' queda igual)
    """
    parte = parte.strip().rstrip(".").strip()
    if "," in parte:
        return parte.split(",")[0].strip()
    return parte

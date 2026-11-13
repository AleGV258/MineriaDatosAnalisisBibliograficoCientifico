"""Filtro de citas bibliográficas según el formato APA 7.

Dado el texto de una sección de referencias y el cuerpo
del documento, este módol...

1. separa el texto en citas individuales (``extraer_citas``),
2. valida la estructura APA 7 de cada cita (``es_apa7``),
3. comprueba que la cita aparezca en el cuerpo (``cita_en_cuerpo``), y
4. devuelve válidas y excluidas con su motivo (``filtrar_citas``).

Formato observado en el corpus real (F-50-01, protocolo C1, sección
"XI. REFERENCIAS BIBLIOGRÁFICAS")::

    Apellido, I., & Apellido, I. (Año). Título. Fuente, vol(núm), págs. https://doi.org/...
    Organismo Institucional. (Año). Título del informe.
    Apellido, I. (n.d.). Título. https://...

Las citas van sin numerar, envueltas en varias líneas y mezcladas con
números de página y la firma de la autora; ``extraer_citas`` tolera ese ruido.
"""

from __future__ import annotations

import re

# Año entre paréntesis: (2021), (2020, enero), (n.d.) o (s.f.).
_RE_ANIO = re.compile(
    r"\(\s*(?P<anio>\d{4}|n\.?\s*d\.?|s\.?\s*f\.?)"
    r"(?:\s*,\s*[A-Za-zÁÉÍÓÚÜÑáéíóúñü]+)?\s*\)",
    re.IGNORECASE,
)
# Inicio de cita: línea que empieza con mayúscula y contiene un año.
_RE_INICIO_CITA = re.compile(r"^[A-ZÁÉÍÓÚÜÑ]")
# Ruido: números de página sueltos y encabezados de sección.
_RE_LINEA_RUIDO = re.compile(r"^\s*\d{1,3}\s*$")
_RE_ENCABEZADO = re.compile(r"REFERENCIA|BIBLIOGRAF", re.IGNORECASE)
# Firma o nota final: 2 a 5 palabras capitalizadas sin puntuación
# ("Ruth Aurelia Soto Fuentes").
_RE_FIN_SECCION = re.compile(
    r"^[A-ZÁÉÍÓÚÜÑ][a-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúñü]+){1,4}$"
)
# URL o DOI en cualquier parte de la cita.
_RE_URL = re.compile(r"https?://|doi\.org|orcid\.org", re.IGNORECASE)
# Autor con iniciales: "Abreu, E." / "Rodríguez, A., & Balbuena, M."
_RE_AUTOR_INICIALES = re.compile(r"^[A-ZÁÉÍÓÚÜÑ][\w\-']+\s*,\s*[A-ZÁÉÍÓÚÜÑ]")
# Autor institucional: dos o más palabras capitalizadas
# ("Comisión Nacional de Bioética").
_RE_AUTOR_INSTITUCIONAL = re.compile(
    r"^[A-ZÁÉÍÓÚÜÑ][\w\-']*"
    r"(?:\s+(?:de|del|la|las|los|y|e|of|the|[A-ZÁÉÍÓÚÜÑ][\w\-']))+"
)

# Separación máxima entre apellido y año dentro de una cita en el cuerpo.
_VENTANA_CITA = 60


def _normalizar(texto: str) -> str:
    """Colapsa saltos de línea y espacios repetidos."""
    return " ".join(texto.split())


def extraer_citas(texto_seccion: str) -> list[str]:
    """Separa la sección de referencias en citas individuales.

    Acepta el texto tal como sale de la conversión PDF→TXT: citas sin
    numerar, envueltas en varias líneas, con números de página y la firma
    de la autora intercalados. Los encabezados, los números de página y
    todo lo que venga después de una firma se ignoran.
    """
    citas: list[str] = []
    actual: list[str] = []
    en_cita = False

    def cerrar_actual() -> None:
        nonlocal actual, en_cita
        if actual:
            citas.append(_normalizar(" ".join(actual)))
        actual, en_cita = [], False

    for linea in texto_seccion.splitlines():
        linea = linea.strip()
        if not linea or _RE_LINEA_RUIDO.match(linea) or _RE_ENCABEZADO.search(linea):
            continue
        if _RE_FIN_SECCION.match(linea) and not _RE_ANIO.search(linea):
            # Firma de la autora o nota final: corta la última cita.
            cerrar_actual()
            continue
        if _RE_INICIO_CITA.match(linea) and _RE_ANIO.search(linea):
            cerrar_actual()
            actual, en_cita = [linea], True
        elif en_cita:
            actual.append(linea)
    cerrar_actual()

    # Descarta bloques sin año (párrafos sueltos, anexos).
    return [cita for cita in citas if _RE_ANIO.search(cita)]


def es_apa7(cita: str) -> tuple[bool, str | None]:
    """Valida la estructura APA 7 de una cita individual.

    Estructura esperada: ``Autor(es). (Año). Título. Fuente``. La fuente
    puede ser una editorial o revista, un URL/DOI, o quedar implícita en
    autores institucionales (la institución edita su propio informe).

    Devuelve ``(True, None)`` si la cita cumple la estructura y
    ``(False, motivo)`` en caso contrario, con el motivo en español listo
    para mostrarse en la GUI.
    """
    cita = _normalizar(cita)
    if not cita:
        return False, "cita vacía"

    anio = _RE_ANIO.search(cita)
    if anio is None:
        return False, "falta el año de publicación (se espera (2021) o (n.d.))"

    autores = cita[: anio.start()].strip().rstrip(".").strip()
    if not autores:
        return False, "falta el autor (se espera Apellido, I. u organismo)"
    if not (
        _RE_AUTOR_INICIALES.match(autores)
        or _RE_AUTOR_INSTITUCIONAL.match(autores)
    ):
        return False, "autor con formato no APA 7 (se espera Apellido, I. u organismo)"

    resto = cita[anio.end():].lstrip()
    if not resto.startswith("."):
        return False, "formato no APA 7: falta el punto después del año"
    resto = resto[1:].strip()
    if len(resto) < 10:
        return False, "falta el título del trabajo"

    segmentos = [s for s in re.split(r"\.\s+", resto) if s]
    tiene_url = bool(_RE_URL.search(resto))
    if (
        not tiene_url
        and len(segmentos) < 2
        and not _RE_AUTOR_INSTITUCIONAL.match(autores)
    ):
        return False, "falta la fuente (editorial o revista) después del título"
    return True, None


def cita_en_cuerpo(cita: str, cuerpo: str) -> bool:
    """Indica si la cita aparece mencionada en el cuerpo del documento.

    Reconoce las formas narrativas y parentéticas habituales:
    ``Abreu (2021)``, ``Abreu et al. (2021)``, ``(Ito, 1991:1)`` y las
    variantes sin fecha ``(n.d.)`` / ``(s.f.)``.
    """
    cita = _normalizar(cita)
    anio = _RE_ANIO.search(cita)
    if anio is None:
        return False

    bloque_autores = cita[: anio.start()].strip().rstrip(".")
    if not bloque_autores:
        return False
    if "," in bloque_autores:
        apellido = bloque_autores.split(",")[0].split()[0]
    else:
        apellido = bloque_autores.split()[0]
    apellido = re.escape(apellido)

    if anio.group("anio").isdigit():
        patron = (
            rf"{apellido}\b[^;\n]{{0,{_VENTANA_CITA}}}?"
            rf"\(?\s*{anio.group('anio')}\b"
        )
    else:
        patron = (
            rf"{apellido}\b[^;\n]{{0,{_VENTANA_CITA}}}?"
            r"\(?\s*(?:n\.?\s*d\.?|s\.?\s*f\.?)"
        )
    return re.search(patron, cuerpo, re.IGNORECASE) is not None


def filtrar_citas(citas: list[str], cuerpo: str) -> dict:
    """Filtra una lista de citas según APA 7 y citación en el cuerpo.

    Devuelve ``{"validas": [...], "excluidas": [{"cita": ..., "motivo": ...}]}``.
    Una cita es válida solo si cumple la estructura APA 7 (``es_apa7``) y
    además está citada en el cuerpo del documento (``cita_en_cuerpo``).
    """
    validas: list[str] = []
    excluidas: list[dict] = []
    for cita in citas:
        normalizada = _normalizar(cita)
        estructura_ok, motivo = es_apa7(normalizada)
        if not estructura_ok:
            excluidas.append({"cita": normalizada, "motivo": motivo})
        elif not cita_en_cuerpo(normalizada, cuerpo):
            excluidas.append(
                {"cita": normalizada, "motivo": "no citada en el cuerpo del documento"}
            )
        else:
            validas.append(normalizada)
    return {"validas": validas, "excluidas": excluidas}

"""Gráficas de frecuencias por variable.

Recibe la salida de ``analizarFrecuencias.frecuencias``, un dict con las
claves "autores", "titulos", "anios" y "editoriales", donde cada valor es
un DataFrame con columnas ["valor", "frecuencia"] (frecuencia absoluta).
Devuelve una figura matplotlib por variable, lista para incrustarse en la
GUI con ``FigureCanvasTkAgg``, y permite guardarlas como PNG.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # generación de figuras sin servidor gráfico

import matplotlib.pyplot as plt
import pandas as pd

#: Cantidad máxima de barras por variable muy poblada (top N).
TOP_N = 10

TITULOS = {
    "autores": "Frecuencia de autores",
    "titulos": "Frecuencia de títulos",
    "anios": "Frecuencia por año",
    "editoriales": "Frecuencia de editoriales y revistas",
}

ETIQUETA_EJE = {
    "autores": "Autores",
    "titulos": "Títulos",
    "editoriales": "Editoriales y revistas",
}

COLOR_BARRAS = "#4C72B0"


def _figura_vacia(titulo: str) -> plt.Figure:
    """Figura de respaldo cuando una variable no tiene datos."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(titulo)
    ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", fontsize=14)
    ax.set_axis_off()
    return fig


def _ordenar(df: pd.DataFrame, clave: str) -> pd.DataFrame:
    """Ordena y recorta la tabla según la variable.

    "anios" muestra todos los años en orden ascendente; el resto se
    ordena por frecuencia descendente y se recorta al top ``TOP_N``.
    """
    df = df.copy()
    if clave == "anios":
        with contextlib.suppress(ValueError, TypeError):
            df["valor"] = df["valor"].astype(int)
        return df.sort_values("valor")
    return df.sort_values("frecuencia", ascending=False).head(TOP_N)


def generar_graficas(frecuencias: dict) -> dict:
    """Genera una figura por variable a partir de las tablas de frecuencia.

    "anios" usa barras verticales; autores, títulos y editoriales usan
    barras horizontales para que los nombres largos sean legibles. Una
    variable sin datos devuelve una figura con el texto "Sin datos".
    """
    figuras: dict = {}
    for clave, titulo in TITULOS.items():
        df = frecuencias.get(clave, pd.DataFrame(columns=["valor", "frecuencia"]))
        if not isinstance(df, pd.DataFrame) or df.empty:
            figuras[clave] = _figura_vacia(titulo)
            continue

        df = _ordenar(df, clave)
        fig, ax = plt.subplots(figsize=(10, 6))
        if clave == "anios":
            ax.bar(df["valor"].astype(str), df["frecuencia"], color=COLOR_BARRAS)
            ax.set_xlabel("Año")
            ax.set_ylabel("Frecuencia")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", alpha=0.3)
        else:
            ax.barh(
                df["valor"].astype(str)[::-1],
                df["frecuencia"][::-1],
                color=COLOR_BARRAS,
            )
            ax.set_ylabel(ETIQUETA_EJE[clave])
            ax.set_xlabel("Frecuencia")
            ax.grid(axis="x", alpha=0.3)
        ax.set_title(titulo)
        fig.tight_layout()
        figuras[clave] = fig
    return figuras


def guardar_graficas(figuras: dict, directorio: str | Path) -> list[Path]:
    """Guarda cada figura como ``<clave>.png`` dentro de ``directorio``.

    Las figuras siguen abiertas después de guardarlas: quien las incruste
    en la GUI sigue siendo su dueño.
    """
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    rutas = []
    for clave, figura in figuras.items():
        ruta = directorio / f"{clave}.png"
        figura.savefig(ruta, dpi=150, bbox_inches="tight")
        rutas.append(ruta)
    return rutas

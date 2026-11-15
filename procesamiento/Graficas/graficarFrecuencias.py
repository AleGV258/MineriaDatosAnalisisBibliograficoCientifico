"""Gráficas de frecuencias por variable.

Recibe la salida de 'analizarFrecuencias.frecuencias', un dict con las
claves "autores", "titulos", "anios" y "editoriales", donde cada valor es
un DataFrame con columnas ["valor", "frecuencia"] (frecuencia absoluta).
Devuelve una figura matplotlib por variable, lista para incrustarse en la
GUI con 'FigureCanvasTkAgg', y permite guardarlas como PNG.
"""


from __future__ import annotations

import contextlib
from pathlib import Path
import matplotlib

matplotlib.use("Agg")  # dibuja en memoria, sin servidor gráfico

import matplotlib.pyplot as plt
import pandas as pd

# Máximo de barras cuando una variable tiene demasiados valores
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

    'anios' muestra todos los años en orden ascendente; el resto se
    ordena por frecuencia descendente y se recorta al top TOP_N.
    """
    df = df.copy()
    if clave == "anios":
        with contextlib.suppress(ValueError, TypeError):
            df["valor"] = df["valor"].astype(int)
        return df.sort_values("valor")
    return df.sort_values("frecuencia", ascending=False).head(TOP_N)


def generar_graficas(frecuencias: dict) -> dict:
    """Genera una figura matplotlib por cada variable.

    'anios' usa barras verticales; el resto usa barras horizontales
    porque los nombres (autores, títulos, editoriales) son largos y se
    leerían cortados en vertical. Una variable sin datos devuelve una
    figura con el texto "Sin datos". Regresa un dict {clave: figura}.
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
            fig.tight_layout()
        else:
            # Reversado para que el valor más frecuente quede arriba
            ax.barh(
                df["valor"].astype(str)[::-1],
                df["frecuencia"][::-1],
                color=COLOR_BARRAS,
            )
            ax.set_ylabel(ETIQUETA_EJE[clave])
            ax.set_xlabel("Frecuencia")
            ax.grid(axis="x", alpha=0.3)
            # Margen izquierdo amplio para que quepan los nombres largos
            fig.subplots_adjust(left=0.35, right=0.97, top=0.9, bottom=0.12)
        ax.set_title(titulo)
        figuras[clave] = fig
    return figuras


def guardar_graficas(figuras: dict, directorio: str | Path) -> list[Path]:
    """Guarda cada figura como '<clave>.png' dentro de 'directorio'.

    Regresa la lista de rutas generadas. Las figuras quedan abiertas
    después de guardarse; quien las incruste en la GUI sigue siendo
    su dueño.
    """
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    rutas = []
    for clave, figura in figuras.items():
        ruta = directorio / f"{clave}.png"
        figura.savefig(ruta, dpi=150, bbox_inches="tight")
        rutas.append(ruta)
    return rutas

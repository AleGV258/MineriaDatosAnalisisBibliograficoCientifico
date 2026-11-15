"""
 *  Integrantes:
 *      - Leonardo David Nava Bautista - 292655
 *      - Michell Alejandro García Vargas - 259663
 *  Materia: Programación Avanzada y Bases de Datos
 *  Proyecto: Minería de Datos aplicado al Análisis Bibliográfico de Textos Científicos.
"""

import customtkinter as ctk

from interfaz.pantallaPrincipal import VentanaPrincipal

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

aplicacion = VentanaPrincipal()
aplicacion.mainloop()

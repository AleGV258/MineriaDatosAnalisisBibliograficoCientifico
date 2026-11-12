import customtkinter as ctk

from interfaz.pantallaPrincipal import VentanaPrincipal


# Se configura la apariencia general de la aplicación
ctk.set_appearance_mode("System")

# Se configura el tema de colores
ctk.set_default_color_theme("blue")

# Se crea la ventana principal
aplicacion = VentanaPrincipal()

# Se inicia la aplicación
aplicacion.mainloop()

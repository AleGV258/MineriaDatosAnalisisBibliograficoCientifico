
import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox

from procesamiento.buscarArchivosPDF import buscarArchivosPDF
from procesamiento.convertirArchivosTXT import convertirArchivosTXT

class VentanaPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Se configura la ventana principal
        self.title("Minería de Textos")
        self.geometry("1100x700")

        # Se inicializan las variables
        self.ruta_directorio = ""
        self.archivos_pdf = []

        # Se crea la interfaz
        self.crear_interfaz()

    def crear_interfaz(self):

        # Se crea el título principal
        self.etiqueta_titulo = ctk.CTkLabel(
            self,
            text="Minería de Textos",
            font=("Arial", 24, "bold")
        )
        self.etiqueta_titulo.pack(pady=15)

        # Se crea el contenedor de selección de carpeta
        self.contenedor_seleccion = ctk.CTkFrame(self)
        self.contenedor_seleccion.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # Se crea el botón para seleccionar una carpeta
        self.boton_seleccionar = ctk.CTkButton(
            self.contenedor_seleccion,
            text="Seleccionar carpeta",
            command=self.seleccionar_directorio
        )

        self.boton_seleccionar.pack(
            side="left",
            padx=10,
            pady=10
        )

        # Se muestra la ruta seleccionada
        self.etiqueta_ruta = ctk.CTkLabel(
            self.contenedor_seleccion,
            text="Ninguna carpeta seleccionada",
            anchor="w"
        )
        self.etiqueta_ruta.pack(
            side="left",
            padx=10,
            fill="x",
            expand=True
        )

        # Se crea el contenedor principal de los paneles
        self.contenedor_principal = ctk.CTkFrame(self)
        self.contenedor_principal.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Se crea el panel izquierdo para los documentos
        self.panel_documentos = ctk.CTkFrame(
            self.contenedor_principal,
            width=300
        )
        self.panel_documentos.pack(
            side="left",
            fill="y",
            padx=(5, 10),
            pady=5
        )
        self.panel_documentos.pack_propagate(False)

        # Se crea el título del panel de documentos
        self.etiqueta_documentos = ctk.CTkLabel(
            self.panel_documentos,
            text="Documentos PDF",
            font=("Arial", 16, "bold")
        )
        self.etiqueta_documentos.pack(pady=10)

        # Se muestra la cantidad de documentos encontrados
        self.etiqueta_contador = ctk.CTkLabel(
            self.panel_documentos,
            text="Documentos encontrados: 0"
        )
        self.etiqueta_contador.pack(pady=5)

        # Se crea el botón para actualizar el listado
        self.boton_actualizar = ctk.CTkButton(
            self.panel_documentos,
            text="Actualizar listado",
            command=self.actualizar_listado
        )
        self.boton_actualizar.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # Se crea el contenedor de la tabla
        self.contenedor_tabla = ctk.CTkFrame(
            self.panel_documentos
        )
        self.contenedor_tabla.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Se crea la tabla de documentos con una sola columna
        self.tabla_documentos = ttk.Treeview(
            self.contenedor_tabla,
            columns=("nombre",),
            show="headings"
        )

        # Se configura el encabezado
        self.tabla_documentos.heading(
            "nombre",
            text="Nombre del fichero"
        )

        # Se configura el ancho de la columna
        self.tabla_documentos.column(
            "nombre",
            width=270,
            anchor="w",
            stretch=False
        )

        # Se crea la barra de desplazamiento
        self.barra_desplazamiento = ttk.Scrollbar(
            self.contenedor_tabla,
            orient="vertical",
            command=self.tabla_documentos.yview
        )

        # Se conecta la barra de desplazamiento con la tabla
        self.tabla_documentos.configure(
            yscrollcommand=self.barra_desplazamiento.set
        )

        # Se posicionan la tabla y la barra de desplazamiento
        self.tabla_documentos.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.barra_desplazamiento.pack(
            side="right",
            fill="y"
        )

        # Se crea el botón para convertir los documentos
        self.boton_convertir = ctk.CTkButton(
            self.panel_documentos,
            text="Convertir a TXT",
            command=self.iniciar_conversion,
            height=40
        )
        self.boton_convertir.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        # Se crea el panel derecho para las gráficas
        self.panel_graficas = ctk.CTkFrame(
            self.contenedor_principal
        )
        self.panel_graficas.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5),
            pady=5
        )

        # Se crea el título del panel de gráficas
        self.etiqueta_graficas = ctk.CTkLabel(
            self.panel_graficas,
            text="Análisis de frecuencias",
            font=("Arial", 18, "bold")
        )
        self.etiqueta_graficas.pack(pady=20)

        # Se muestra un mensaje inicial en el panel de gráficas
        self.etiqueta_mensaje = ctk.CTkLabel(
            self.panel_graficas,
            text="Análisis de frecuencias",
            text_color="gray"
        )
        self.etiqueta_mensaje.pack(pady=20)

    def seleccionar_directorio(self):
        # Se abre el explorador de carpetas
        ruta_seleccionada = filedialog.askdirectory()

        # Se comprueba que se haya seleccionado una carpeta
        if ruta_seleccionada:
            self.ruta_directorio = ruta_seleccionada
            self.etiqueta_ruta.configure(text=self.ruta_directorio)
            self.actualizar_listado()

    def actualizar_listado(self):
        # Se comprueba que exista una carpeta seleccionada
        if not self.ruta_directorio:
            return

        # Se buscan los documentos PDF
        self.archivos_pdf = buscarArchivosPDF(self.ruta_directorio)

        # Se eliminan los registros anteriores de la tabla
        for elemento in self.tabla_documentos.get_children():
            self.tabla_documentos.delete(elemento)

        # Se agregan los documentos encontrados a la tabla
        for archivo in self.archivos_pdf:
            self.tabla_documentos.insert(
                "",
                "end",
                values=(archivo["nombre"],)
            )

        # Se actualiza el contador de documentos
        self.etiqueta_contador.configure(
            text=f"Documentos encontrados: {len(self.archivos_pdf)}"
        )

    def iniciar_conversion(self):
        # Se comprueba que existan documentos para convertir
        if not self.archivos_pdf:
            messagebox.showwarning(
                "Sin documentos",
                "No hay archivos PDF para convertir"
            )
            return

        # Se inicia la conversión de los documentos
        archivos_convertidos = convertirArchivosTXT(self.archivos_pdf)

        # Se muestra el resultado de la conversión
        messagebox.showinfo(
            "Conversión finalizada",
            f"Se convirtieron {len(archivos_convertidos)} documentos correctamente"
        )

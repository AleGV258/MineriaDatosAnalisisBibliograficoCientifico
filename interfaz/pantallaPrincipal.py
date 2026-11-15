"""Ventana principal de la aplicación.

Interfaz con CustomTkinter: selección de la carpeta de protocolos,
listado de los PDF, conversión a TXT, análisis de frecuencias con
sus gráficas en pestañas y exportación a CSV/JSON/PNG.
"""

from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from procesamiento.ConvertirPDF.buscarArchivosPDF import buscar_archivos_PDF
from procesamiento.ConvertirPDF.convertirArchivosTXT import convertir_archivos_TXT
from procesamiento.ExcluirCitas.extraerReferencias import analizar_documento
from procesamiento.AnalisisFrecuencias.analizarFrecuencias import frecuencias
from procesamiento.Graficas.graficarFrecuencias import generar_graficas, guardar_graficas
from procesamiento.ExportarCSV.exportarCSV import exportar_frecuencias_CSV
from procesamiento.ExportarCSV.exportarJSON import exportar_citas_JSON, exportar_frecuencias_JSON

class VentanaPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Minería de Textos")
        self.geometry("1100x700")

        self.rutaDirectorio = ""
        self.archivosPDF = []
        self.resultadosReferencias = []
        self.tablaFrecuencias = {}

        self.crear_interfaz()

    def crear_interfaz(self):
        """Arma toda la ventana: título, selector de carpeta y paneles."""
        self.etiquetaTitulo = ctk.CTkLabel(
            self,
            text="Minería de Textos",
            font=("Arial", 24, "bold")
        )
        self.etiquetaTitulo.pack(pady=15)

        # Barra de arriba para elegir la carpeta de protocolos
        self.contenedorSeleccion = ctk.CTkFrame(self)
        self.contenedorSeleccion.pack(fill="x", padx=20, pady=10)

        self.botonSeleccionar = ctk.CTkButton(
            self.contenedorSeleccion,
            text="Seleccionar carpeta",
            command=self.seleccionar_directorio
        )
        self.botonSeleccionar.pack(side="left", padx=10, pady=10)

        self.etiquetaRuta = ctk.CTkLabel(
            self.contenedorSeleccion,
            text="Ninguna carpeta seleccionada",
            anchor="w"
        )
        self.etiquetaRuta.pack(side="left", padx=10, fill="x", expand=True)

        # Contenedor principal dividido en panel izquierdo y derecho
        self.contenedorPrincipal = ctk.CTkFrame(self)
        self.contenedorPrincipal.pack(fill="both", expand=True, padx=20, pady=10)

        self.panelDocumentos = ctk.CTkFrame(
            self.contenedorPrincipal,
            width=300
        )
        self.panelDocumentos.pack(side="left", fill="y", padx=(5, 10), pady=5)
        self.panelDocumentos.pack_propagate(False)

        self.etiquetaDocumentos = ctk.CTkLabel(
            self.panelDocumentos,
            text="Documentos PDF",
            font=("Arial", 16, "bold")
        )
        self.etiquetaDocumentos.pack(pady=10)

        self.etiquetaContador = ctk.CTkLabel(
            self.panelDocumentos,
            text="Documentos encontrados: 0"
        )
        self.etiquetaContador.pack(pady=5)

        self.botonActualizar = ctk.CTkButton(
            self.panelDocumentos,
            text="Actualizar listado",
            command=self.actualizar_listado
        )
        self.botonActualizar.pack(fill="x", padx=10, pady=5)

        # Tabla con el nombre de cada PDF encontrado
        self.contenedorTabla = ctk.CTkFrame(self.panelDocumentos)
        self.contenedorTabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.tablaDocumentos = ttk.Treeview(
            self.contenedorTabla,
            columns=("nombre",),
            show="headings"
        )
        self.tablaDocumentos.heading("nombre", text="Nombre del fichero")
        self.tablaDocumentos.column("nombre", width=270, anchor="w", stretch=False)

        self.barraDesplazamiento = ttk.Scrollbar(
            self.contenedorTabla,
            orient="vertical",
            command=self.tablaDocumentos.yview
        )
        self.tablaDocumentos.configure(yscrollcommand=self.barraDesplazamiento.set)

        self.tablaDocumentos.pack(side="left", fill="both", expand=True)
        self.barraDesplazamiento.pack(side="right", fill="y")

        # Botones del flujo: convertir, analizar y exportar
        self.botonConvertir = ctk.CTkButton(
            self.panelDocumentos,
            text="Convertir a TXT",
            command=self.iniciar_conversion,
            height=40
        )
        self.botonConvertir.pack(fill="x", padx=10, pady=(0, 10))

        self.botonAnalisis = ctk.CTkButton(
            self.panelDocumentos,
            text="Realizar análisis de frecuencias",
            command=self.iniciar_analisis,
            height=40
        )
        self.botonAnalisis.pack(fill="x", padx=10, pady=(0, 10))

        self.botonExportar = ctk.CTkButton(
            self.panelDocumentos,
            text="Exportar a CSV",
            command=self.iniciar_exportacion,
            height=40
        )
        self.botonExportar.pack(fill="x", padx=10, pady=(0, 10))

        # Panel derecho: aquí se dibujan las gráficas por variable
        self.panelGraficas = ctk.CTkFrame(self.contenedorPrincipal)
        self.panelGraficas.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

        self.etiquetaGraficas = ctk.CTkLabel(
            self.panelGraficas,
            text="Análisis de frecuencias",
            font=("Arial", 18, "bold")
        )
        self.etiquetaGraficas.pack(pady=20)

        self.etiquetaMensaje = ctk.CTkLabel(
            self.panelGraficas,
            text="Análisis de frecuencias",
            text_color="gray"
        )
        self.etiquetaMensaje.pack(pady=20)

    def seleccionar_directorio(self):
        """Abre el explorador de carpetas y carga el listado de PDFs."""
        rutaSeleccionada = filedialog.askdirectory()
        if rutaSeleccionada:
            self.rutaDirectorio = rutaSeleccionada
            self.etiquetaRuta.configure(text=self.rutaDirectorio)
            self.actualizar_listado()

    def actualizar_listado(self):
        """Vuelve a buscar los PDF de la carpeta y refresca la tabla."""
        if not self.rutaDirectorio:
            return
        self.archivosPDF = buscar_archivos_PDF(self.rutaDirectorio)

        for elemento in self.tablaDocumentos.get_children():
            self.tablaDocumentos.delete(elemento)

        for archivo in self.archivosPDF:
            self.tablaDocumentos.insert("", "end", values=(archivo["nombre"],))

        self.etiquetaContador.configure(
            text=f"Documentos encontrados: {len(self.archivosPDF)}"
        )

    def iniciar_conversion(self):
        """Convierte los PDF de la lista a TXT en 'datos/salida'."""
        if not self.archivosPDF:
            messagebox.showwarning(
                "Sin documentos",
                "No hay archivos PDF para convertir"
            )
            return

        archivosConvertidos = convertir_archivos_TXT(self.archivosPDF)

        messagebox.showinfo(
            "Conversión finalizada",
            f"Se convirtieron {len(archivosConvertidos)} documentos correctamente"
        )

    def iniciar_analisis(self):
        """Analiza los TXT de 'datos/salida' y genera frecuencias, gráficas y JSON."""
        carpetaSalida = Path(__file__).resolve().parents[1] / "datos" / "salida"
        archivosTXT = sorted(carpetaSalida.glob("*.txt"))

        if not archivosTXT:
            messagebox.showwarning(
                "Sin documentos",
                "No hay archivos TXT para analizar, primero convierte los PDF"
            )
            return

        self.resultadosReferencias = [
            analizar_documento(txt) for txt in archivosTXT
        ]
        self.tablaFrecuencias = frecuencias(self.resultadosReferencias)
        self.mostrar_graficas()
        exportar_citas_JSON(self.resultadosReferencias)
        exportar_frecuencias_JSON(self.tablaFrecuencias)

        totalValidas = sum(r["n_validas"] for r in self.resultadosReferencias)
        messagebox.showinfo(
            "Análisis finalizado",
            f"Se analizaron {len(archivosTXT)} documentos\n"
            f"Citas válidas: {totalValidas}"
        )

    def iniciar_exportacion(self):
        """Exporta el análisis a CSV y guarda las gráficas como PNG."""
        if not self.resultadosReferencias:
            messagebox.showwarning(
                "Sin análisis",
                "Primero realiza el análisis de frecuencias"
            )
            return

        rutaCSV = exportar_frecuencias_CSV(self.resultadosReferencias)

        carpetaGraficas = (
            Path(__file__).resolve().parents[1] / "datos" / "salida" / "graficas"
        )
        guardar_graficas(self.figurasFrecuencias, carpetaGraficas)

        messagebox.showinfo(
            "Exportación finalizada",
            f"Se guardó el CSV en:\n{rutaCSV}\n\n"
            f"Las gráficas en:\n{carpetaGraficas}"
        )

    def mostrar_graficas(self):
        """Dibuja las frecuencias en pestañas, una por variable."""
        # Se limpian los widgets anteriores del panel derecho
        for widget in self.panelGraficas.winfo_children():
            if widget != self.etiquetaGraficas:
                widget.destroy()

        self.figurasFrecuencias = generar_graficas(self.tablaFrecuencias)

        nombres = {
            "autores": "Autores",
            "titulos": "Títulos",
            "anios": "Años",
            "editoriales": "Editoriales",
        }
        self.pestanasFrecuencias = ctk.CTkTabview(self.panelGraficas)
        self.pestanasFrecuencias.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Cada figura de matplotlib se incrusta en su pestaña
        for clave, figura in self.figurasFrecuencias.items():
            pestana = self.pestanasFrecuencias.add(nombres.get(clave, clave))
            lienzo = FigureCanvasTkAgg(figura, pestana)
            lienzo.draw()
            lienzo.get_tk_widget().pack(fill="both", expand=True)

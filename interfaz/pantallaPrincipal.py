"""Ventana principal de la aplicación.

Interfaz con CustomTkinter: selección de la carpeta de protocolos,
listado de los PDF, conversión a TXT, análisis de frecuencias con
sus gráficas en pestañas y exportación a CSV/JSON/PNG.
"""

import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from procesamiento.ConvertirPDF.buscarArchivosPDF import buscar_archivos_PDF, carpeta_salida
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

        # Icono de la aplicacion
        icono = carpeta_salida().parent / "Icon.ico"
        if icono.exists():
            self.iconbitmap(str(icono))

        self.carpeta = ""
        self.pdfs = []
        self.resultados = []
        self.frecuencias = {}

        self.crear_interfaz()

    def crear_interfaz(self):
        """Arma toda la ventana: título, selector de carpeta y paneles."""
        self.titulo = ctk.CTkLabel(
            self,
            text="Minería de Textos",
            font=("Arial", 24, "bold")
        )
        self.titulo.pack(pady=15)

        # Barra de arriba para elegir la carpeta de protocolos
        self.frameSeleccion = ctk.CTkFrame(self)
        self.frameSeleccion.pack(fill="x", padx=20, pady=10)

        self.btnCarpeta = ctk.CTkButton(
            self.frameSeleccion,
            text="Seleccionar carpeta",
            command=self.seleccionar_directorio
        )
        self.btnCarpeta.pack(side="left", padx=10, pady=10)

        self.lblRuta = ctk.CTkLabel(
            self.frameSeleccion,
            text="Ninguna carpeta seleccionada",
            anchor="w"
        )
        self.lblRuta.pack(side="left", padx=10, fill="x", expand=True)

        # Contenedor principal dividido en panel izquierdo y derecho
        self.framePrincipal = ctk.CTkFrame(self)
        self.framePrincipal.pack(fill="both", expand=True, padx=20, pady=10)

        self.panelDocs = ctk.CTkFrame(
            self.framePrincipal,
            width=300
        )
        self.panelDocs.pack(side="left", fill="y", padx=(5, 10), pady=5)
        self.panelDocs.pack_propagate(False)

        self.lblDocs = ctk.CTkLabel(
            self.panelDocs,
            text="Documentos PDF",
            font=("Arial", 16, "bold")
        )
        self.lblDocs.pack(pady=10)

        self.lblContador = ctk.CTkLabel(
            self.panelDocs,
            text="Documentos encontrados: 0"
        )
        self.lblContador.pack(pady=5)

        self.botonActualizar = ctk.CTkButton(
            self.panelDocs,
            text="Actualizar listado",
            command=self.actualizar_listado
        )
        self.botonActualizar.pack(fill="x", padx=10, pady=5)

        # Tabla con el nombre de cada PDF encontrado
        self.frameTabla = ctk.CTkFrame(self.panelDocs)
        self.frameTabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabla = ttk.Treeview(
            self.frameTabla,
            columns=("nombre",),
            show="headings"
        )
        self.tabla.heading("nombre", text="Nombre del fichero")
        self.tabla.column("nombre", width=270, anchor="w", stretch=False)

        self.scrollTabla = ttk.Scrollbar(
            self.frameTabla,
            orient="vertical",
            command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=self.scrollTabla.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        self.scrollTabla.pack(side="right", fill="y")

        # Botones del flujo: convertir, analizar y exportar
        self.btnConvertir = ctk.CTkButton(
            self.panelDocs,
            text="Convertir a TXT",
            command=self.iniciar_conversion,
            height=40
        )
        self.btnConvertir.pack(fill="x", padx=10, pady=(0, 10))

        self.btnAnalisis = ctk.CTkButton(
            self.panelDocs,
            text="Realizar análisis de frecuencias",
            command=self.iniciar_analisis,
            height=40
        )
        self.btnAnalisis.pack(fill="x", padx=10, pady=(0, 10))

        self.btnExportar = ctk.CTkButton(
            self.panelDocs,
            text="Exportar a CSV y gráficas",
            command=self.iniciar_exportacion,
            height=40
        )
        self.btnExportar.pack(fill="x", padx=10, pady=(0, 10))

        # Panel derecho: aquí se dibujan las gráficas por variable
        self.panelGraficas = ctk.CTkFrame(self.framePrincipal)
        self.panelGraficas.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

        self.lblGraficas = ctk.CTkLabel(
            self.panelGraficas,
            text="Análisis de frecuencias",
            font=("Arial", 18, "bold")
        )
        self.lblGraficas.pack(pady=20)

        # Línea de estado: informa el resultado de cada acción del flujo
        self.lblMensaje = ctk.CTkLabel(
            self.panelGraficas,
            text="Selecciona una carpeta de protocolos para empezar",
            text_color="gray"
        )
        self.lblMensaje.pack(pady=20)

    def seleccionar_directorio(self):
        """Abre el explorador de carpetas y carga el listado de PDFs."""
        rutaSeleccionada = filedialog.askdirectory()
        if rutaSeleccionada:
            self.carpeta = rutaSeleccionada
            self.lblRuta.configure(text=self.carpeta)
            self.actualizar_listado()

    def actualizar_listado(self):
        """Vuelve a buscar los PDF de la carpeta y refresca la tabla."""
        if not self.carpeta:
            return
        self.pdfs = buscar_archivos_PDF(self.carpeta)

        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        for archivo in self.pdfs:
            self.tabla.insert("", "end", values=(archivo["nombre"],))

        self.lblContador.configure(
            text=f"Documentos encontrados: {len(self.pdfs)}"
        )

    def iniciar_conversion(self):
        """Convierte los PDF de la lista a TXT en 'datos/salida'."""
        if not self.pdfs:
            messagebox.showwarning(
                "Sin documentos",
                "No hay archivos PDF para convertir"
            )
            return

        archivosConvertidos = convertir_archivos_TXT(self.pdfs)
        self.lblMensaje.configure(
            text=f"{len(archivosConvertidos)} documentos convertidos a TXT"
        )

        messagebox.showinfo(
            "Conversión finalizada",
            f"Se convirtieron {len(archivosConvertidos)} documentos correctamente"
        )

    def iniciar_analisis(self):
        """Analiza los TXT de 'datos/salida' y genera frecuencias, gráficas y JSON."""
        carpetaSalida = carpeta_salida()
        archivosTXT = sorted(carpetaSalida.glob("*.txt"))

        if not archivosTXT:
            messagebox.showwarning(
                "Sin documentos",
                "No hay archivos TXT para analizar, primero convierte los PDF"
            )
            return

        self.lblMensaje.configure(text=f"Analizando {len(archivosTXT)} documentos...")
        self.update_idletasks()

        # Los TXT vacíos provienen de PDF sin capa de texto (escaneados):
        # se detectan y quedan fuera del análisis para reportarse al usuario
        sinTexto = [
            txt.name for txt in archivosTXT
            if not txt.read_text(encoding="utf-8", errors="ignore").strip()
        ]

        self.resultados = [
            analizar_documento(txt) for txt in archivosTXT
            if txt.name not in sinTexto
        ]

        if not self.resultados:
            self.lblMensaje.configure(text="Ningún documento tiene texto extraíble")
            messagebox.showwarning(
                "Sin texto",
                "Ningún TXT tiene texto extraíble (todos los PDF parecen escaneados)"
            )
            return

        self.frecuencias = frecuencias(self.resultados)
        self.mostrar_graficas()
        exportar_citas_JSON(self.resultados)
        exportar_frecuencias_JSON(self.frecuencias)

        totalValidas = sum(r["n_validas"] for r in self.resultados)
        estado = (
            f"Listo: {totalValidas} citas válidas en {len(self.resultados)} documentos"
        )
        if sinTexto:
            estado += f" · {len(sinTexto)} sin texto ({', '.join(sinTexto)})"
        self.lblMensaje.configure(text=estado)

        resumen = (
            f"Se analizaron {len(self.resultados)} documentos\n"
            f"Citas válidas: {totalValidas}"
        )
        if sinTexto:
            resumen += (
                "\n\nSin texto extraíble (probablemente escaneados):\n"
                + ", ".join(sinTexto)
            )
        messagebox.showinfo("Análisis finalizado", resumen)

    def iniciar_exportacion(self):
        """Exporta el análisis a CSV y guarda las gráficas como PNG."""
        if not self.resultados:
            messagebox.showwarning(
                "Sin análisis",
                "Primero realiza el análisis de frecuencias"
            )
            return

        rutaCSV = exportar_frecuencias_CSV(self.resultados)

        carpetaGraficas = carpeta_salida() / "graficas"
        guardar_graficas(self.figurasFrecuencias, carpetaGraficas)

        self.lblMensaje.configure(text="CSV y gráficas guardados en datos/salida")

        messagebox.showinfo(
            "Exportación finalizada",
            f"Se guardó el CSV en:\n{rutaCSV}\n\n"
            f"Las gráficas en:\n{carpetaGraficas}"
        )

    def mostrar_graficas(self):
        """Dibuja las frecuencias en pestañas, una por variable."""
        # Se limpian los widgets anteriores del panel derecho (la línea de
        # estado se conserva) y se liberan las figuras del análisis previo
        for widget in self.panelGraficas.winfo_children():
            if widget not in (self.lblGraficas, self.lblMensaje):
                widget.destroy()

        if getattr(self, "figurasFrecuencias", None):
            for figura in self.figurasFrecuencias.values():
                figura.clear()
                plt.close(figura)

        self.figurasFrecuencias = generar_graficas(self.frecuencias)

        nombres = {
            "autores": "Autores",
            "titulos": "Títulos",
            "anios": "Años",
            "editoriales": "Editoriales",
        }
        self.tabs = ctk.CTkTabview(self.panelGraficas)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Cada figura de matplotlib se incrusta en su pestaña
        for clave, figura in self.figurasFrecuencias.items():
            pestana = self.tabs.add(nombres.get(clave, clave))
            lienzo = FigureCanvasTkAgg(figura, pestana)
            lienzo.draw()
            lienzo.get_tk_widget().pack(fill="both", expand=True)

from sys import exit as sys_exit
from shutil import copyfile
from threading import Thread
import customtkinter
from tkinter import StringVar, ttk, filedialog, messagebox

from numpy import arange, polyfit, poly1d, linspace
from CTkListbox import *
from PIL import Image
from customtkinter import CTkImage
from matplotlib import pyplot as plt, ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from webbrowser import open as open_web

import SH_Stats_back.gestor as gestor
import SH_Stats_back.funciones_auxiliares as funciones_aux

PANEL_PATH = "res\\panel.db"
ICON_PATH = "res\\logo_shs_sf_dark.ico"
LIGHT_IMAGE_PATH = "res\\logo_shs_sf_light.png"
DARK_IMAGE_PATH = "res\\logo_shs_sf_dark.png"
VERSION = "1.2.0"
URL_WEB = "https://guillermofranco.notion.site/8b35019a2d8749188b925809f87e5236?v=ff4a0ea1a5ae4f3e85882a8468668bcb"
class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.title("Spanish Handball Stats")
        self.geometry(f"{1100}x{580}")
        # ´maximize
        self.state("zoomed")
        customtkinter.set_appearance_mode("Dark")
        self.iconbitmap(funciones_aux.resource_path(ICON_PATH))

        # Variables
        self.panel = None
        self.current_competicion = None

        # Layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Barra lateral
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")


        light_image_path = funciones_aux.resource_path(LIGHT_IMAGE_PATH)
        dark_image_path = funciones_aux.resource_path(DARK_IMAGE_PATH)
        self.logo_image = CTkImage(light_image=Image.open(light_image_path).resize((150, 150)),
                                   dark_image=Image.open(dark_image_path).resize((150, 150)),
                                   size=(150, 150))
        self.logo_image_label = customtkinter.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        self.logo_image_label.grid(row=0, column=0, padx=5, pady=10)





        self.btn_actualizar_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Actualizar Panel", command=lambda : self.ventana_actualizar_panel())
        self.btn_actualizar_panel.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_frame.rowconfigure(2, weight=5)


        self.btn_abrir_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Abrir Panel", command=self.abrir_panel)
        self.btn_abrir_panel.grid(row=3, column=0, padx=20, pady=10)
        self.btn_guardar_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Guardar Panel", command=self.guardar_panel)
        self.btn_guardar_panel.grid(row=4, column=0, padx=20, pady=10)
        self.btn_borrar_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Borrar Panel", command=self.borrar_panel)
        self.btn_borrar_panel.grid(row=5, column=0, padx=20, pady=10)
        self.btn_annadir_al_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Añadir al Panel", command=self.annadir_al_panel)
        # self.btn_annadir_al_panel.grid(row=6, column=0, padx=20, pady=10)
        self.sidebar_frame.rowconfigure(7, weight=5)
        self.btn_exportar_partidos = customtkinter.CTkButton(self.sidebar_frame, text="Exportar Partidos",
                                                             command=self.exportar_partidos, state="normal")
        self.btn_exportar_partidos.grid(row=8, column=0, padx=20, pady=10, sticky="s")
        self.btn_exportar_competiciones = customtkinter.CTkButton(self.sidebar_frame,
                                                                  text="Exportar Competiciones",
                                                                  command=self.exportar_competiciones, state="normal")
        self.btn_exportar_competiciones.grid(row=9, column=0, padx=20, pady=10, sticky="s")
        self.sidebar_frame.rowconfigure(10, weight=5)

        self.btn_ajustes = customtkinter.CTkButton(self.sidebar_frame, text ="Ajustes", command= lambda : self.show_message("Función no implementada"))
        #self.btn_ajustes.grid(row=11, column=0, padx=20, pady=10, sticky="s")
        self.btn_salir = customtkinter.CTkButton(self.sidebar_frame, text ="Salir", command= lambda : self.cerrar_app())
        self.btn_salir.grid(row=12, column=0, padx=20, pady=10, sticky="s")
        #Text with version app
        self.version_text = customtkinter.CTkLabel(self.sidebar_frame, text=f"Versión {VERSION}", font=customtkinter.CTkFont(size=10))
        self.version_text.grid(row=13, column=0, padx=20, pady=10, sticky="s")

        # Competiciones
        self.competiciones_frame = customtkinter.CTkFrame(self, width=300, corner_radius=10)
        self.competiciones_frame.grid(row=0, column=1, rowspan= 2, sticky="nsw", padx=10, pady=(10,0))
        self.competiciones_frame.grid_propagate(True)
        self.competiciones_frame.grid_columnconfigure(0, weight=1)
        self.competiciones_frame.grid_columnconfigure(1, weight=1)

        self.competiciones_label = customtkinter.CTkLabel(self.competiciones_frame, text="Competiciones",
                                                          font=customtkinter.CTkFont(size=20, weight="bold"), anchor="center")
        self.competiciones_label.grid(row=0, column=0, columnspan = 2,  padx=20, pady=(20, 10))

        self.competiciones_lista = CTkListbox(self.competiciones_frame, height=300, border_width=0)
        self.competiciones_lista.grid(row=1, column=0, padx=10, pady=10, columnspan = 2, rowspan = 2, sticky="nsew")

        self.btn_annadir_competicion = customtkinter.CTkButton(self.competiciones_frame, text="Añadir Competición",
                                                               command=self.annadir_competicion)
        self.btn_annadir_competicion.grid(row=3, column=0, padx=10, pady=10, sticky="ne")
        self.btn_borrar_competicion = customtkinter.CTkButton(self.competiciones_frame, text="Borrar Competición",
                                                              command=self.borrar_competicion)
        self.btn_borrar_competicion.grid(row=3, column=1, padx=10, pady=10, sticky="nw")

        # Enlaces
        self.enlaces_frame = customtkinter.CTkFrame(self, corner_radius=10, width=300)
        self.enlaces_frame.grid(row=2, column=1, rowspan = 2, sticky="nsew", padx=10, pady=10)

        label = customtkinter.CTkLabel(self.enlaces_frame, text="Enlaces",
                                                            font=customtkinter.CTkFont(size=20, weight="bold"), anchor="center")
        label.grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 10))

        self.enlaces_label_ultima_actualizacion = customtkinter.CTkLabel(self.enlaces_frame,
                                                                         text="Última actualización:\n",
                                                                         font=customtkinter.CTkFont(size=14,
                                                                                                    weight="bold"))
        self.enlaces_label_ultima_actualizacion.grid(row=5, column=0, columnspan = 2, padx=(10, 0), pady=10, sticky="n")
        self.enlaces_lista = CTkListbox(self.enlaces_frame, border_width=0,
                                        command=self.on_enlaces_lista_selected, justify="right")
        self.enlaces_lista.grid(row=6, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")
        self.btn_enlaces_annadir = customtkinter.CTkButton(self.enlaces_frame, text="Añadir Enlace",
                                                           command=self.annadir_enlace, state="disabled")
        self.btn_enlaces_annadir.grid(row=7, column=0, padx=(10, 0), pady=0, sticky="s")
        self.btn_enlaces_actualizar = customtkinter.CTkButton(self.enlaces_frame, text="Actualizar Enlaces",
                                                              command=self.actualizar_competicion, state="disabled")
        self.btn_enlaces_actualizar.grid(row=7, column=1, padx=(10, 0), pady=0, sticky="s")


        # Competicion
        self.competicion_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.competicion_frame.grid(row=0, column=2, rowspan= 4, sticky="nsew", padx=(0,10), pady=10)
        self.competicion_frame.grid_propagate(True)
        self.competicion_label = customtkinter.CTkLabel(self.competicion_frame, text="Competición #",
                                                        font=customtkinter.CTkFont(size=20, weight="bold"), anchor="center")
        self.competicion_label.pack(padx=10, pady=(20, 0))
        self.tabview_competicion = customtkinter.CTkTabview(self.competicion_frame, state="disabled")
        self.tabview_competicion.pack(expand=True, fill="both", padx=10, pady=10)
        self.tabview_competicion.add("General")
        self.tabview_competicion.add("Equipos")
        self.tabview_competicion.add("Partidos")

        # Competicion/General
        self.general_segmented_button_var = StringVar(value="Visualizando")
        self.general_tabview = customtkinter.CTkTabview(self.tabview_competicion.tab("General"))
        self.general_tabview.pack(expand=True, fill="both", padx=0, pady=(0,10))
        self.general_tabview.add("Estadísticas")
        self.general_tabview.add("Clasificación")
        self.general_tabview.add("Gráficos")

        # Competicion/General/Estadísticas
        self.estadisticas_frame = customtkinter.CTkFrame(self.general_tabview.tab("Estadísticas"), corner_radius=10)
        self.estadisticas_frame.pack(expand=True, fill="both")
        self.estadisticas_frame.grid_propagate(True)
        # self.estadisticas_text = customtkinter.CTkTextbox(self.estadisticas_frame, border_width=0)
        # self.estadisticas_text.insert("end", "Visualización de Estadísticas")
        # self.estadisticas_text.configure(state="disabled")
        # self.estadisticas_text.pack(expand=True, fill="both", padx=10, pady=10)



        # Competicion/General/Clasificación
        self.clasificacion_frame = customtkinter.CTkFrame(self.general_tabview.tab("Clasificación"), corner_radius=10)
        self.clasificacion_frame.pack(expand=True, fill="both")
        self.clasificacion_frame.grid_propagate(True)
        # Configure columns
        self.clasificacion_frame.columnconfigure(0, weight=1)
        self.clasificacion_frame.columnconfigure(1, weight=0)
        # Confugure rows
        self.clasificacion_frame.rowconfigure(0, weight=1)
        self.clasificacion_frame.rowconfigure(1, weight=0)

        # Add treeview
        tamanno = len(self.panel.get_competicion(self.competicion_label.cget("text")).get_equipos()) if self.panel is not None else 2
        self.clasificacion_treeview = ttk.Treeview(self.clasificacion_frame)
        self.clasificacion_treeview.grid(row=0, column=0, padx=(10,0), pady=10, sticky="nsew")
        # Add scrollbar
        self.clasificacion_treeview_scrollbar = customtkinter.CTkScrollbar(self.clasificacion_frame, command=self.clasificacion_treeview.yview, hover=True)
        self.clasificacion_treeview_scrollbar.grid(row=0, column=1, padx=(2,10), pady=10, sticky="ns")
        self.clasificacion_treeview.configure(yscrollcommand=self.clasificacion_treeview_scrollbar.set)


        # Configure Style
        style = ttk.Style()

        style.theme_use("default")

        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        borderwidth=0,
                         font = (None, 18))
        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font = (None, 20)

                        )
        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Configurar Classificación Treeview
        self.clasificacion_treeview["columns"] = ('Puesto', 'nombre', 'temporada', 'gf', 'gc', 'victorias', 'derrotas', 'empates')
        self.clasificacion_treeview.column("#0", width=0, stretch="no")
        self.clasificacion_treeview.column("Puesto", width=15, anchor="center")
        self.clasificacion_treeview.column("nombre", anchor="center", width=250)
        self.clasificacion_treeview.column("temporada", anchor="center", width=50)
        self.clasificacion_treeview.column("gf", anchor="center", width=15)
        self.clasificacion_treeview.column("gc", anchor="center", width=15)
        self.clasificacion_treeview.column("victorias", anchor="center", width=15)
        self.clasificacion_treeview.column("derrotas", anchor="center", width=15)
        self.clasificacion_treeview.column("empates", anchor="center", width=15)
        self.clasificacion_treeview.heading("Puesto", text="Puesto", anchor="center")
        self.clasificacion_treeview.heading("nombre", text="Equipo", anchor="center")
        self.clasificacion_treeview.heading("temporada", text="Temp", anchor="center")
        self.clasificacion_treeview.heading("gf", text="GF", anchor="center")
        self.clasificacion_treeview.heading("gc", text="GC", anchor="center")
        self.clasificacion_treeview.heading("victorias", text="V", anchor="center")
        self.clasificacion_treeview.heading("derrotas", text="D", anchor="center")
        self.clasificacion_treeview.heading("empates", text="E", anchor="center")

        # Competicion/General/Gráficos
        self.graficos_frame = customtkinter.CTkScrollableFrame(self.general_tabview.tab("Gráficos"), corner_radius=10)
        self.graficos_frame.pack(expand=True, fill="both")
        self.graficos_text = customtkinter.CTkTextbox(self.graficos_frame, border_width=0)
        self.graficos_text.insert("end", "Visualización de Gráficos")
        self.graficos_text.configure(state="disabled")
        self.graficos_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Competicion/Equipos
        self.equipos_frame = customtkinter.CTkFrame(self.tabview_competicion.tab("Equipos"), corner_radius=10)
        self.equipos_frame.pack(expand=True, fill="both")
        self.equipos_frame.grid_propagate(True)
        self.equipos_buscador_combobox = customtkinter.CTkComboBox(self.equipos_frame, border_width=0, command=self.seleccionar_equipos)
        self.equipos_buscador_combobox.pack(fill="both", padx=10, pady=10)

        self.equipos_tabview = customtkinter.CTkTabview(self.equipos_frame)
        self.equipos_tabview.pack(expand=True, fill="both", padx=10, pady=(0,10))
        self.equipos_tabview.add("Estadísticas")
        self.equipos_tabview.add("Gráficos")
        self.equipos_tabview.add("Partidos")




        # Competicion/Equipos/Estadísticas
        self.equipos_estadisticas_frame = customtkinter.CTkScrollableFrame(self.equipos_tabview.tab("Estadísticas"), corner_radius=10)
        self.equipos_estadisticas_frame.pack(expand=True, fill="both")
        self.equipos_estadisticas_text = customtkinter.CTkTextbox(self.equipos_estadisticas_frame, border_width=0)
        self.equipos_estadisticas_text.insert("end", "Visualización de Estadísticas")
        self.equipos_estadisticas_text.configure(state="disabled")
        self.equipos_estadisticas_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Competicion/Equipos/Gráficos
        self.equipos_graficos_frame = customtkinter.CTkScrollableFrame(self.equipos_tabview.tab("Gráficos"), corner_radius=10)
        self.equipos_graficos_frame.pack(expand=True, fill="both")
        # self.equipos_graficos_frame.grid_propagate(True)
        self.equipos_graficos_text = customtkinter.CTkTextbox(self.equipos_graficos_frame, border_width=0)
        self.equipos_graficos_text.insert("end", "Visualización de Gráficos")
        self.equipos_graficos_text.configure(state="disabled")
        self.equipos_graficos_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Competicion/Equipos/Partidos
        self.equipos_partidos_frame = customtkinter.CTkFrame(self.equipos_tabview.tab("Partidos"), corner_radius=10)
        self.equipos_partidos_frame.pack(expand=True, fill="both")
        self.equipos_partidos_frame.grid_propagate(True)
        self.equipos_partidos_frame.columnconfigure(0, weight=1)
        self.equipos_partidos_frame.columnconfigure(1, weight=1)
        # self.equipos_partidos_frame.grid_propagate(True)
        # Ordenar por label
        self.equipos_partidos_label_ordenar_por = customtkinter.CTkLabel(self.equipos_partidos_frame, text="Ordenar por:", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.equipos_partidos_label_ordenar_por.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # Combo box equipos_partidos
        self.equipos_partidos_combobox = customtkinter.CTkComboBox(self.equipos_partidos_frame, border_width=0, command=self.ordenar_partidos_equipo, values=["Más goles por partido","Menos goles por partido","Mejor resultado", "Peor resultado", "Más goles a favor", "Menos goles a favor", "Más goles en contra", "Menos goles en contra"], state="readonly")
        self.equipos_partidos_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Create treeview
        self.equipos_partidos_treeview = ttk.Treeview(self.equipos_partidos_frame, columns = ('local', 'gl', 'gv', 'visitante'), show='headings', height=30)
        self.equipos_partidos_treeview.grid(row=1, column=0, padx=(10,0), pady=10, columnspan=2, sticky="nsew")
        # Configure columns
        self.equipos_partidos_treeview.column("#0", width=0, stretch="no")
        self.equipos_partidos_treeview.column("local", anchor="center", width=250)
        self.equipos_partidos_treeview.column("gl", anchor="center", width=25)
        self.equipos_partidos_treeview.column("gv", anchor="center", width=25)
        self.equipos_partidos_treeview.column("visitante", anchor="center", width=250)
        self.equipos_partidos_treeview.heading("local", text="Local", anchor="center")
        self.equipos_partidos_treeview.heading("gl", text="GL", anchor="center")
        self.equipos_partidos_treeview.heading("gv", text="GV", anchor="center")
        self.equipos_partidos_treeview.heading("visitante", text="Visitante", anchor="center")

        # Add scrollbar
        self.equipos_partidos_treeview_scrollbar = customtkinter.CTkScrollbar(self.equipos_partidos_frame, command=self.equipos_partidos_treeview.yview, hover=True)
        self.equipos_partidos_treeview_scrollbar.grid(row=1, column=2, padx=(2,10), pady=10, sticky="ns")
        self.equipos_partidos_treeview.configure(yscrollcommand=self.equipos_partidos_treeview_scrollbar.set)





        # Competicion/Partidos
        self.partidos_frame = customtkinter.CTkFrame(self.tabview_competicion.tab("Partidos"), corner_radius=10)
        self.partidos_frame.pack(expand=True, fill="both")
        self.partidos_frame.columnconfigure(0, weight=1)
        self.partidos_frame.columnconfigure(1, weight=1)
        #Label Ordenar por:
        self.partidos_label_ordenar_por = customtkinter.CTkLabel(self.partidos_frame, text="Ordenar por:", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.partidos_label_ordenar_por.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Configure rows
        # self.partidos_frame.rowconfigure(0, weight=1)
        self.partidos_frame.rowconfigure(1, weight=1)
        # self.partidos_frame.rowconfigure(2, weight=0)



        # Create combo box
        self.partidos_buscador_combobox = customtkinter.CTkComboBox(self.partidos_frame, border_width=0, command=self.ordenar_partidos)
        self.partidos_buscador_combobox.grid(row=0, column=1, padx=10, pady=10, sticky = "ew")
        # Add values to combobox

        valores = ["Mayor diferencia", "Menor diferencia", "Más goles por partido", "Menos goles por partido", "Más goles ganadores", "Menos goles ganadores", "Más goles perdedores", "Menos goles perdedores"]


        self.partidos_buscador_combobox.configure(values=valores
                                                     , state="readonly")
        self.partidos_buscador_combobox.set("")
        # Create treeview
        self.partidos_treeview = ttk.Treeview(self.partidos_frame, columns = ('local', 'gl', 'gv', 'visitante'), show='headings', height=10)
        self.partidos_treeview.grid(row=1, column=0, padx=(10,0), pady=10, columnspan=2, sticky="nsew")
        # Configure columns
        self.partidos_treeview.column("#0", width=0, stretch="no")
        self.partidos_treeview.column("local", anchor="center", width=250)
        self.partidos_treeview.column("gl", anchor="center", width=25)
        self.partidos_treeview.column("gv", anchor="center", width=25)
        self.partidos_treeview.column("visitante", anchor="center", width=250)
        self.partidos_treeview.heading("local", text="Local", anchor="center")
        self.partidos_treeview.heading("gl", text="GL", anchor="center")
        self.partidos_treeview.heading("gv", text="GV", anchor="center")
        self.partidos_treeview.heading("visitante", text="Visitante", anchor="center")

        # Add scrollbar
        self.partidos_treeview_scrollbar = customtkinter.CTkScrollbar(self.partidos_frame, command=self.partidos_treeview.yview, hover=True)
        self.partidos_treeview_scrollbar.grid(row=1, column=2, padx=(2,10), pady=10, sticky="ns")
        self.partidos_treeview.configure(yscrollcommand=self.partidos_treeview_scrollbar.set)


        # Otras configuraciones
        self.cargar_estado()
        self.after(0, lambda: self.state('zoomed'))  # Bug en zoomed state, hay que hacerlo así




        # Bindings
        self.competiciones_lista.bind("<<ListboxSelect>>", self.on_competiciones_lista_selected)
        self.equipos_buscador_combobox.bind("<KeyRelease>", self.actualizar_filtro)
        self.clasificacion_treeview.bind("<Double-Button-1>", self.on_clasificacion_treeview_double_click)
        self.competicion_label.bind("<Button-1>", self.modificar_nombre_competicion)
        self.competicion_label.bind("<Enter>", self.entra_cursor)
        self.competicion_label.bind("<Leave>", self.sale_cursor)
        self.logo_image_label.bind("<Button-1>", self.abrir_web)
        self.logo_image_label.bind("<Enter>", self.entra_cursor)
        self.logo_image_label.bind("<Leave>", self.sale_cursor)


    def entra_cursor(self, event):
        """
        Función que cambia el cursor cuando se pasa por encima de un widget
        :param event:
        :return:
        """

        try:
            if event.widget.cget("text") != "Competición #":
                event.widget.config(cursor="hand2")
        except:
            event.widget.config(cursor="hand2")

    def sale_cursor(self, event):
        """
        Función que cambia el cursor cuando se sale de un widget
        :param event:
        :return:
        """
        event.widget.config(cursor="")

    def abrir_web(self, event):
        """
        Función que abre la web de SHStats
        :param event:
        :return:
        """
        open_web(URL_WEB)

    def cerrar_app(self):
        """
        Función que cierra la app.
        :return:
        """
        print("Cerrando app...")
        self.destroy()
        sys_exit()

    def actualizar_filtro(self, event):
        """
        Función que actualiza el filtro de equipos. Se usa para el buscador de equipos.
        :param event:
        :return:
        """
        filtro = self.equipos_buscador_combobox.get().lower()
        equipos = self.panel.get_competicion(self.competicion_label.cget("text")).get_equipos()
        nombres_equipos = []
        for equipo in equipos:
            if filtro in equipo.nombre.lower():
                nombres_equipos.append(equipo.nombre)
        self.equipos_buscador_combobox.configure(values=nombres_equipos)
        self.equipos_buscador_combobox.set(filtro)

    def on_clasificacion_treeview_double_click(self, event):
        """
        Función que se ejecuta cuando se hace doble click en un equipo de la clasificación.
        :param event:
        :return:
        """
        #open tabview equipos
        self.tabview_competicion.set("Equipos")
        #select equipo
        item = self.clasificacion_treeview.selection()[0]
        nombre_equipo = self.clasificacion_treeview.item(item, "values")[1]
        self.equipos_buscador_combobox.set(nombre_equipo)
        self.seleccionar_equipos(nombre_equipo)




    def on_competiciones_lista_selected(self, event):
        """
        Función que se ejecuta cuando se selecciona una competición de la lista de competiciones.
        :param event:
        :return:
        """
        if event is not None and event != self.competicion_label.cget("text"):
            if self.competiciones_lista.curselection() == ():
                return
            competicion = self.competiciones_lista.get(self.competiciones_lista.curselection())
            self.abrir_competicion(competicion)
            if self.enlaces_lista.curselection() is not None: # If there is a selected item
                self.enlaces_lista.deactivate(self.enlaces_lista.curselection())
    def on_enlaces_lista_selected(self, event):
        """
        Función que se ejecuta cuando se selecciona un enlace de la lista de enlaces.
        :param event:
        :return:
        """

        if event is not None:
            self.modificar_enlace()



    def actualizar_competicion(self):
        """
        Función que actualiza la competición seleccionada.
        :return:
        """


        hilo_actualizar = Thread(target=self.actualizar_competicion_thread)
        hilo_actualizar.start()
        self.loading_screen()
        self.loading_window.update()




    def actualizar_competicion_thread(self):
        """
        Función que se ejecuta en un hilo para actualizar la competición seleccionada.
        :return:
        """
        self.panel.actualizar_competicion(self.competicion_label.cget("text"))
        self.enlaces_label_ultima_actualizacion.configure(
            text=f"Última actualización:\n{self.panel.get_competicion(self.competicion_label.cget('text')).ultima_actualizacion}")
        self.abrir_competicion(self.competicion_label.cget("text"))
        self.loading_window.destroy()

    def ventana_actualizar_panel(self):
        """
        Función que muestra una ventana de confirmación para actualizar el panel.
        :return:
        """
        #Show pop up window for confirmation
        if self.panel is None:
            return
        confirmation_window = customtkinter.CTkToplevel(self)
        confirmation_window.title("Confirmación")
        confirmation_window.geometry("300x150")
        confirmation_window.resizable(False, False)
        confirmation_window.attributes("-topmost", True)
        confirmation_window.grab_set()
        confirmation_window.focus_set()
        confirmation_window.transient(self)
        # Create label
        label = customtkinter.CTkLabel(confirmation_window, text="La actualización puede tardar unos minutos\n¿Estás seguro?")
        label.pack(padx=20, pady=20)
        # Create buttons
        buttons_frame = customtkinter.CTkFrame(confirmation_window)
        buttons_frame.pack(padx=20, pady=20)
        btn_si = customtkinter.CTkButton(buttons_frame, text="Sí", command=lambda : self.actualizar_panel(confirmation_window), width=100)
        btn_si.pack(padx=10, side="left")
        btn_no = customtkinter.CTkButton(buttons_frame, text="No", command=lambda : confirmation_window.destroy(), width=100)
        btn_no.pack(padx=10, side="right")

    def actualizar_panel(self, confirmation_window):
        """
        Función que actualiza el panel.
        :param confirmation_window:
        :return:
        """
        confirmation_window.destroy()
        hilo_actualizar = Thread(target=self.actualizar_panel_thread)
        hilo_actualizar.start()
        self.loading_screen()
        self.loading_window.update()

    def actualizar_panel_thread(self):
        """
        Función que se ejecuta en un hilo para actualizar el panel.
        :return:
        """
        self.panel.actualizar_competiciones()
        self.loading_window.destroy()
        self.abrir_competicion(None)

    def loading_screen(self):
        """
        Función que muestra una ventana de carga con una barra de progreso indeterminada.
        :return:
        """
        # Create tokLevelWindow
        self.loading_window = customtkinter.CTkToplevel(self)
        self.loading_window.title("Cargando")
        # icon
        self.loading_window.iconbitmap(funciones_aux.resource_path(ICON_PATH))


        progressbar = customtkinter.CTkProgressBar(self.loading_window, orientation="horizontal")
        progressbar.configure(mode="indeterminate")
        progressbar.start()
        progressbar.pack(padx=20, pady=20)
        texto = customtkinter.CTkLabel(self.loading_window, text="Actualizando enlaces...")
        texto.pack(padx=20, pady=20)
        self.loading_window.attributes("-topmost", True)

    def borrar_panel(self):
        """
        Función que borra el panel.
        :return:
        """
        # Clear frame equipos_estadisticas_frame
        for widget in self.equipos_estadisticas_frame.winfo_children():
            widget.destroy()
        # Clear frame equipos_graficos_frame
        for widget in self.equipos_graficos_frame.winfo_children():
            widget.destroy()
        # Clear frame estadisticas_frame
        for widget in self.estadisticas_frame.winfo_children():
            widget.destroy()

        self.panel.eliminar_competiciones()
        self.actualizar_competicion_listview()
        self.abrir_competicion(None)
    def abrir_competicion(self, nombre_competicion):
        """
        Función que abre una competición.
        :param nombre_competicion: Nombre de la competición a abrir. Si es None, abrirá la competición Nula por defecto.
        :return:
        """

        try:

            if len(self.panel.get_competiciones()) == 0:
                self.btn_exportar_partidos.configure(state="disabled")
                self.btn_exportar_competiciones.configure(state="disabled")
            else:
                self.btn_exportar_competiciones.configure(state="normal")
                self.btn_exportar_partidos.configure(state="normal")
            #check enlaces length
            if nombre_competicion is not None:
                if len(self.panel.get_competicion(nombre_competicion).enlaces) == 0:
                    self.btn_enlaces_actualizar.configure(state="disabled")
                else:
                    self.btn_enlaces_actualizar.configure(state="normal")
            else:
                self.btn_enlaces_actualizar.configure(state="disabled")

            # Clear frame
            for widget in self.equipos_estadisticas_frame.winfo_children():
                widget.destroy()
            for widget in self.equipos_graficos_frame.winfo_children():
                widget.destroy()
            for widget in self.estadisticas_frame.winfo_children():
                widget.destroy()

            # Change tabview to General
            self.tabview_competicion.set("General")


            if nombre_competicion is None:
                self.tabview_competicion.configure(state="disabled")
                self.competicion_label.configure(text="Competición #")
                self.enlaces_lista.delete(0, "end")
                self.btn_enlaces_actualizar.configure(state="disabled")
                self.btn_enlaces_annadir.configure(state="disabled")
                self.enlaces_label_ultima_actualizacion.configure(text=f"Última actualización:\n")
                self.tabview_competicion.set("General")
                self.general_tabview.set("Estadísticas")
                self.general_tabview.configure(state="disabled")
                # Put "" on combobox
                self.partidos_buscador_combobox.set("")
                self.equipos_buscador_combobox.set("")
                self.equipos_partidos_combobox.set("")
                return

            if self.competicion_label.cget("text") == "Competición #":
                self.tabview_competicion.configure(state="normal")
                self.general_tabview.configure(state="normal")
            self.competicion_label.configure(text=nombre_competicion)
            self.enlaces_lista.delete(0, "end")


            competicion = self.panel.get_competicion(nombre_competicion)
            enlaces = self.panel.get_competicion(nombre_competicion).enlaces

            for enlace in enlaces:
                self.enlaces_lista.insert("end", enlace)


            self.btn_enlaces_annadir.configure(state="normal")
            self.enlaces_label_ultima_actualizacion.configure(text=f"Última actualización:\n{competicion.ultima_actualizacion}")


            # Tab General

            # Tab General - Clasificación
            clasificacion_df = competicion.get_clasificacion()
            self.clasificacion_treeview.delete(*self.clasificacion_treeview.get_children())
            for index, row in clasificacion_df.iterrows():
                self.clasificacion_treeview.insert(parent="", index="end", iid=index, text="", values=(
                    index, row["nombre"], row["temporada"], row["gf"], row["gc"], row["victorias"], row["derrotas"],
                    row["empates"]))

            # Tab Equipos
            # Cargar listado de equipos
            listado_equipos = competicion.get_equipos()
            nombres_equipos = []
            for equipo in listado_equipos:
                nombres_equipos.append(equipo.nombre)
            self.equipos_buscador_combobox.configure(values=nombres_equipos)
            self.equipos_buscador_combobox.set("")



            # Tab General - Estadísticas
            # Clear frame


            estadisticas = self.panel.get_estadisticas_competicion(nombre_competicion)

            etiqueta = customtkinter.CTkLabel(self.estadisticas_frame, text="Total de:",
                                              font=customtkinter.CTkFont(size=20, weight="bold"))
            etiqueta.pack(padx=10, pady=(20, 0))
            # Crear TreeView 1: Equipos, Partidos
            treeview = ttk.Treeview(self.estadisticas_frame, columns=('Equipos', 'Partidos'), show='headings',
                                    height=1)
            treeview.column('Equipos', anchor="center", width=50)
            treeview.column('Partidos', anchor="center", width=50)
            treeview.heading('Equipos', text='Equipos', anchor="center")
            treeview.heading('Partidos', text='Partidos', anchor="center")

            treeview.pack(fill="both", padx=10, pady=0)

            etiqueta = customtkinter.CTkLabel(self.estadisticas_frame, text="Victorias de:",
                                              font=customtkinter.CTkFont(size=20, weight="bold"))
            etiqueta.pack(padx=10, pady=(20, 0))
            treeview.insert(parent="", index="end", iid=0, text="", values=(estadisticas["numero_equipos"], estadisticas["numero_partidos"]))

            # Crear TreeView 2: Victorias Locales, Victorias Visitantes, Empates
            treeview = ttk.Treeview(self.estadisticas_frame,
                                    columns=('Victorias Locales', 'Victorias Visitantes', 'Empates'), show='headings',
                                    height=1)
            treeview.column('Victorias Locales', anchor="center", width=50)
            treeview.column('Victorias Visitantes', anchor="center", width=50)
            treeview.column('Empates', anchor="center", width=50)
            treeview.heading('Victorias Locales', text='Locales', anchor="center")
            treeview.heading('Victorias Visitantes', text='Visitantes', anchor="center")
            treeview.heading('Empates', text='Empates', anchor="center")
            treeview.pack(fill="both", padx=10, pady=0)

            etiqueta = customtkinter.CTkLabel(self.estadisticas_frame, text="Media de Goles: ",
                                              font=customtkinter.CTkFont(size=20, weight="bold"))
            etiqueta.pack(padx=10, pady=(20, 0))
            treeview.insert(parent="", index="end", iid=0, text="", values=(estadisticas["victorias_locales"], estadisticas["victorias_visitantes"], estadisticas["empates"]))

            # Crear TreeView 3: Goles por partido, Goles Ganadores, Goles perdedores
            treeview = ttk.Treeview(self.estadisticas_frame,
                                    columns=('Goles por partido', 'Goles Ganadores', 'Goles perdedores'),
                                    show='headings',
                                    height=1)
            treeview.column('Goles por partido', anchor="center", width=50)
            treeview.column('Goles Ganadores', anchor="center", width=50)
            treeview.column('Goles perdedores', anchor="center", width=50)

            treeview.heading('Goles por partido', text='Por partido', anchor="center")
            treeview.heading('Goles Ganadores', text='Ganadores', anchor="center")
            treeview.heading('Goles perdedores', text='Perdedores', anchor="center")
            treeview.pack(fill="both", padx=10, pady=0)
            treeview.insert(parent="", index="end", iid=0, text="", values=(str(estadisticas["media_goles_por_partido"]) + " ± " + str(estadisticas["std_goles_por_partido"]), str(estadisticas["media_goles_ganadores"]) + " ± " + str(estadisticas["std_goles_ganadores"]), str(estadisticas["media_goles_perdedores"]) + " ± " + str(estadisticas["std_goles_perdedores"])))


            # Treeview de Coeficientes
            coeficientes = competicion.get_coeficientes(clasificacion_df)
            etiqueta = customtkinter.CTkLabel(self.estadisticas_frame, text="Coeficientes:",
                                              font=customtkinter.CTkFont(size=20, weight="bold"))
            etiqueta.pack(padx=10, pady=(20, 0))
            treeview = ttk.Treeview(self.estadisticas_frame,
                                    columns=('Coeficiente', 'Valor'), show='headings',
                                    height=2)
            treeview.column('Coeficiente', anchor="center", width=50)
            treeview.column('Valor', anchor="center", width=50)
            treeview.heading('Coeficiente', text='Coeficiente', anchor="center")
            treeview.heading('Valor', text='Valor', anchor="center")
            treeview.pack(fill="both", padx=10, pady=0)

            treeview.insert(parent="", index="end", iid=0, text="", values=("Pearson GF-Puntos", round(coeficientes["GF_Pearson"], 2)))
            treeview.insert(parent="", index="end", iid=1, text="", values=("Pearson GC-Puntos", round(coeficientes["GC_Pearson"], 2)))
            # treeview.insert(parent="", index="end", iid=2, text="", values=("Spearman GF", round(coeficientes["GF_Spearman"], 2)))
            # treeview.insert(parent="", index="end", iid=3, text="", values=("Spearman GC", round(coeficientes["GC_Spearman"], 2)))

            self.update() # Forzamos a que se actualice el frame

            # Clear frame
            for widget in self.graficos_frame.winfo_children():
                widget.destroy()


            # Tab General - Gráficos
            # Gráficos
            estadisticas = self.panel.get_estadisticas_competicion(nombre_competicion)
            gf = estadisticas["goles_ganadores"]
            gc = estadisticas["goles_perdedores"]
            goles = [gf, gc]
            labels = ["Goles ganadores", "Goles perdedores"]
            fig_violinplot, ax = self.crear_violinplot(datos=goles, labels=labels, titulo="Violinplot de goles de " + nombre_competicion, ylabel="Goles", xlabel="Tipo de gol", dark=True)

            plt.tight_layout()

            fig_histograma, ax = self.crear_histograma(datos=estadisticas["goles_por_partido"], titulo="Histograma de goles por partido de " + nombre_competicion, ylabel="Frecuencia", xlabel="Goles", dark=True)


            histograma_competicion = FigureCanvasTkAgg(fig_histograma, master=self.graficos_frame)
            histograma_competicion.draw()
            histograma_competicion.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

            # Add figure to
            violinplot_competicion = FigureCanvasTkAgg(fig_violinplot, master=self.graficos_frame)
            violinplot_competicion.draw()
            violinplot_competicion.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)


            # Creamos puestos
            index = []
            for i in range(1, len(clasificacion_df.index) + 1):
                index.append(i)

            try:

                # Puesto y GF
                gf_por_partido = []
                for i in range(0, len(clasificacion_df.index)):
                    gf_por_partido.append(clasificacion_df.iloc[i]["gf"] / (clasificacion_df.iloc[i]["victorias"] + clasificacion_df.iloc[i]["derrotas"] + clasificacion_df.iloc[i]["empates"]))

                datos = [index, gf_por_partido]
                fig_puesto_gf, ax = self.crear_scatterplot(datos=datos, titulo="Puesto y goles a favor de " + nombre_competicion, ylabel="Goles a favor", xlabel="Puesto", dark=True, linea_vertical=False)
                scatterplot_competicion = FigureCanvasTkAgg(fig_puesto_gf, master=self.graficos_frame)
                scatterplot_competicion.draw()
                scatterplot_competicion.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

                # Puesto y GC
                gc_por_partido = []
                for i in range(0, len(clasificacion_df.index)):
                    gc_por_partido.append(clasificacion_df.iloc[i]["gc"] / (clasificacion_df.iloc[i]["victorias"] + clasificacion_df.iloc[i]["derrotas"] + clasificacion_df.iloc[i]["empates"]))
                datos = [index, gc_por_partido]
                fig_puesto_gc, ax = self.crear_scatterplot(datos=datos, titulo="Puesto y goles en contra de " + nombre_competicion, ylabel="Goles en contra", xlabel="Puesto", dark=True, linea_vertical=False)
                scatterplot_competicion = FigureCanvasTkAgg(fig_puesto_gc, master=self.graficos_frame)
                scatterplot_competicion.draw()
                scatterplot_competicion.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)
            except:
                pass

            # Tab Partidos

            #
            self.partidos_buscador_combobox.set("")
            partidos_df = competicion.partidos_to_df()
            partidos_df["dif"] = abs(partidos_df["gl"] - partidos_df["gv"])
            partidos_df = partidos_df.sort_values(by=["dif"], ascending=False)



            # Insert partidos
            self.partidos_treeview.delete(*self.partidos_treeview.get_children())
            for index, row in partidos_df.iterrows():
                self.partidos_treeview.insert(parent="", index="end", iid=index, text="", values=(
                    row["local"], row["gl"], row["gv"], row["visitante"]))

            # Tab Equipos
            self.equipos_buscador_combobox.set("")
            self.equipos_partidos_combobox.set("")
            self.equipos_partidos_treeview.delete(*self.equipos_partidos_treeview.get_children())


        except Exception as e:

            self.show_message("Error al abrir la competición.\n" + str(e))
            print(e)

    def annadir_competicion(self):
        """
        Función que muestra una ventana para añadir una competición.
        :return:
        """
        # Create tokLevelWindow
        self.annadir_competicion_window = customtkinter.CTkToplevel(self)
        self.annadir_competicion_window.title("Añadir Competición")
        self.annadir_competicion_window.geometry(f"{300}x{150}")
        #icon
        self.annadir_competicion_window.iconbitmap(funciones_aux.resource_path(ICON_PATH))
        self.annadir_competicion_window.attributes("-topmost", True)
        self.annadir_competicion_window.resizable(False, False)
        # Create frame
        annadir_competicion_frame = customtkinter.CTkFrame(self.annadir_competicion_window, corner_radius=10)
        annadir_competicion_frame.pack(expand=True, fill="both")
        annadir_competicion_frame.grid_propagate(True)
        # Create label
        annadir_competicion_label = customtkinter.CTkLabel(annadir_competicion_frame, text="Nombre de la competición")
        annadir_competicion_label.pack(padx=20, pady=10)
        # Create entry
        self.annadir_competicion_entry = customtkinter.CTkEntry(annadir_competicion_frame, width=200, border_width=0)
        self.annadir_competicion_entry.pack(padx=10, pady=10)
        # Create button
        annadir_competicion_button = customtkinter.CTkButton(annadir_competicion_frame, text="Añadir", command=self.annadir_competicion_event)
        annadir_competicion_button.pack(padx=20, pady=10)

        # bind enter key
        self.annadir_competicion_window.bind("<Return>", lambda event: self.annadir_competicion_event())

    def get_competicion(self, nombre):
        """
        Función que devuelve una competición. Llama a la función get_competicion de la clase Panel.
        :param nombre: Nombre de la competición a devolver.
        :return:
        """
        return self.panel.get_competicion(nombre)
    def annadir_competicion_event(self):
        """
        Función que se ejecuta cuando se pulsa el botón de añadir competición.
        :return:
        """
        entrada = self.annadir_competicion_entry.get()
        self.annadir_competicion_window.destroy()
        self.panel.add_competicion(gestor.Competicion(nombre=entrada, actualizar_al_iniciar=False, nombre_bd=PANEL_PATH))
        self.actualizar_competicion_listview()
        self.abrir_competicion(entrada)
        self.competiciones_lista.select(-1)

        pass

    def borrar_competicion(self):
        """
        Función que elimina la competición seleccionada.
        :return:
        """
        self.panel.eliminar_competicion(self.competicion_label.cget("text"))
        self.actualizar_competicion_listview()
        self.abrir_competicion(None)



    def actualizar_competicion_listview(self):
        """
        Función que actualiza la lista de competiciones.
        :return:
        """
        self.competiciones_lista.delete(0, "end")
        competiciones = self.panel.get_competiciones()
        for competicion in competiciones:
            self.competiciones_lista.insert("end", competicion.nombre)
        pass


    def abrir_panel(self):
        """
        Función que abre un panel. Genera una ventana para seleccionar el panel a abrir.
        :return:
        """
        origen = filedialog.askopenfilename(initialdir=".", title="Abrir Panel",
                                                filetypes=(("DataBase", "*.db"), ("Todos los archivos", "*.*")))
        if origen == "" or origen is None:
             return
        try:
            path = funciones_aux.resource_path(PANEL_PATH)
            copyfile(origen, path)
        except:
            print("Error al abrir el panel")

        self.cargar_estado()
        self.abrir_competicion(None)


    def annadir_al_panel(self):
        """
        Función que añade una competición al panel. #TODO
        :return:
        """
        self.show_message("Función no implementada")

    def guardar_panel(self):
        """
        Función que guarda el panel. Genera una ventana para seleccionar el destino del panel.
        :return:
        """
        destino = filedialog.asksaveasfilename(initialdir=".", title="Guardar Panel",
                                                filetypes=(("DataBase", "*.db"), ("Todos los archivos", "*.*")), defaultextension=".db")
        if destino == "" or destino is None:
             return
        try:
            path = funciones_aux.resource_path(PANEL_PATH)
            copyfile(path, destino)
        except:
            print("Error al guardar el panel")

    def show_message(self, message):
        """
        Función que muestra una ventana con un mensaje.
        :param message:
        :return:
        """
        self.message_window = customtkinter.CTkToplevel(self)
        self.message_window.title("Mensaje")
        self.message_window.geometry(f"{300}x{150}")
        self.message_window.attributes("-topmost", True)
        self.message_window.resizable(False, False)
        # Create frame
        message_frame = customtkinter.CTkFrame(self.message_window, corner_radius=10)
        message_frame.pack(expand=True, fill="both")
        message_frame.grid_propagate(True)
        # Create label
        message_label = customtkinter.CTkLabel(message_frame, text=message)
        message_label.pack(padx=20, pady=10)
        # Create button
        message_button = customtkinter.CTkButton(message_frame, text="Aceptar", command=self.message_window.destroy)
        message_button.pack(padx=20, pady=(10,0))


    def seleccionar_equipos(self, nombre_equipo):
        """
        Función que selecciona un equipo en el panel.
        :param nombre_equipo: Nombre del equipo a seleccionar.
        :return:
        """
        competicion = self.get_competicion(self.competicion_label.cget("text"))
        equipo = competicion.get_equipo(nombre_equipo)
        df_clasificacion = competicion.get_clasificacion()
        estadisticas = competicion.get_estadisticas_equipo(equipo, df_clasificacion)


        # Clear frame
        for widget in self.equipos_estadisticas_frame.winfo_children():
            widget.destroy()

        # Goles a favor y en contra
        label = customtkinter.CTkLabel(self.equipos_estadisticas_frame, text="Información general", font=customtkinter.CTkFont(size=20, weight="bold"))
        label.pack(padx=10, pady=10)
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Puesto", "Goles a favor", "Goles en contra"), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("Puesto", anchor="center", width=50)
        treeview.column("Goles a favor", anchor="center", width=50)
        treeview.column("Goles en contra", anchor="center", width=50)
        treeview.heading("Puesto", text="Puesto", anchor="center")
        treeview.heading("Goles a favor", text="Goles a favor", anchor="center")
        treeview.heading("Goles en contra", text="Goles en contra", anchor="center")

        treeview.insert(parent="", index="end", iid=0, text="", values=(estadisticas["puesto"],sum(estadisticas["gf"]), sum(estadisticas["gc"])))


        # Media de goles a favor y en contra
        label = customtkinter.CTkLabel(self.equipos_estadisticas_frame, text="Goles por partido", font=customtkinter.CTkFont(size=20, weight="bold"))
        label.pack(padx=10, pady=10)
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Goles a favor", "Goles en contra"), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)

        treeview.column("Goles a favor", anchor="center", width=50)
        treeview.column("Goles en contra", anchor="center", width=50)
        treeview.heading("Goles a favor", text="Media de goles a favor", anchor="center")
        treeview.heading("Goles en contra", text="Media de goles en contra", anchor="center")

        treeview.insert(parent="", index="end", iid=0, text="", values=(str(estadisticas["avg_gf"]) + " ± " + str(estadisticas["std_gf"]), str(estadisticas["avg_gc"]) + " ± " + str(estadisticas["std_gc"])))

        # Goles por partido esperados
        # label = customtkinter.CTkLabel(self.equipos_estadisticas_frame, text="Goles por partido esperados", font=customtkinter.CTkFont(size=20, weight="bold"))
        # label.pack(padx=10, pady=10)
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Goles a favor", "Goles en contra"), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("Goles a favor", anchor="center", width=50)
        treeview.column("Goles en contra", anchor="center", width=50)
        treeview.heading("Goles a favor", text="Goles a favor esperados", anchor="center")
        treeview.heading("Goles en contra", text="Goles en contra esperados", anchor="center")
        treeview.insert(parent="", index="end", iid=0, text="",
                        values=(estadisticas["gf_esperados_por_partido"], estadisticas["gc_esperados_por_partido"]))



        # Victorias, derrotas y empates locales y visitantes

        label = customtkinter.CTkLabel(self.equipos_estadisticas_frame, text="Victorias, derrotas y empates", font=customtkinter.CTkFont(size=20, weight="bold"))
        label.pack(padx=10, pady=10)
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Tipo", "Victorias", "Derrotas", "Empates"), show='headings', height=3)
        treeview.pack( fill="both", padx=10, pady=10)
        treeview.column("Tipo", anchor="center", width=50)
        treeview.column("Victorias", anchor="center", width=50)
        treeview.column("Derrotas", anchor="center", width=50)
        treeview.column("Empates", anchor="center", width=50)
        treeview.heading("Tipo", text="Tipo", anchor="center")
        treeview.heading("Victorias", text="Victorias", anchor="center")
        treeview.heading("Derrotas", text="Derrotas", anchor="center")
        treeview.heading("Empates", text="Empates", anchor="center")

        treeview.insert(parent="", index="end", iid=0, text="", values=("Locales", estadisticas["victorias_locales"], estadisticas["derrotas_locales"], estadisticas["empates_locales"]))
        treeview.insert(parent="", index="end", iid=1, text="", values=("Visitantes", estadisticas["victorias_visitantes"], estadisticas["derrotas_visitantes"], estadisticas["empates_visitantes"]))
        treeview.insert(parent="", index="end", iid=2, text="", values=("Totales", sum(estadisticas["victorias"]), sum(estadisticas["derrotas"]), sum(estadisticas["empates"])))

        # Mejor racha de victorias, peor racha de derrotas y mayor racha de empates
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Mejor racha de victorias", "Peor racha de derrotas", "Mayor racha de empates"), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("Mejor racha de victorias", anchor="center", width=50)
        treeview.column("Peor racha de derrotas", anchor="center", width=50)
        treeview.column("Mayor racha de empates", anchor="center", width=50)
        treeview.heading("Mejor racha de victorias", text="Mejor racha de victorias", anchor="center")
        treeview.heading("Peor racha de derrotas", text="Peor racha de derrotas", anchor="center")
        treeview.heading("Mayor racha de empates", text="Mayor racha de empates", anchor="center")

        treeview.insert(parent="", index="end", iid=0, text="", values=(estadisticas["mayor_racha_victorias"], estadisticas["mayor_racha_derrotas"], estadisticas["mayor_racha_empates"]))

        # Mejor victoria
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Mejor Victoria",), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("Mejor Victoria", anchor="center", width=50)
        treeview.heading("Mejor Victoria", text="Mejor Victoria", anchor="center")
        partido = estadisticas["mejor_victoria"]
        texto = f"{partido.local}  {partido.gl} - {partido.gv}  {partido.visitante} " if partido is not None else ""
        treeview.insert(parent="", index="end", iid=0, text="", values=(texto,))

        # Peor derrota
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Peor Derrota",), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("Peor Derrota", anchor="center", width=50)
        treeview.heading("Peor Derrota", text="Peor Derrota", anchor="center")
        partido = estadisticas["peor_derrota"]
        texto = f"{partido.local}  {partido.gl} - {partido.gv}  {partido.visitante}" if partido is not None else ""
        treeview.insert(parent="", index="end", iid=0, text="", values=(texto,))

        # Últimos 5 partidos
        label = customtkinter.CTkLabel(self.equipos_estadisticas_frame, text="Últimos 5 partidos", font=customtkinter.CTkFont(size=20, weight="bold"))
        label.pack(padx=10, pady=10)
        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("Victorias", "Derrotas", "Empates"), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("Victorias", anchor="center", width=50)
        treeview.column("Derrotas", anchor="center", width=50)
        treeview.column("Empates", anchor="center", width=50)
        treeview.heading("Victorias", text="Victorias", anchor="center")
        treeview.heading("Derrotas", text="Derrotas", anchor="center")
        treeview.heading("Empates", text="Empates", anchor="center")
        treeview.insert(parent="", index="end", iid=0, text="", values=(estadisticas["victorias_ultimos_5"], estadisticas["derrotas_ultimos_5"], estadisticas["empates_ultimos_5"]))

        treeview = ttk.Treeview(self.equipos_estadisticas_frame, columns=("GF", "GC"), show='headings', height=1)
        treeview.pack(fill="both", padx=10, pady=10)
        treeview.column("GF", anchor="center", width=50)
        treeview.column("GC", anchor="center", width=50)
        treeview.heading("GF", text="Media goles a favor", anchor="center")
        treeview.heading("GC", text="Media goles en contra", anchor="center")
        treeview.insert(parent="", index="end", iid=0, text="", values=(f"{estadisticas["avg_gf_ultimos_5"]} ± {estadisticas["std_gf_ultimos_5"]}", f"{estadisticas["avg_gc_ultimos_5"]} ± {estadisticas["std_gc_ultimos_5"]}"))


        # Gráficos
        gf = estadisticas["gf"]
        gc = estadisticas["gc"]
        goles = [gf, gc]
        labels = ["Goles a favor", "Goles en contra"]
        fig_violinplot, ax = self.crear_violinplot(datos=goles, labels=labels, titulo="Violinplot de goles de " + nombre_equipo, ylabel="Goles", xlabel="Tipo de gol", dark=True)
        # plt.tight_layout()

        # Gráficos/ Scatterplot
        gt_y_diferencia = estadisticas["gt_y_diferencia"]
        valores_x = []
        valores_y = []
        for i in gt_y_diferencia:
            valores_x.append(i[1])
            valores_y.append(i[0])
        fig_scatter, ax = self.crear_scatterplot(datos=[valores_x, valores_y], titulo="Scatterplot de goles de " + nombre_equipo, ylabel="Goles totales", xlabel="Diferencia", dark=True, linea_vertical=True)

        # Clear frame
        for widget in self.equipos_graficos_frame.winfo_children():
            widget.destroy()

        # Add figure to
        violinplot_equipo = FigureCanvasTkAgg(fig_violinplot, master=self.equipos_graficos_frame)
        violinplot_equipo.draw()
        violinplot_equipo.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        scatterplot_equipo = FigureCanvasTkAgg(fig_scatter, master=self.equipos_graficos_frame)
        scatterplot_equipo.draw()
        scatterplot_equipo.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        # Partidos
        self.equipos_partidos_combobox.set("")
        partidos_df = competicion.get_partidos_equipo_df(equipo)
        partidos_df["dif"] = abs(partidos_df["gl"] - partidos_df["gv"])
        partidos_df = partidos_df.sort_values(by=["dif"], ascending=False)

        # Insert partidos
        self.equipos_partidos_treeview.delete(*self.equipos_partidos_treeview.get_children())

        for index, row in partidos_df.iterrows():
            self.equipos_partidos_treeview.insert(parent="", index="end", iid=index, text="", values=(
            row["local"], row["gl"], row["gv"], row["visitante"]))


        # Al finalizar
        # Actualizar combobox con todos los equipos
        nombres_equipos = []
        for equipo in competicion.get_equipos():
            nombres_equipos.append(equipo.nombre)
        self.equipos_buscador_combobox.configure(values=nombres_equipos)


    def crear_violinplot(self, ax = None, datos = None, labels = None, titulo = None, ylabel = None, xlabel = None, dark = True):
        """
        Función que crea un violinplot.
        :param ax:
        :param datos:
        :param labels:
        :param titulo:
        :param ylabel:
        :param xlabel:
        :param dark: True si el fondo es oscuro, False si es claro.
        :return: fig, ax
        """
        try:
            if len(datos) != len(labels):
                raise Exception("El número de datos y etiquetas no coincide")
            if len(datos) != 2:
                raise Exception("El número de grupos de datos debe ser 2")
            if len(datos[0]) != len(datos[1]):
                raise Exception("El número de datos de cada grupo debe ser el mismo")
            if len(datos[0]) == 0:
                raise Exception("Los datos no pueden estar vacíos")
        except Exception as e:
            print(e)
            return None, None

        color_fondo = "#2a2d2e" if dark else "white"
        color_texto = "white" if dark else "black"
        if ax is None:
            fig, ax = plt.subplots(facecolor=color_fondo, figsize=(12, 6))
        else:
            fig = None

        violin_parts = ax.violinplot(datos, showmedians=True, showmeans=True, showextrema=True)
        for pc in violin_parts['bodies']:
            pc.set_facecolor('C0')
            pc.set_edgecolor('white')
            pc.set_alpha(0.7)

        # Propiedades de la mediana
        violin_parts['cmedians'].set_color('white')
        violin_parts['cmedians'].set_linewidth(1)

        # Propiedades de la media
        # violin_parts['cmeans'].set_marker('D')
        # violin_parts['cmeans'].set_markerfacecolor('C1')
        # violin_parts['cmeans'].set_markeredgecolor('C1')
        # violin_parts['cmeans'].set_markersize(10)
        ax.spines["bottom"].set_color(color_texto)
        ax.spines["left"].set_color(color_texto)
        ax.spines["top"].set_color(color_texto)
        ax.spines["right"].set_color(color_texto)
        ax.tick_params(axis='x', colors=color_texto, labelsize=14)
        ax.tick_params(axis='y', colors=color_texto, labelsize=14)
        ax.set_facecolor(color_fondo)
        ax.set_xticks(arange(1, len(labels) + 1), labels=labels, color=color_texto, fontdict={"fontsize": 16})
        ax.set_title(titulo, color=color_texto, fontdict={"fontsize": 20})
        ax.set_ylabel(ylabel, color=color_texto, fontdict={"fontsize": 16})
        ax.set_xlabel(xlabel, color=color_texto, fontdict={"fontsize": 16})

        plt.tight_layout()
        return fig, ax

    def crear_scatterplot(self, ax = None, datos = None, titulo = None, ylabel = None, xlabel = None, dark = True, linea_vertical = True):
        """
        Función que crea un scatterplot.
        :param ax:
        :param datos:
        :param titulo:
        :param ylabel:
        :param xlabel:
        :param dark: True si el fondo es oscuro, False si es claro.
        :param linea_vertical: True si se quiere dibujar una línea vertical en x = 0, False si no.
        :return: fig, ax
        """
        color_fondo = "#2a2d2e" if dark else "white"
        color_texto = "white" if dark else "black"
        color_puntos = "white" if dark else "black"
        if ax is None:
            fig, ax = plt.subplots(facecolor=color_fondo, figsize=(12, 6))
        else:
            fig = None

        coefficients = polyfit(datos[0], datos[1], 1)
        polynomial = poly1d(coefficients)
        tendencia_x = linspace(min(datos[0]), max(datos[0]), 100)
        tendencia_y = polynomial(tendencia_x)


        ax.plot(tendencia_x, tendencia_y, color='C0', label='Línea de tendencia', linewidth=1.5 )
        # Draw a vertical line at x= 0
        if linea_vertical:
            ax.axvline(x=0, color=color_texto, linewidth=1.5, alpha=0.5, linestyle='--')

        ax.scatter(datos[0], datos[1], color="C0", s=20)
        ax.spines["bottom"].set_color(color_texto)
        ax.spines["left"].set_color(color_texto)
        ax.spines["top"].set_color(color_texto)
        ax.spines["right"].set_color(color_texto)
        ax.tick_params(axis='x', colors=color_texto, labelsize=14)
        ax.tick_params(axis='y', colors=color_texto, labelsize=14)
        ax.set_facecolor(color_fondo)
        ax.set_title(titulo, color=color_texto, fontdict={"fontsize": 20})
        ax.set_ylabel(ylabel, color=color_texto, fontdict={"fontsize": 16})
        ax.set_xlabel(xlabel, color=color_texto, fontdict={"fontsize": 16})
        legend = ax.legend()
        legend.get_frame().set_facecolor(color_fondo)
        legend.get_frame().set_edgecolor(color_texto)
        legend.get_frame().set_linewidth(1)
        legend.get_frame().set_alpha(1)
        legend.get_texts()[0].set_color(color_texto)

        return fig, ax

    def crear_histograma(self, ax = None, datos = None, titulo = None, ylabel = None, xlabel = None, dark = True):
        """
        Función que crea un histograma.
        :param ax:
        :param datos:
        :param titulo:
        :param ylabel:
        :param xlabel:
        :param dark: True si el fondo es oscuro, False si es claro.
        :return: fig, ax
        """
        try:
            if len(datos) == 0:
                raise Exception("Los datos no pueden estar vacíos")
        except Exception as e:
            print(e)
            return None, None
        color_fondo = "#2a2d2e" if dark else "white"
        color_texto = "white" if dark else "black"
        color_puntos = "white" if dark else "black"
        if ax is None:
            fig, ax = plt.subplots(facecolor=color_fondo, figsize=(12, 6))
        else:
            fig = None

        bins = arange(min(datos), max(datos) + 1.5) - 0.5
        ax.hist(datos, bins = bins,color="C0", edgecolor="white")
        ax.spines["bottom"].set_color(color_texto)
        ax.spines["left"].set_color(color_texto)
        ax.spines["top"].set_color(color_texto)
        ax.spines["right"].set_color(color_texto)
        ax.tick_params(axis='x', colors=color_texto, labelsize=14)
        # Set the ticks to be every 3 bins
        if len(bins) > 60:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(3))
        elif len(bins) > 30:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
        else:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))



        ax.tick_params(axis='y', colors=color_texto, labelsize=14)
        ax.set_facecolor(color_fondo)
        ax.set_title(titulo, color=color_texto, fontdict={"fontsize": 20})
        ax.set_ylabel(ylabel, color=color_texto, fontdict={"fontsize": 16})
        ax.set_xlabel(xlabel, color=color_texto, fontdict={"fontsize": 16})

        return fig, ax



    def annadir_enlace(self):
        """
        Función que muestra una ventana para añadir un enlace.
        :return:
        """
        # Create tokLevelWindow
        self.annadir_enlace_window = customtkinter.CTkToplevel(self)
        self.annadir_enlace_window.title("Añadir Enlace")
        self.annadir_enlace_window.geometry(f"{300}x{150}")
        self.annadir_enlace_window.attributes("-topmost", True)
        self.annadir_enlace_window.resizable(False, False)
        # Create frame
        annadir_enlace_frame = customtkinter.CTkFrame(self.annadir_enlace_window, corner_radius=10)
        annadir_enlace_frame.pack(expand=True, fill="both")
        annadir_enlace_frame.grid_propagate(True)
        # Create label
        annadir_enlace_label = customtkinter.CTkLabel(annadir_enlace_frame, text="Enlace")
        annadir_enlace_label.pack(padx=20, pady=10)
        # Create entry
        self.annadir_enlace_entry = customtkinter.CTkEntry(annadir_enlace_frame, width=200, border_width=0)
        self.annadir_enlace_entry.pack(padx=10, pady=10)
        # Create button
        annadir_enlace_button = customtkinter.CTkButton(annadir_enlace_frame, text="Añadir", command=self.annadir_enlace_event)
        annadir_enlace_button.pack(padx=20, pady=10)

        # bind enter key
        self.annadir_enlace_window.bind("<Return>", lambda event: self.annadir_enlace_event())

    def annadir_enlace_event(self):
        """
        Función que se ejecuta cuando se pulsa el botón de añadir enlace. Añade el enlace a la competición seleccionada.
        :return:
        """
        enlace = self.annadir_enlace_entry.get()

        self.panel.annadir_enlace_a_competicion(self.competicion_label.cget("text"), enlace)
        self.panel.set_fecha_ultima_actualizacion(self.competicion_label.cget("text"), None)
        self.annadir_enlace_window.destroy()

        self.abrir_competicion(self.competicion_label.cget("text"))

    def borrar_enlace(self):
        """
        Función que elimina el enlace seleccionado.
        :return:
        """
        if self.modificar_enlace_window is not None:
            self.modificar_enlace_window.destroy()
        enlace = self.enlaces_lista.get(self.enlaces_lista.curselection())
        self.panel.eliminar_enlace_a_competicion(self.competicion_label.cget("text"), enlace)
        self.panel.set_fecha_ultima_actualizacion(self.competicion_label.cget("text"), None)
        self.abrir_competicion(self.competicion_label.cget("text"))

    def modificar_enlace(self):
        """
        Función que muestra una ventana para modificar el enlace seleccionado.
        :return:
        """
        #Open new window with entry
        self.modificar_enlace_window = customtkinter.CTkToplevel(self)
        self.modificar_enlace_window.title("Modificar Enlace")
        # self.modificar_enlace_window.geometry(f"{400}x{150}")
        self.modificar_enlace_window.attributes("-topmost", True)
        self.modificar_enlace_window.resizable(False, False)
        # Create frame
        modificar_enlace_frame = customtkinter.CTkFrame(self.modificar_enlace_window, corner_radius=10)
        modificar_enlace_frame.pack(expand=True, fill="both")
        modificar_enlace_frame.grid_propagate(True)
        # Create label
        modificar_enlace_label = customtkinter.CTkLabel(modificar_enlace_frame, text="Enlace", font=customtkinter.CTkFont(size=20, weight="bold"))
        modificar_enlace_label.grid(row=0, column=0, columnspan = 2, padx=20, pady=10)
        # Create entry
        self.modificar_enlace_entry = customtkinter.CTkEntry(modificar_enlace_frame,  border_width=0, width=400)
        self.modificar_enlace_entry.grid(row=1, column=0, columnspan = 2, padx=10, pady=10, sticky="ew")
        # Create button
        modificar_enlace_button = customtkinter.CTkButton(modificar_enlace_frame, text="Modificar", command=self.modificar_enlace_event)
        modificar_enlace_button.grid(row=2, column=0, padx=20, pady=10)
        # Create button
        borrar_enlace_button = customtkinter.CTkButton(modificar_enlace_frame, text="Borrar", command=self.borrar_enlace)
        borrar_enlace_button.grid(row=2, column=1, padx=10, pady=10)


        # Set entry text
        enlace = self.enlaces_lista.get(self.enlaces_lista.curselection())
        self.modificar_enlace_entry.insert("end", enlace)

        # bind modificar_enlace_window on destroy
        self.modificar_enlace_window.protocol("WM_DELETE_WINDOW", lambda : on_destroy())
        def on_destroy():
            if self.modificar_enlace_window is not None:
                self.enlaces_lista.deactivate(self.enlaces_lista.curselection())
            self.modificar_enlace_window.destroy()

    def modificar_enlace_event(self):
        """
        Función que se ejecuta cuando se pulsa el botón de modificar enlace. Modifica el enlace seleccionado.
        :return:
        """
        enlace = self.modificar_enlace_entry.get()
        enlace_viejo = self.enlaces_lista.get(self.enlaces_lista.curselection())
        self.panel.modificar_enlace_a_competicion(self.competicion_label.cget("text"), enlace_viejo, enlace)
        self.panel.set_fecha_ultima_actualizacion(self.competicion_label.cget("text"), None)
        self.abrir_competicion(self.competicion_label.cget("text"))
        self.modificar_enlace_window.destroy()

    def modificar_nombre_competicion(self, event):
        """
        Función que muestra una ventana para modificar el nombre de la competición seleccionada.
        :param event:
        :return:
        """

        if self.competicion_label.cget("text") == "Competición #":
            return
        # Create tokLevelWindow
        self.modificar_nombre_competicion_window = customtkinter.CTkToplevel(self)
        self.modificar_nombre_competicion_window.title("Modificar Nombre de la Competición")
        self.modificar_nombre_competicion_window.geometry(f"{300}x{150}")
        self.modificar_nombre_competicion_window.attributes("-topmost", True)
        self.modificar_nombre_competicion_window.resizable(False, False)
        # Create frame
        modificar_nombre_competicion_frame = customtkinter.CTkFrame(self.modificar_nombre_competicion_window, corner_radius=10)

        modificar_nombre_competicion_frame.pack(expand=True, fill="both")
        modificar_nombre_competicion_frame.grid_propagate(True)
        # Create label
        modificar_nombre_competicion_label = customtkinter.CTkLabel(modificar_nombre_competicion_frame, text="Nombre de la competición")
        modificar_nombre_competicion_label.pack(padx=20, pady=10)
        # Create entry
        self.modificar_nombre_competicion_entry = customtkinter.CTkEntry(modificar_nombre_competicion_frame, width=200, border_width=0)
        self.modificar_nombre_competicion_entry.pack(padx=10, pady=10)
        # Create button
        modificar_nombre_competicion_button = customtkinter.CTkButton(modificar_nombre_competicion_frame, text="Modificar", command=self.modificar_nombre_competicion_event)
        modificar_nombre_competicion_button.pack(padx=20, pady=10)

        # Set entry text
        self.modificar_nombre_competicion_entry.insert("end", self.competicion_label.cget("text"))

    def modificar_nombre_competicion_event(self):
        """
        Función que se ejecuta cuando se pulsa el botón de modificar nombre de la competición. Modifica el nombre de la competición seleccionada.
        :return:
        """
        nombre = self.modificar_nombre_competicion_entry.get()
        self.panel.modificar_nombre_competicion(self.competicion_label.cget("text"), nombre)
        self.modificar_nombre_competicion_window.destroy()
        self.actualizar_competicion_listview()
        self.abrir_competicion(nombre)

    def ordenar_partidos(self, event):
        """
        Función que ordena los partidos de la competición seleccionada según el criterio seleccionado.
        :param event:
        :return:
        """

        if self.competicion_label.cget("text") == "Competición #":
            return
        partidos_df = self.panel.get_competicion(self.competicion_label.cget("text")).partidos_to_df()
        partidos_df["dif"] = abs(partidos_df["gl"] - partidos_df["gv"])
        partidos_df["tot"] = partidos_df["gl"] + partidos_df["gv"]
        partidos_df["goles_ganadores"] = partidos_df.apply(lambda row: row["gl"] if row["gl"] > row["gv"] else row["gv"], axis=1)
        partidos_df["goles_perdedores"] = partidos_df.apply(lambda row: row["gl"] if row["gl"] < row["gv"] else row["gv"], axis=1)


        match self.partidos_buscador_combobox.get():
            case "Mayor diferencia":
                partidos_df = partidos_df.sort_values(by=["dif"], ascending=False)
            case "Menor diferencia":
                partidos_df = partidos_df.sort_values(by=["dif"], ascending=True)
            case "Más goles por partido":
                partidos_df = partidos_df.sort_values(by=["tot"], ascending=False)
            case "Menos goles por partido":
                partidos_df = partidos_df.sort_values(by=["tot"], ascending=True)
            case "Más goles ganadores":
                partidos_df = partidos_df.sort_values(by=["goles_ganadores"], ascending=False)
            case "Menos goles ganadores":
                partidos_df = partidos_df.sort_values(by=["goles_ganadores"], ascending=True)
            case "Más goles perdedores":
                partidos_df = partidos_df.sort_values(by=["goles_perdedores"], ascending=False)
            case "Menos goles perdedores":
                partidos_df = partidos_df.sort_values(by=["goles_perdedores"], ascending=True)
            case _:
                print("Error")

        # Insert partidos
        self.partidos_treeview.delete(*self.partidos_treeview.get_children())
        for index, row in partidos_df.iterrows():
            self.partidos_treeview.insert(parent="", index="end", iid=index, text="", values=(
            row["local"], row["gl"], row["gv"], row["visitante"]))



    def ordenar_partidos_equipo(self, event):
        """
        Función que ordena los partidos del equipo seleccionado según el criterio seleccionado.
        :param event:
        :return:
        """

        if self.competicion_label.cget("text") == "Competición #":
            return
        competicion = self.panel.get_competicion(self.competicion_label.cget("text"))
        equipo = competicion.get_equipo(self.equipos_buscador_combobox.get())
        partidos_df = competicion.get_partidos_equipo_df(equipo)
        partidos_df["dif"] = abs(partidos_df["gl"] - partidos_df["gv"])
        partidos_df["tot"] = partidos_df["gl"] + partidos_df["gv"]
        partidos_df["goles_equipo"] = partidos_df.apply(lambda row: row["gl"] if row["local"] == equipo.nombre else row["gv"], axis=1)
        partidos_df["goles_rival"] = partidos_df.apply(lambda row: row["gl"] if row["local"] != equipo.nombre else row["gv"], axis=1)
        partidos_df["dif_neta"] = partidos_df.apply(lambda row: row["goles_equipo"] - row["goles_rival"], axis=1)

        match self.equipos_partidos_combobox.get():
            case "Más goles por partido":
                partidos_df = partidos_df.sort_values(by=["tot"], ascending=False)
            case "Menos goles por partido":
                partidos_df = partidos_df.sort_values(by=["tot"], ascending=True)
            case "Mejor resultado":
                partidos_df = partidos_df.sort_values(by=["dif_neta"], ascending=False)
            case "Peor resultado":
                partidos_df = partidos_df.sort_values(by=["dif_neta"], ascending=True)
            case "Más goles a favor":
                partidos_df = partidos_df.sort_values(by=["goles_equipo"], ascending=False)
            case "Menos goles a favor":
                partidos_df = partidos_df.sort_values(by=["goles_equipo"], ascending=True)
            case "Más goles en contra":
                partidos_df = partidos_df.sort_values(by=["goles_rival"], ascending=False)
            case "Menos goles en contra":
                partidos_df = partidos_df.sort_values(by=["goles_rival"], ascending=True)
            case _:
                print("Error")

        # Insert partidos
        self.equipos_partidos_treeview.delete(*self.equipos_partidos_treeview.get_children())
        for index, row in partidos_df.iterrows():
            self.equipos_partidos_treeview.insert(parent="", index="end", iid=index, text="", values=(
            row["local"], row["gl"], row["gv"], row["visitante"]))




    def cargar_estado(self):
        """
        Función que carga el estado de la aplicación. Usa PANEL_PATH como ruta para cargar el panel.
        :return:
        """
        path = funciones_aux.resource_path(PANEL_PATH)
        self.panel = gestor.panel_from_db(ruta_abs= path, ruta_rel= PANEL_PATH)
        self.abrir_competicion(None)
        self.actualizar_competicion_listview()

    def exportar_partidos(self):
        """
        Función que exporta los partidos de la competición seleccionada. Abre un filedialog para seleccionar la ruta y el formato.
        :return:
        """
        partidos = self.panel.partidos_to_df()



        filepath = filedialog.asksaveasfilename(initialdir=".", title="Guardar Partidos",
                                                filetypes=(("Excel", "*.xlsx"), ("CSV", "*.csv"), ("JSON", "*.json"), ("Todos los archivos", "*.*")), defaultextension=".xlsx")
        if filepath == "" or filepath is None:
            return
        if filepath.endswith(".xlsx"):
            partidos.to_excel(filepath)
        elif filepath.endswith(".csv"):
            partidos.to_csv(filepath)
        elif filepath.endswith(".json"):
            partidos.to_json(filepath)
        else:
            self.show_message("Formato no soportado")



    def exportar_competiciones(self):
        """
        Función que exporta las competiciones. Abre un filedialog para seleccionar la ruta y el formato.
        :return:
        """
        competiciones = self.panel.competiciones_to_df()
        filepath = filedialog.asksaveasfilename(initialdir=".", title="Guardar Competiciones",
                                                filetypes=(("Excel", "*.xlsx"), ("CSV", "*.csv"), ("JSON", "*.json"), ("Todos los archivos", "*.*")), defaultextension=".xlsx")
        if filepath == "" or filepath is None:
            return
        if filepath.endswith(".xlsx"):
            competiciones.to_excel(filepath)
        elif filepath.endswith(".csv"):
            competiciones.to_csv(filepath)
        elif filepath.endswith(".json"):
            competiciones.to_json(filepath)
        else:
            self.show_message("Formato no soportado")



if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", lambda : app.cerrar_app())
    app.mainloop()

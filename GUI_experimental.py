import json
import shutil
import threading
from tkinter import ttk, filedialog

import customtkinter
import tkinter as tk

import pandas as pd
from CTkListbox import *
from PIL import Image
from customtkinter import CTkSegmentedButton, CTkImage

import SH_Stats_back.gestor as gestor

PANEL_PATH = "config/panel.db"
class App(customtkinter.CTk):
    panel = gestor.Panel("Panel Predeterminado", [])
    def __init__(self):
        super().__init__()
        self.title("Spanish Handball Stats")
        self.geometry(f"{1100}x{580}")
        # ´maximize
        self.state("zoomed")
        self.iconbitmap("config/logo_shs_sf_dark.ico")

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



        self.logo_image = CTkImage(light_image=Image.open("config/logo_shs_sf_light.png").resize((150, 150)),
                                      dark_image=Image.open("config/logo_shs_sf_dark.png").resize((150, 150)),
                                      size=(150, 150))
        self.logo_image_label = customtkinter.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        self.logo_image_label.grid(row=0, column=0, padx=5, pady=10)





        self.btn_actualizar_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Actualizar Panel", command=lambda : self.show_message("Función no implementada"))
        self.btn_actualizar_panel.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_frame.rowconfigure(2, weight=1)


        self.btn_abrir_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Abrir Panel", command=self.abrir_panel)
        self.btn_abrir_panel.grid(row=3, column=0, padx=20, pady=10)
        self.btn_guardar_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Guardar Panel", command=self.guardar_panel)
        self.btn_guardar_panel.grid(row=4, column=0, padx=20, pady=10)
        self.btn_borrar_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Borrar Panel", command=self.borrar_panel)
        self.btn_borrar_panel.grid(row=5, column=0, padx=20, pady=10)
        self.btn_annadir_al_panel = customtkinter.CTkButton(self.sidebar_frame, text ="Añadir al Panel", command=self.annadir_al_panel)
        self.btn_annadir_al_panel.grid(row=6, column=0, padx=20, pady=10)
        self.sidebar_frame.rowconfigure(7, weight=10)
        self.btn_ajustes = customtkinter.CTkButton(self.sidebar_frame, text ="Ajustes", command= lambda : self.show_message("Función no implementada"))
        self.btn_ajustes.grid(row=8, column=0, padx=20, pady=10, sticky="s")
        self.btn_salir = customtkinter.CTkButton(self.sidebar_frame, text ="Salir", command= lambda : self.destroy())
        self.btn_salir.grid(row=9, column=0, padx=20, pady=10, sticky="s")

        # Competiciones
        self.competiciones_frame = customtkinter.CTkFrame(self, width=300, corner_radius=10)
        self.competiciones_frame.grid(row=0, column=1, rowspan= 4, sticky="nsw", padx=10, pady=10)
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
        self.competiciones_frame.rowconfigure(3, weight=1)
        self.btn_exportar_partidos = customtkinter.CTkButton(self.competiciones_frame, text="Exportar Partidos",
                                                             command=self.exportar_partidos, state="normal")
        self.btn_exportar_partidos.grid(row=5, column=0,columnspan = 2,  padx=20, pady=10, sticky="s")
        self.btn_exportar_competiciones = customtkinter.CTkButton(self.competiciones_frame, text="Exportar Competiciones",
                                                                  command=self.exportar_competiciones, state="normal")
        self.btn_exportar_competiciones.grid(row=6, column=0,columnspan = 2,  padx=20, pady=10, sticky="s")

        # Competicion
        self.competicion_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.competicion_frame.grid(row=0, column=2, rowspan= 4, sticky="nsew", padx=(0,10), pady=10)
        self.competicion_frame.grid_propagate(True)
        self.competicion_label = customtkinter.CTkLabel(self.competicion_frame, text="Competición #",
                                                        font=customtkinter.CTkFont(size=20, weight="bold"), anchor="center")
        self.competicion_label.pack(padx=10, pady=(20, 0))
        self.tabview_competicion = customtkinter.CTkTabview(self.competicion_frame, state="disabled")
        self.tabview_competicion.pack(expand=True, fill="both", padx=10, pady=10)
        self.tabview_competicion.add("Configuración")
        self.tabview_competicion.add("General")
        self.tabview_competicion.add("Equipos")

        # Competicion/Enlaces

        self.enlaces_frame = customtkinter.CTkFrame(self.tabview_competicion.tab("Configuración"), corner_radius=10)
        self.enlaces_frame.pack(expand=True, fill="both")
        self.enlaces_frame.grid_propagate(True)
        self.enlaces_lista = CTkListbox(self.enlaces_frame,  width=300, border_width=0, command=self.on_enlaces_lista_selected, justify="right")
        self.enlaces_lista.grid(row=0, column=0, padx=10, pady=10, rowspan = 4, sticky="nsew")
        self.btn_enlaces_actualizar = customtkinter.CTkButton(self.enlaces_frame, text="Actualizar Enlaces", command=self.actualizar, state="disabled")
        self.btn_enlaces_actualizar.grid(row=0, column=1, padx=(10,0), pady=0, sticky="s")
        self.enlaces_label_ultima_actualizacion = customtkinter.CTkLabel(self.enlaces_frame, text="Última actualización:\n", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.enlaces_label_ultima_actualizacion.grid(row=1, column=1, padx=(10,0), pady=10, sticky="n")
        self.btn_enlaces_borrar = customtkinter.CTkButton(self.enlaces_frame, text="Borrar Enlace", command=self.borrar_enlace, state="disabled")
        self.btn_enlaces_borrar.grid(row=3, column=1, padx=(10,0), pady=20, sticky="s")
        self.btn_enlaces_annadir = customtkinter.CTkButton(self.enlaces_frame, text="Añadir Enlace", command=self.annadir_enlace, state="disabled")
        self.btn_enlaces_annadir.grid(row=4, column=1, padx=(10,0), pady=20, sticky="s")
        self.btn_modificar_enlace = customtkinter.CTkButton(self.enlaces_frame, text="Modificar Enlace", command=self.modificar_enlace, state="disabled")
        self.btn_modificar_enlace.grid(row=5, column=1, padx=(10,0), pady=20, sticky="s")
        self.enlaces_frame.rowconfigure(0, weight=1)
        self.enlaces_frame.rowconfigure(1, weight=1)
        self.enlaces_frame.rowconfigure(2, weight=10)
        self.enlaces_frame.rowconfigure(3, weight=1)
        self.enlaces_frame.columnconfigure(0, weight=1)
        self.enlaces_frame.columnconfigure(1, weight=1)

        # Competiciones/General
        self.general_segmented_button_var = tk.StringVar(value="Visualizando")
        self.general_tabview = customtkinter.CTkTabview(self.tabview_competicion.tab("General"))
        self.general_tabview.pack(expand=True, fill="both", padx=0, pady=(0,10))
        self.general_tabview.add("Estadísticas")
        self.general_tabview.add("Clasificación")
        self.general_tabview.add("Gráficos")

        # Competiciones/General/Estadísticas
        self.estadisticas_frame = customtkinter.CTkFrame(self.general_tabview.tab("Estadísticas"), corner_radius=10)
        self.estadisticas_frame.pack(expand=True, fill="both")
        self.estadisticas_frame.grid_propagate(True)
        self.estadisticas_text = customtkinter.CTkTextbox(self.estadisticas_frame, border_width=0)
        self.estadisticas_text.insert("end", "Visualización de Estadísticas")
        self.estadisticas_text.configure(state="disabled")
        self.estadisticas_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Competiciones/General/Clasificación
        self.clasificacion_frame = customtkinter.CTkFrame(self.general_tabview.tab("Clasificación"), corner_radius=10)
        self.clasificacion_frame.pack(expand=True, fill="both")
        self.clasificacion_frame.grid_propagate(True)
        # Add treeview
        self.clasificacion_treeview = ttk.Treeview(self.clasificacion_frame)
        self.clasificacion_treeview.pack(expand=True, fill="both", padx=10, pady=10)
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
                         font = (None, 14))
        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font = (None, 16)

                        )
        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Configure treeview
        self.clasificacion_treeview["columns"] = ('nombre', 'temporada', 'gf', 'gc', 'victorias', 'derrotas', 'empates')
        self.clasificacion_treeview.column("#0", width=0, stretch="no")
        self.clasificacion_treeview.column("nombre", anchor="center", width=200)
        self.clasificacion_treeview.column("temporada", anchor="center", width=50)
        self.clasificacion_treeview.column("gf", anchor="center", width=25)
        self.clasificacion_treeview.column("gc", anchor="center", width=25)
        self.clasificacion_treeview.column("victorias", anchor="center", width=25)
        self.clasificacion_treeview.column("derrotas", anchor="center", width=25)
        self.clasificacion_treeview.column("empates", anchor="center", width=25)
        self.clasificacion_treeview.heading("nombre", text="Equipo", anchor="center")
        self.clasificacion_treeview.heading("temporada", text="Temp", anchor="center")
        self.clasificacion_treeview.heading("gf", text="GF", anchor="center")
        self.clasificacion_treeview.heading("gc", text="GC", anchor="center")
        self.clasificacion_treeview.heading("victorias", text="V", anchor="center")
        self.clasificacion_treeview.heading("derrotas", text="D", anchor="center")
        self.clasificacion_treeview.heading("empates", text="E", anchor="center")

        # Competiciones/General/Gráficos
        self.graficos_frame = customtkinter.CTkFrame(self.general_tabview.tab("Gráficos"), corner_radius=10)
        self.graficos_frame.pack(expand=True, fill="both")
        self.graficos_frame.grid_propagate(True)
        self.graficos_text = customtkinter.CTkTextbox(self.graficos_frame, border_width=0)
        self.graficos_text.insert("end", "Visualización de Gráficos")
        self.graficos_text.configure(state="disabled")
        self.graficos_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Competiciones/Equipos
        self.equipos_frame = customtkinter.CTkFrame(self.tabview_competicion.tab("Equipos"), corner_radius=10)
        self.equipos_frame.pack(expand=True, fill="both")
        self.equipos_frame.grid_propagate(True)
        self.equipos_buscador_combobox = customtkinter.CTkComboBox(self.equipos_frame, border_width=0, command=self.seleccionar_equipos)
        self.equipos_buscador_combobox.pack(fill="both", padx=10, pady=10)
        self.equipos_buscador_combobox.configure(values=["Equipo 1", "Equipo 2", "Equipo 3"])

        self.equipos_tabview = customtkinter.CTkTabview(self.equipos_frame)
        self.equipos_tabview.pack(expand=True, fill="both", padx=10, pady=(0,10))
        self.equipos_tabview.add("Estadísticas")
        self.equipos_tabview.add("Gráficos")




        # Competiciones/Equipos/Estadísticas
        self.equipos_estadisticas_frame = customtkinter.CTkFrame(self.equipos_tabview.tab("Estadísticas"), corner_radius=10)
        self.equipos_estadisticas_frame.pack(expand=True, fill="both")
        self.equipos_estadisticas_frame.grid_propagate(True)
        self.equipos_estadisticas_text = customtkinter.CTkTextbox(self.equipos_estadisticas_frame, border_width=0)
        self.equipos_estadisticas_text.insert("end", "Visualización de Estadísticas")
        self.equipos_estadisticas_text.configure(state="disabled")
        self.equipos_estadisticas_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Competiciones/Equipos/Gráficos
        self.equipos_graficos_frame = customtkinter.CTkFrame(self.equipos_tabview.tab("Gráficos"), corner_radius=10)
        self.equipos_graficos_frame.pack(expand=True, fill="both")
        self.equipos_graficos_frame.grid_propagate(True)
        self.equipos_graficos_text = customtkinter.CTkTextbox(self.equipos_graficos_frame, border_width=0)
        self.equipos_graficos_text.insert("end", "Visualización de Gráficos")
        self.equipos_graficos_text.configure(state="disabled")
        self.equipos_graficos_text.pack(expand=True, fill="both", padx=10, pady=10)


        self.cargar_estado()
        self.after(0, lambda: self.state('zoomed')) # Bug en zoomed state, hay que hacerlo así

        # Bindings
        self.competiciones_lista.bind("<<ListboxSelect>>", self.on_competiciones_lista_selected)
        self.equipos_buscador_combobox.bind("<KeyRelease>", self.actualizar_filtro)
        self.clasificacion_treeview.bind("<Double-Button-1>", self.on_clasificacion_treeview_double_click)
        self.competicion_label.bind("<Button-1>", self.modificar_nombre_competicion)

    def actualizar_filtro(self, event):
        filtro = self.equipos_buscador_combobox.get().lower()
        equipos = self.panel.get_competicion(self.competicion_label.cget("text")).get_equipos()
        nombres_equipos = []
        for equipo in equipos:
            if filtro in equipo.nombre.lower():
                nombres_equipos.append(equipo.nombre)
        self.equipos_buscador_combobox.configure(values=nombres_equipos)
        self.equipos_buscador_combobox.set(filtro)

    def on_clasificacion_treeview_double_click(self, event):
        #open tabview equipos
        self.tabview_competicion.set("Equipos")
        #select equipo
        item = self.clasificacion_treeview.selection()[0]
        nombre_equipo = self.clasificacion_treeview.item(item, "values")[0]
        self.equipos_buscador_combobox.set(nombre_equipo)
        self.seleccionar_equipos(nombre_equipo)




    def on_competiciones_lista_selected(self, event):
        if event is not None and event != self.competicion_label.cget("text"):
            self.elegir_competicion()
            if self.enlaces_lista.curselection() is not None: # If there is a selected item
                self.enlaces_lista.deactivate(self.enlaces_lista.curselection())
    def on_enlaces_lista_selected(self, event):

        if event is not None:

            print("Enlace: " + event)
            self.btn_enlaces_borrar.configure(state="normal")
            self.btn_enlaces_annadir.configure(state="normal")
            self.btn_modificar_enlace.configure(state="normal")




    def sidebar_button_event(self):
        print("Sidebar button pressed")

    def actualizar(self):

        hilo_actualizar = threading.Thread(target=self.actualizar_thread)
        hilo_actualizar.start()
        self.loading_screen()
        self.loading_window.update()




    def actualizar_thread(self):
        self.panel.actualizar_competicion(self.competicion_label.cget("text"))
        print("Actualizando enlaces...")
        self.enlaces_label_ultima_actualizacion.configure(
            text=f"Última actualización:\n{self.panel.get_competicion(self.competicion_label.cget('text')).ultima_actualizacion}")
        self.abrir_competicion(self.competicion_label.cget("text"))
        self.loading_window.destroy()





    def loading_screen(self):
        # Create tokLevelWindow
        self.loading_window = customtkinter.CTkToplevel(self)
        self.loading_window.title("Cargando")

        progressbar = customtkinter.CTkProgressBar(self.loading_window, orientation="horizontal")
        progressbar.configure(mode="indeterminate")
        progressbar.start()
        progressbar.pack(padx=20, pady=20)
        texto = customtkinter.CTkLabel(self.loading_window, text="Actualizando enlaces...")
        texto.pack(padx=20, pady=20)
        self.loading_window.attributes("-topmost", True)

    def elegir_competicion(self):
        # Check if there is a competition selected
        if self.competiciones_lista.curselection() == ():
            return
        # Get the competition selected
        competicion = self.competiciones_lista.get(self.competiciones_lista.curselection())
        # Update the competition label
        self.abrir_competicion(competicion)
        pass

    def borrar_panel(self):
        self.panel.eliminar_competiciones()
        self.actualizar_competicion_listview()
        self.abrir_competicion(None)
    def abrir_competicion(self, nombre_competicion):
        if len(self.panel.get_competiciones()) == 0:
            self.btn_exportar_partidos.configure(state="disabled")
            self.btn_exportar_competiciones.configure(state="disabled")
        else:
            self.btn_exportar_competiciones.configure(state="normal")
            self.btn_exportar_partidos.configure(state="normal")

        if nombre_competicion is None:
            self.tabview_competicion.configure(state="disabled")
            self.competicion_label.configure(text="Competición #")
            self.tabview_competicion.set("Configuración")
            self.enlaces_lista.delete(0, "end")
            self.btn_enlaces_actualizar.configure(state="disabled")
            self.btn_enlaces_borrar.configure(state="disabled")
            self.btn_enlaces_annadir.configure(state="disabled")
            self.btn_modificar_enlace.configure(state="disabled")
            self.enlaces_label_ultima_actualizacion.configure(text=f"Última actualización:\n")
            return

        if self.competicion_label.cget("text") == "Competición #":
            self.tabview_competicion.configure(state="normal")
        self.competicion_label.configure(text=nombre_competicion)
        self.tabview_competicion.set("Configuración")
        self.enlaces_lista.delete(0, "end")

        enlaces = self.panel.get_competicion(nombre_competicion).enlaces

        for enlace in enlaces:
            self.enlaces_lista.insert("end", enlace)


        # Tab Configuración
        self.enlaces_label_ultima_actualizacion.configure(text=f"Última actualización:\n{self.get_competicion(nombre_competicion).ultima_actualizacion}")
        self.tabview_competicion.set("Configuración")
        self.btn_enlaces_actualizar.configure(state="normal")
        self.btn_enlaces_borrar.configure(state="disabled")
        self.btn_modificar_enlace.configure(state="disabled")

        self.btn_enlaces_annadir.configure(state="normal")

        # Tab General
        # Tab General - Clasificación
        clasificacion_df = self.panel.get_competicion(nombre_competicion).get_clasificacion()
        self.clasificacion_treeview.delete(*self.clasificacion_treeview.get_children())
        for index, row in clasificacion_df.iterrows():
            self.clasificacion_treeview.insert(parent="", index="end", iid=index, text="", values=(row["nombre"], row["temporada"], row["gf"], row["gc"], row["victorias"], row["derrotas"], row["empates"]))

        # Tab Equipos
        # Cargar listado de equipos
        listado_equipos = self.panel.get_competicion(nombre_competicion).get_equipos()
        nombres_equipos = []
        for equipo in listado_equipos:
            nombres_equipos.append(equipo.nombre)
        self.equipos_buscador_combobox.configure(values=nombres_equipos)
        self.equipos_buscador_combobox.set("")
        self.equipos_estadisticas_text.configure(state="normal")
        self.equipos_estadisticas_text.delete("1.0", "end")
        self.equipos_estadisticas_text.insert("end", "Visualización de Estadísticas")
        self.equipos_estadisticas_text.configure(state="disabled")

        # TODO: En desarrollo
        estadisticas = self.panel.get_estadisticas_competicion(nombre_competicion)
        # Delete goles_ganadores, goles_perdedores, goles_locales, goles_visitantes
        del estadisticas["goles_ganadores"]
        del estadisticas["goles_perdedores"]
        del estadisticas["goles_por_partido"]
        self.estadisticas_text.configure(state="normal")
        self.estadisticas_text.delete("1.0", "end")
        for estadistica in estadisticas:
            self.estadisticas_text.insert("end", str(estadistica) + ": " + str(estadisticas[estadistica]))
            self.estadisticas_text.insert("end", "\n")
        self.estadisticas_text.configure(state="disabled")




        pass
    def annadir_competicion(self):
        # Create tokLevelWindow
        self.annadir_competicion_window = customtkinter.CTkToplevel(self)
        self.annadir_competicion_window.title("Añadir Competición")
        self.annadir_competicion_window.geometry(f"{300}x{150}")
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

    def get_competicion(self, nombre):
        return self.panel.get_competicion(nombre)
    def annadir_competicion_event(self):
        #TODO: Actualizar BBDD, no funciona
        print("Añadir competición")
        self.panel.add_competicion(gestor.Competicion(nombre=self.annadir_competicion_entry.get(), actualizar_al_iniciar=False, nombre_bd=self.panel.archivo_bd))
        self.actualizar_competicion_listview()
        self.abrir_competicion(self.annadir_competicion_entry.get())
        self.abrir_competicion(self.annadir_competicion_entry.get())
        self.annadir_competicion_window.destroy()
        pass

    def borrar_competicion(self):
        self.panel.eliminar_competicion(self.competicion_label.cget("text"))
        self.actualizar_competicion_listview()
        self.abrir_competicion(None)



    def actualizar_competicion_listview(self):
        self.competiciones_lista.delete(0, "end")
        competiciones = self.panel.get_competiciones()
        for competicion in competiciones:
            self.competiciones_lista.insert("end", competicion.nombre)
        pass

    def cargar_competicion(self):
        pass

    def cargar_panel(self, competiciones):
        self.panel = gestor.panel_from_json(competiciones)

        pass

    def abrir_panel(self):
        origen = filedialog.askopenfilename(initialdir=".", title="Abrir Panel",
                                                filetypes=(("DataBase", "*.db"), ("Todos los archivos", "*.*")))
        if origen == "" or origen is None:
             return
        try:
            shutil.copyfile(origen, PANEL_PATH)
        except:
            print("Error al abrir el panel")

        self.cargar_estado()
        print("Abrir panel")

    def annadir_al_panel(self):
        self.show_message("Función no implementada")

    def guardar_panel(self):
        destino = filedialog.asksaveasfilename(initialdir=".", title="Guardar Panel",
                                                filetypes=(("DataBase", "*.db"), ("Todos los archivos", "*.*")), defaultextension=".db")
        if destino == "" or destino is None:
             return
        try:
            shutil.copyfile(PANEL_PATH, destino)
        except:
            print("Error al guardar el panel")

    def show_message(self, message):
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
        message_button.pack(padx=20, pady=10)


    def seleccionar_equipos(self, nombre_equipo):
        competicion = self.get_competicion(self.competicion_label.cget("text"))
        equipo = competicion.get_equipo(nombre_equipo)
        estadisticas = competicion.get_estadisticas_equipo(equipo)
        del estadisticas["victorias"]
        del estadisticas["derrotas"]
        del estadisticas["empates"]
        del estadisticas["gf"]
        del estadisticas["gc"]
        self.equipos_estadisticas_text.configure(state="normal")
        self.equipos_estadisticas_text.delete("1.0", "end")
        for estadistica in estadisticas:
            self.equipos_estadisticas_text.insert("end", str(estadistica) + ": " + str(estadisticas[estadistica]))
            self.equipos_estadisticas_text.insert("end", "\n")
        self.equipos_estadisticas_text.configure(state="disabled")
        nombres_equipos = []
        for equipo in competicion.get_equipos():
            nombres_equipos.append(equipo.nombre)
        self.equipos_buscador_combobox.configure(values=nombres_equipos)


    def annadir_enlace(self):
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

    def annadir_enlace_event(self):
        enlace = self.annadir_enlace_entry.get()

        self.panel.annadir_enlace_a_competicion(self.competicion_label.cget("text"), enlace)
        self.panel.set_fecha_ultima_actualizacion(self.competicion_label.cget("text"), None)

        self.abrir_competicion(self.competicion_label.cget("text"))

        self.annadir_enlace_window.destroy()
    def borrar_enlace(self):
        enlace = self.enlaces_lista.get(self.enlaces_lista.curselection())
        self.panel.eliminar_enlace_a_competicion(self.competicion_label.cget("text"), enlace)
        self.panel.set_fecha_ultima_actualizacion(self.competicion_label.cget("text"), None)
        self.abrir_competicion(self.competicion_label.cget("text"))

    def modificar_enlace(self):
        #Open new window with entry
        self.modificar_enlace_window = customtkinter.CTkToplevel(self)
        self.modificar_enlace_window.title("Modificar Enlace")
        self.modificar_enlace_window.geometry(f"{300}x{150}")
        self.modificar_enlace_window.attributes("-topmost", True)
        self.modificar_enlace_window.resizable(False, False)
        # Create frame
        modificar_enlace_frame = customtkinter.CTkFrame(self.modificar_enlace_window, corner_radius=10)
        modificar_enlace_frame.pack(expand=True, fill="both")
        modificar_enlace_frame.grid_propagate(True)
        # Create label
        modificar_enlace_label = customtkinter.CTkLabel(modificar_enlace_frame, text="Enlace")
        modificar_enlace_label.pack(padx=20, pady=10)
        # Create entry
        self.modificar_enlace_entry = customtkinter.CTkEntry(modificar_enlace_frame, width=200, border_width=0)
        self.modificar_enlace_entry.pack(padx=10, pady=10)
        # Create button
        modificar_enlace_button = customtkinter.CTkButton(modificar_enlace_frame, text="Modificar", command=self.modificar_enlace_event)
        modificar_enlace_button.pack(padx=20, pady=10)

        # Set entry text
        enlace = self.enlaces_lista.get(self.enlaces_lista.curselection())
        self.modificar_enlace_entry.insert("end", enlace)

    def modificar_enlace_event(self):
        enlace = self.modificar_enlace_entry.get()
        enlace_viejo = self.enlaces_lista.get(self.enlaces_lista.curselection())
        self.panel.modificar_enlace_a_competicion(self.competicion_label.cget("text"), enlace_viejo, enlace)
        self.panel.set_fecha_ultima_actualizacion(self.competicion_label.cget("text"), None)
        self.abrir_competicion(self.competicion_label.cget("text"))
        self.modificar_enlace_window.destroy()

    def modificar_nombre_competicion(self, event):
        print("Modificar nombre competición")
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
        nombre = self.modificar_nombre_competicion_entry.get()
        self.panel.modificar_nombre_competicion(self.competicion_label.cget("text"), nombre)
        self.abrir_competicion(nombre)
        self.modificar_nombre_competicion_window.destroy()







    def cargar_estado(self):
        self.panel = gestor.panel_from_db(PANEL_PATH)
        self.actualizar_competicion_listview()

    def exportar_partidos(self):
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
    app.mainloop()

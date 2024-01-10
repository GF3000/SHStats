import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from clases import competicion
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from SH_Stats_back import funciones_auxiliares, analisis


class VentanaMain(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SH Stats")
        self.geometry("1000x400")

        if not os.path.exists("exports"):
            os.mkdir("exports")

        self.competiciones = []
        self.df_estadisticas = None
        self.df_partidos = None
        self.fuentes = {}

        self.cargar_estilos()
        self.cargar_menu_superior()
        self.cargar_widgets()
        self.cargar_configuracion()

        # Otras cosas
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def cargar_estilos(self):
        self.fuentes = {}
        try:
            with open("config/fonts.json", "r") as archivo:
                self.fuentes = json.load(archivo)
        except FileNotFoundError:
            print("No se ha encontrado el archivo fonts.json")
            self.fuentes = {"titulos": ("Arial", 20), "botones": ("Arial", 20), "textos": ("Arial", 10)}
        estilo = ttk.Style()
        estilo.configure("Title.TLabel", font=self.fuentes["titulos"])
        estilo_botones = ttk.Style()
        estilo_botones.configure("Boton.TButton", font=self.fuentes["botones"], padding=6, relief="flat")
        estilo_botones.configure("BotonAzul.TButton", font=self.fuentes["botones"], padding=6, relief="flat",
                                 foreground="blue", cursor="hand2")
        estilo_botones.configure("BotonRojo.TButton", font=self.fuentes["botones"], padding=6, relief="flat",
                                 foreground="red", cursor="hand2")
        estilo_botones.configure("BotonVerde.TButton", font=self.fuentes["botones"], padding=6, relief="flat",
                                 foreground="green", cursor="hand2")
        estilo_botones.configure("BotonPequeño.TButton", padding=6, relief="flat",
                                 background="white", foreground="blue", anchor="center", borderwidth=4,
                                 font=self.fuentes["textos"])

    def cargar_menu_superior(self):
        # Barra de menú
        self.barra_menu = tk.Menu(self)
        self.config(menu=self.barra_menu)

        # Menú Archivo
        menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        menu_archivo.add_command(label="Abrir", command=self.abrir_archivo)
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo)
        menu_archivo.add_command(label="Borrar competiciones", command=self.borrar_competiciones)
        menu_archivo.add_command(label="Añadir competiciones", command=self.annadir_competiciones)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salir)
        self.barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        # Menú Ayuda
        menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self.acerca_de)
        menu_ayuda.add_command(label="Ayuda", command=self.mostrar_ayuda)
        menu_ayuda.add_command(label="Enlances", command=self.mostrar_ayuda_enlaces)
        self.barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        # Menú Configuración
        menu_configuracion = tk.Menu(self.barra_menu, tearoff=0)
        menu_configuracion.add_command(label="Configurar Estadísticas",
                                       command=lambda: self.abrir_ventana_configuracion("Estadísticas",
                                                                                        "config/config_estadisticas.json"))
        menu_configuracion.add_command(label="Configurar Partidos",
                                       command=lambda: self.abrir_ventana_configuracion("Partidos",
                                                                                        "config/config_partidos.json"))
        menu_configuracion.add_command(label="Configurar Gráficos",
                                       command=lambda: self.mostrar_mensaje(f"Configurar Gráficos"))
        self.barra_menu.add_cascade(label="Configuración", menu=menu_configuracion)

    def cargar_widgets(self):
        # Columna de Enlaces
        self.label_enlaces = ttk.Label(self, text="Competiciones", style="Title.TLabel")
        self.label_enlaces.grid(row=0, column=0, padx=10, pady=3)
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, font=self.fuentes["textos"])
        self.listbox.grid(row=2, rowspan=1, column=0, padx=10, pady=10, sticky="nsew")

        # Botón para añadir Liga
        self.boton_anadir_competicion = ttk.Button(self, text="Añadir Competición", command=self.anadir_liga,
                                                   style="Boton.TButton")
        self.boton_anadir_competicion.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Columna de Tabla
        self.label_tabla = ttk.Label(self, text="Estadísticas", style="Title.TLabel")
        self.label_tabla.grid(row=0, column=1, padx=10, pady=3)

        self.boton_ver_estadisitcas = ttk.Button(self, text=f"Ver Estadísticas",
                           command=lambda: self.mostrar_df_estadisticas(), style="Boton.TButton")
        self.boton_ver_estadisitcas.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.boton_exportar_estadisticas = ttk.Button(self, text=f"Exportar Estadísticas",
                           command=lambda: self.abrir_ventana_exportar_estadisticas(), style="Boton.TButton")
        self.boton_exportar_estadisticas.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # Columna de Partidos
        self.label_partidos = ttk.Label(self, text="Partidos", style="Title.TLabel")
        self.label_partidos.grid(row=0, column=2, padx=10, pady=3)
        self.boton_ver_partidos = ttk.Button(self, text=f"Ver Partidos",
                           command=lambda: self.mostrar_partidos(), style="Boton.TButton")
        self.boton_ver_partidos.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.boton_exportar_partidos = ttk.Button(self, text=f"Exportar Partidos",
                           command=lambda: self.abrir_ventana_exportar_partidos(), style="Boton.TButton")
        self.boton_exportar_partidos.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

        # Columna de Gráficos
        self.label_graficos = ttk.Label(self, text="Gráficos", style="Title.TLabel")
        self.label_graficos.grid(row=0, column=3, padx=10, pady=3)

        boton = ttk.Button(self, text=f"Ver Gráficos",
                           command=lambda: self.mostrar_graficos(), style="Boton.TButton", state=tk.DISABLED)
        boton.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Exportar Gráficos",
                           command=lambda: self.mostrar_mensaje(f"Exportar Gráficos"), style="Boton.TButton", state=tk.DISABLED)
        boton.grid(row=2, column=3, padx=10, pady=10, sticky="nsew")

    def on_select(self, event):
        # display element selected on list
        try:
            index = self.listbox.curselection()[0]
            self.mostrar_segunda_ventana(self.competiciones[index])
        except IndexError:
            pass

    def abrir_ventana_configuracion(self, nombre=None, archivo=None):
        # Create a new window
        ventana_configuracion = VentanaConfiguracion(self, nombre, archivo)
        self.df_estadisticas = None
        self.df_partidos = None

    def borrar_competiciones(self):
        self.competiciones = []
        self.actualizar_listbox()
        self.guardar_configuracion()
        self.cargar_configuracion()
        self.df_estadisticas = None
        self.df_partidos = None

    def annadir_competiciones(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivo SHStats", "*.shs"), ("Todos los archivos", "*.*")])
        if filepath:
            with open(filepath, "r") as archivo:
                nuevas_ligas = json.load(archivo)
                nuevas_ligas = nuevas_ligas.get("ligas", [])
                for liga in nuevas_ligas:
                    self.competiciones.append(competicion(nombre=liga["nombre"], enlaces=liga["enlaces"]))
            self.guardar_configuracion()
            self.actualizar_listbox()
            self.df_estadisticas = None
            self.df_partidos = None

    def abrir_archivo(self):
        # Agrega la lógica para abrir un archivo
        file_path = filedialog.askopenfilename(filetypes=[("Archivo SHStats", "*.shs"), ("Todos los archivos", "*.*")])
        if file_path:
            # Agrega la lógica para abrir el archivo seleccionado
            with open(file_path, "r") as archivo:
                # delete ligas.json content

                with open("config/ligas.shs", "w") as ligas:
                    ligas.write(archivo.read())
            self.cargar_configuracion()
            self.actualizar_listbox()

    def guardar_archivo(self):
        # Abre un cuadro de diálogo para elegir la ubicación de guardado
        file_path = filedialog.asksaveasfilename(defaultextension=".shs",
                                                 filetypes=[("Archivo SHStats", "*.shs"),
                                                            ("Todos los archivos", "*.*")])
        if file_path:
            # Agrega la lógica para guardar el archivo en la ubicación seleccionada
            with open(file_path, "w") as archivo:
                # Copy content from ligas.json to the new file
                with open("config/ligas.shs", "r") as ligas:
                    archivo.write(ligas.read())

    def salir(self):
        self.destroy()

    def acerca_de(self):
        try:
            with open("config/about.txt", "r", encoding="utf-8") as archivo:
                contenido = archivo.read()

            # Crear una ventana emergente para mostrar el contenido
            ventana_acerca_de = tk.Toplevel(self)
            ventana_acerca_de.title("Acerca de")

            # Etiqueta para mostrar el contenido
            etiqueta_contenido = ttk.Label(ventana_acerca_de, text=contenido, wraplength=400, justify="left",
                                           font=self.fuentes["textos"])
            etiqueta_contenido.pack(padx=20, pady=20)

        except FileNotFoundError:
            # Manejar el caso en el que el archivo no existe
            tk.messagebox.showerror("Error", "El archivo 'config/about.txt' no se encuentra.")

    def mostrar_ayuda(self):
        try:
            with open("config/help.txt", "r", encoding="utf-8") as archivo:
                contenido = archivo.read()

            # Crear una ventana emergente para mostrar el contenido
            ventana_ayuda = tk.Toplevel(self)
            ventana_ayuda.title("Ayuda")

            # Etiqueta para mostrar el contenido
            etiqueta_contenido = ttk.Label(ventana_ayuda, text=contenido, wraplength=400, justify="left",
                                           font=self.fuentes["textos"])
            etiqueta_contenido.pack(padx=20, pady=20)
        except FileNotFoundError:
            # Manejar el caso en el que el archivo no existe
            tk.messagebox.showerror("Error", "El archivo 'config/help.txt' no se encuentra.")

    def mostrar_ayuda_enlaces(self):
        try:
            with open("config/help_enlaces.txt", "r", encoding="utf-8") as archivo:
                contenido = archivo.read()

            # Crear una ventana emergente para mostrar el contenido
            ventana_ayuda = tk.Toplevel(self)
            ventana_ayuda.title("Ayuda")

            # Etiqueta para mostrar el contenido
            etiqueta_contenido = ttk.Label(ventana_ayuda, text=contenido, wraplength=400, justify="left",
                                           font=self.fuentes["textos"])
            etiqueta_contenido.pack(padx=20, pady=20)
        except FileNotFoundError:
            # Manejar el caso en el que el archivo no existe
            tk.messagebox.showerror("Error", "El archivo 'config/help_enlaces.txt' no se encuentra.")
    def mostrar_graficos(self):
        if self.df_estadisticas is None:
            self.df_estadisticas = self.get_df_estadisticas()
        if self.df_estadisticas is None:
            return
        plt.bar(self.df_estadisticas["nombre"], self.df_estadisticas["avg_goles"], color="blue")
        plt.title("Goles por partido")
        plt.show()
        plt.bar(self.df_estadisticas["nombre"], self.df_estadisticas["avg_DIF_total"], color="blue")
        plt.title("Diferencia de goles por partido")
        plt.show()
        # plt.bar(self.df["nombre"], self.df["avg_GF_en_victorias"], color = "blue")
        # plt.bar(self.df["nombre"], self.df["avg_GC_en_victorias"], color = "red")
        # plt.title("Goles en victorias")
        # plt.show()

    def mostrar_partidos(self):
        if self.df_partidos is None:
            self.df_partidos = self.get_df_partidos()
        if self.df_partidos is None:
            return

        ventana_partidos = tk.Toplevel(self)
        ventana_partidos.title("Ventana de Partidos")
        # Crear un widget tk.Treeview para mostrar el DataFrame en la nueva ventana
        tree = ttk.Treeview(ventana_partidos)
        tree["columns"] = list(self.df_partidos.columns)
        # tree.heading("#0", text="Índice")
        for col in self.df_partidos.columns:
            tree.heading(col, text=col)

        # Agregar filas al tk.Treeview
        for index, row in self.df_partidos.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(padx=10, pady=10)

    def abrir_ventana_exportar_partidos(self):
        if self.df_partidos is None:
            self.df_partidos = self.get_df_partidos()
        if self.df_partidos is None:
            return
        ventana_exportar = ExportarVentana(self.df_partidos)

    def abrir_ventana_exportar_estadisticas(self):
        if self.df_estadisticas is None:
            self.df_estadisticas = self.get_df_estadisticas()
        if self.df_estadisticas is None:
            return
        ventana_exportar = ExportarVentana(self.df_estadisticas)

    def mostrar_segunda_ventana(self, liga):
        segunda_ventana = VentanaCompeticion(self, liga)

    def borrar_boton_liga(self, liga):
        # Buscar el botón que corresponde a la liga usando index
        if liga in self.competiciones:
            self.competiciones.remove(liga)
            self.actualizar_listbox()

    def get_df_partidos(self):
        urls = []
        if self.df_partidos is None:
            for liga in self.competiciones:
                urls.extend(liga.enlaces)
            self.df_partidos = analisis.get_partidos(urls)
        if self.df_partidos is None:
            return

        try:
            with open("config/config_partidos.json", "r") as archivo:
                configuracion = json.load(archivo)
            print(configuracion)
            if configuracion["Columna diferencia"] == True:
                columna = abs(self.df_partidos["GL"] - self.df_partidos["GV"])
                self.df_partidos.insert(4, "DIF", columna)

            if configuracion["Columna goles totales"] == True:
                columna = self.df_partidos["GL"] + self.df_partidos["GV"]
                self.df_partidos.insert(5, "GT", columna)

            if configuracion["Columna fecha"] == False:
                self.df_partidos = self.df_partidos.drop(columns=["Fecha"])
            return self.df_partidos
        except Exception as e:
            messagebox.showerror("Error", "Error al cargar la configuración personalizada de partidos.")
            print(e)
            return None

    def get_df_estadisticas(self):
        # Hacemos la tarea
        iter_competicion = None
        try:

            ligas_y_enlaces = {}
            with open("config/config_estadisticas.json", "r") as archivo:
                configuracion = json.load(archivo)
            if not configuracion["Separar por competiciones"]:
                ligas_y_enlaces["Competicion"] = []
                for iter_competicion in self.competiciones:
                    ligas_y_enlaces["Competicion"].extend(iter_competicion.enlaces)
            else:
                for iter_competicion in self.competiciones:
                    ligas_y_enlaces[iter_competicion.nombre] = iter_competicion.enlaces
            self.df_estadisticas = analisis.comparar_ligas(ligas_y_enlaces)
            if configuracion["Separar por competiciones"] == False:
                self.df_estadisticas = self.df_estadisticas.drop(columns=["nombre", "federacion", "liga", "temporada"])
            return self.df_estadisticas
        except Exception as e:
            if len(self.competiciones) == 0:
                messagebox.showerror("Error", "No hay ligas para comparar.\nAñade ligas para poder compararlas.")
            else:
                if iter_competicion is not None:
                    messagebox.showerror("Error",
                                         f"Ha ocurrido un error al intentar obtener las estadísticas"
                                         f" de \"{iter_competicion.nombre}\"."
                                         f"\nVerifica que las urls sean correctas.")
                else:
                    messagebox.showerror("Error",
                                         "Ha ocurrido un error al intentar obtener las estadísticas.\nVerifica que las urls sean correctas.")

            print(e)
            return None

    def mostrar_df_estadisticas(self):
        if self.df_estadisticas is None:
            self.get_df_estadisticas()
        if self.df_estadisticas is None:
            return

        ventana_dataframe = tk.Toplevel(self)
        ventana_dataframe.title("Ventana del DataFrame")

        # Crear un widget tk.Treeview para mostrar el DataFrame en la nueva ventana
        tree = ttk.Treeview(ventana_dataframe)
        tree["columns"] = list(self.df_estadisticas.columns)
        # tree.heading("#0", text="Índice")
        for col in self.df_estadisticas.columns:
            tree.heading(col, text=col)

        # Agregar filas al tk.Treeview
        for index, row in self.df_estadisticas.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(padx=10, pady=10)

    def anadir_liga(self):
        nueva_liga = competicion()
        self.mostrar_segunda_ventana(nueva_liga)

    def anadir_boton_liga(self, liga, index=None):
        estilo_boton = ttk.Style()
        estilo_boton.configure("BotonVerde.TButton", padding=6, relief="flat",
                               background="white", foreground="green", anchor="center", borderwidth=4,
                               font=self.fuentes["textos"])
        boton = ttk.Button(self, text=liga.nombre, command=lambda: self.mostrar_segunda_ventana(liga),
                           style="BotonPequeño.TButton")
        if index != None:
            boton.grid(row=index + 2, column=0, padx=10, pady=10, sticky="nsew")
        else:
            boton.grid(row=len(self.competiciones) + 1, column=0, padx=10, pady=10, sticky="nsew")

    def mostrar_mensaje(self, mensaje):
        mensaje = mensaje + "\nFunción no implementada."
        messagebox.showinfo("Mensaje", mensaje)

    def guardar_configuracion(self):
        # Guardar la configuración en un archivo JSON
        configuracion = {"ligas": [{"nombre": liga.nombre, "index": liga.index, "enlaces": liga.enlaces} for liga in
                                   self.competiciones]}
        with open("config/ligas.shs", "w") as archivo:
            json.dump(configuracion, archivo)

    def cargar_configuracion(self):
        try:
            # Cargar la configuración desde el archivo JSON
            with open("config/ligas.shs", "r") as archivo:
                configuracion = json.load(archivo)
                ligas = configuracion.get("ligas", [])
                if len(ligas) == 0:
                    estado = tk.DISABLED

                else:
                    estado = tk.NORMAL
                self.boton_ver_partidos.config(state=estado)
                self.boton_ver_estadisitcas.config(state=estado)
                self.boton_exportar_partidos.config(state=estado)
                self.boton_exportar_estadisticas.config(state=estado)


                self.competiciones = [competicion(nombre=liga["nombre"], enlaces=liga["enlaces"]) for liga in ligas]
                self.actualizar_listbox()

        except FileNotFoundError:
            # Si el archivo no existe, no hay configuración para cargar
            self.boton_ver_partidos.config(state=tk.DISABLED)
            self.boton_ver_estadisitcas.config(state=tk.DISABLED)
            self.boton_exportar_partidos.config(state=tk.DISABLED)
            self.boton_exportar_estadisticas.config(state=tk.DISABLED)
            pass

    def actualizar_listbox(self):
        self.listbox.delete(0, tk.END)
        self.df_estadisticas = None
        self.df_partidos = None
        if len(self.competiciones) == 0:
            self.listbox.insert(tk.END, "No hay competiones para mostrar")
        else:
            self.listbox.delete(0, tk.END)
            for liga in self.competiciones:
                self.listbox.insert(tk.END, liga.nombre)


class VentanaCompeticion(tk.Toplevel):
    def __init__(self, parent, liga, fonts=None):
        super().__init__(parent)

        self.title(f"Liga: {liga.nombre}")
        self.geometry("750x400")
        self.liga = liga
        self.df = None
        self.parent = parent

        self.cargar_widgets()
        self.actualizar_botones_enlaces()

        self.listbox_enlaces.bind("<<ListboxSelect>>", self.on_select)
        self.entry_nombre.bind("<KeyRelease>", lambda event: self.actualizar_botones_enlaces())

        # Al cerrar
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.parent.cargar_configuracion()
        self.destroy()
    def cargar_widgets(self):
        # Columna 1
        self.label_col1 = ttk.Label(self, text="Links", style="Title.TLabel")
        self.label_col1.grid(row=0, column=0, padx=10, pady=10)
        # Botón para añadir Liga
        self.boton_anadir_enlace = ttk.Button(self, text="Añadir Enlace", command=self.anadir_enlace,
                                              style="Boton.TButton")
        self.boton_anadir_enlace.grid(row=1, column=0, padx=10, pady=10)
        self.listbox_enlaces = tk.Listbox(self, font=self.parent.fuentes["textos"])
        self.listbox_enlaces.grid(row=2, rowspan=2, column=0, padx=10, pady=10)

        self.boton_guardar = ttk.Button(self, text="Guardar", command=lambda: self.guardar_liga(self.liga),
                                        style="BotonVerde.TButton")
        self.boton_guardar.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Columna 2 - Nombre
        self.label_nombre = ttk.Label(self, text="Nombre", style="Title.TLabel")
        self.label_nombre.grid(row=0, column=1, padx=10, pady=10)

        self.entry_nombre = ttk.Entry(self, font=self.parent.fuentes["botones"])
        self.entry_nombre.insert(0, self.liga.nombre)
        self.entry_nombre.grid(row=1, column=1, padx=10, pady=10)

        # Columna 3
        self.label_col3 = ttk.Label(self, text="Opciones", style="Title.TLabel")
        self.label_col3.grid(row=0, column=2, padx=10, pady=10)

        self.boton_equipos = ttk.Button(self, text="Ver Equipos", command=lambda: self.cargar_ventana_equipos(),
                                        style="Boton.TButton")
        self.boton_equipos.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.boton_ver_tabla_partidos = ttk.Button(self, text=f"Ver Tabla Partidos",
                           command=lambda: self.mostrar_dataframe(),
                           style="Boton.TButton")
        self.boton_ver_tabla_partidos.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        self.boton_exportar_tabla_partidos = ttk.Button(self, text=f"Exportar Tabla Partidos",
                           command=lambda: self.exportar_dataframe(),
                           style="Boton.TButton")
        self.boton_exportar_tabla_partidos.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")
        self.boton_borrar = ttk.Button(self, text="Borrar", command=lambda: self.borrar_liga(self.liga),
                                       style="BotonRojo.TButton")
        self.boton_borrar.grid(row=4, column=2, padx=10, pady=10, sticky="nsew")

        # Columna 4

        self.boton_equipos = ttk.Button(self, text="Ver Equipos", command=lambda: self.cargar_ventana_equipos(),
                                        style="Boton.TButton")
        self.boton_equipos.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    def on_select(self, event):
        try:
            index = self.listbox_enlaces.curselection()[0]
            self.edicion_enlace(self.liga.enlaces[index])
        except IndexError:
            pass

    def get_dataframe(self):
        try:
            df = analisis.get_partidos(self.liga.enlaces)
            return df
        except Exception as e:
            print(e)
            messagebox.showerror("Error",
                                 "Ha ocurrido un error al intentar obtener los datos.\nVerifica que los enlaces sean correctos.")
            return None

    def mostrar_dataframe(self):
        if self.df is None:
            self.df = self.get_dataframe()
        if self.df is None:
            return
        ventana_dataframe = tk.Toplevel(self)
        ventana_dataframe.title("Tabla de Datos")
        ventana_dataframe.geometry("1000x400")
        tabla = ttk.Treeview(ventana_dataframe)
        tabla["columns"] = list(self.df.columns)
        tabla["show"] = "headings"
        for col in tabla["columns"]:
            tabla.heading(col, text=col)
        for index, row in self.df.iterrows():
            tabla.insert("", "end", values=list(row))
        tabla.pack(padx=10, pady=10)

    def exportar_dataframe(self):
        if self.df is None:
            self.df = self.get_dataframe()
        if self.df is None:
            return
        ventana_exportar = ExportarVentana(self.df)

    def exportar_a_excel(self, df, nombre_archivo, ventana):
        try:
            df.to_excel("exports/" + nombre_archivo + ".xlsx")
            print(f"Exportado a Excel: {nombre_archivo}")
            messagebox.showinfo("Exportado", "Los datos se han exportado correctamente en la carpeta exports.")
        except Exception as e:
            print(e)
            messagebox.showerror("Error",
                                 "Ha ocurrido un error al intentar exportar los datos.\nVerifica que el nombre del archivo sea correcto.")
        ventana.destroy()

    def exportar_a_csv(self, df, nombre_archivo):
        try:
            df.to_csv("exports/" + nombre_archivo + ".csv")
            print(f"Exportado a CSV: {nombre_archivo}")
            messagebox.showinfo("Exportado", "Los datos se han exportado correctamente en la carpeta exports.")
        except Exception as e:
            print(e)
            messagebox.showerror("Error",
                                 "Ha ocurrido un error al intentar exportar los datos.\nVerifica que el nombre del archivo sea correcto.")

    def anadir_enlace(self):
        ventana_annadir_enlace = tk.Toplevel(self)
        ventana_annadir_enlace.title("Añadir Enlace")
        ttk.Label(ventana_annadir_enlace, text="Añadir Enlace:", style="Title.TLabel").pack(pady=5)
        entry_enlace = ttk.Entry(ventana_annadir_enlace, font=self.parent.fuentes["botones"], width=50)
        entry_enlace.pack(pady=5)

        def guardar_enlace():
            nuevo_enlace = entry_enlace.get()
            nuevo_enlace = funciones_auxiliares.convert_url(nuevo_enlace)
            self.liga.enlaces.append(nuevo_enlace)
            self.actualizar_botones_enlaces()
            ventana_annadir_enlace.destroy()

        btn_guardar = ttk.Button(ventana_annadir_enlace, text="Guardar", command=guardar_enlace,
                                 style="BotonVerde.TButton")
        btn_guardar.pack(pady=5)

    def edicion_enlace(self, enlace):
        enlace_en_uso = enlace
        # Crear una nueva ventana para la edición del enlace
        ventana_edicion = tk.Toplevel(self)
        ventana_edicion.title("Edición de Enlace")

        # Etiqueta y caja de texto para editar el enlace
        ttk.Label(ventana_edicion, text="Editar Enlace:", style="Title.TLabel").grid(row=0, column=0, columnspan=2,
                                                                                     padx=10, pady=10)
        entry_enlace = ttk.Entry(ventana_edicion, font=self.parent.fuentes["botones"], width=50)
        entry_enlace.insert(0, enlace)
        entry_enlace.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Función para guardar el enlace editado
        def guardar_enlace():
            nuevo_enlace = entry_enlace.get()
            nuevo_enlace = funciones_auxiliares.convert_url(nuevo_enlace)
            self.liga.enlaces[self.liga.enlaces.index(enlace)] = nuevo_enlace
            self.actualizar_botones_enlaces()
            ventana_edicion.destroy()

        # Botón para guardar el enlace
        btn_guardar = ttk.Button(ventana_edicion, text="Guardar", command=guardar_enlace, style="BotonVerde.TButton")
        btn_guardar.grid(row=2, column=0, padx=10, pady=10)

        # Botón para borrar el enlace
        btn_borrar = ttk.Button(ventana_edicion, text="Borrar",
                                command=lambda: self.borrar_enlace(enlace_en_uso, ventana_edicion),
                                style="BotonRojo.TButton")
        btn_borrar.grid(row=2, column=1, padx=10, pady=10)

    def borrar_enlace(self, enlace,
                      ventana_edicion):  # Aquí puedes realizar acciones para borrar el enlace, por ejemplo, actualizar tu lista de enlaces
        if enlace in self.liga.enlaces:
            self.liga.enlaces.remove(enlace)
            self.actualizar_botones_enlaces()
        ventana_edicion.destroy()

    def actualizar_botones_enlaces(self):
        self.df = None
        self.listbox_enlaces.delete(0, tk.END)
        if len(self.liga.enlaces) == 0:
            estado = tk.DISABLED
        else:
            estado = tk.NORMAL
        self.boton_equipos.config(state=estado)
        self.boton_ver_tabla_partidos.config(state=estado)
        self.boton_exportar_tabla_partidos.config(state=estado)

        if (self.entry_nombre.get() == ""):
            estado = tk.DISABLED
        else:
            estado = tk.NORMAL
        self.boton_guardar.config(state=estado)
        self.boton_borrar.config(state=estado)
        if len(self.liga.enlaces) == 0:
            self.listbox_enlaces.insert(tk.END, "No hay enlaces")
        else:
            self.listbox_enlaces.delete(0, tk.END)
            for enlace in self.liga.enlaces:
                if len(enlace) > 18:
                    nuevo_enlace = "..." + enlace[-15:]
                    self.listbox_enlaces.insert(tk.END, nuevo_enlace)
                else:
                    self.listbox_enlaces.insert(tk.END, enlace)

    def guardar_liga(self, liga):
        nombre_nuevo = self.entry_nombre.get()
        if nombre_nuevo:
            if liga not in self.parent.listado_competiciones:
                self.parent.listado_competiciones.append(liga)
            liga.nombre = nombre_nuevo
            self.parent.actualizar_listbox()
            self.parent.guardar_configuracion()  # Guarda la configuración al actualizar la liga
            self.parent.cargar_configuracion()
        self.destroy()

    def borrar_liga(self, liga):
        self.parent.borrar_boton_liga(liga)
        self.parent.guardar_configuracion()
        self.parent.cargar_configuracion()
        self.destroy()

    def mostrar_mensaje(self, mensaje):
        mensaje = mensaje + "\n (Esta función aún no está implementada)"
        messagebox.showinfo("Mensaje", mensaje)

    def cargar_ventana_equipos(self):
        ventana_equipos = VentanaEquipos(self.liga)
        ventana_equipos.mainloop()


class VentanaEquipos(tk.Toplevel):

    def __init__(self, competiciones):
        tk.Toplevel.__init__(self)
        self.competiciones = competiciones
        self.title("Equipos")
        self.geometry("1200x800")
        self.resizable(True, True)
        self.config(bg="white")
        self.equipos = None
        self.nombres_equipos = None
        self.partidos = None
        self.df_partidos = None

        try:
            self.cargar_equipos()
        except Exception as e:
            self.destroy()
            messagebox.showerror("Error",
                                 "Ha ocurrido un error al intentar obtener los datos.\nVerifica que los enlaces sean correctos.")
            print(e)
            return
        self.crear_widgets()

    def crear_widgets(self):

        # Variable de control para el menú desplegable
        self.seleccion = tk.StringVar()

        # Menú desplegable
        self.menu_desplegable = ttk.Combobox(self, textvariable=self.seleccion, values=self.nombres_equipos,
                                             state="normal", width=50, font=self.master.fuentes["botones"])
        self.menu_desplegable.grid(row=0, column=0,columnspan = 2,  padx=10, pady=10, sticky="w")

        self.menu_desplegable.bind('<KeyRelease>', self.actualizar_filtro)
        self.menu_desplegable.bind('<<ComboboxSelected>>', self.mostrar_seleccion)
        df_clasificacion = analisis.get_clasificacion(self.partidos)
        self.mostrar_clasificacion(df_clasificacion)

        # Select the first item
        self.menu_desplegable.current(0)
        self.mostrar_seleccion()

    def mostrar_seleccion(self, event=None):
        # Mostrar la selección en un messagebox
        seleccion = self.seleccion.get()
        equipo = self.equipos.buscar_por_nombre(seleccion)
        df = analisis.get_df_partidos(equipo)
        # frame = tkinter.Frame(self, width=100, height=200)
        # frame.grid(row=1, column=0, padx=10, pady=10, )
        # self.visualizador_df = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True, width=200, height=200)
        # self.visualizador_df.show()
        estadisticas = analisis.get_stats_de_partidos_de_equipos(equipo)
        self.mostrar_estaditicas_partidos(estadisticas)
        self.mostrar_info_equipo(equipo)
        self.mostrar_graficos(df)
        self.mostrar_tabla_partidos(estadisticas)

    def mostrar_info_equipo(self, equipo):

        liga = equipo.liga
        grupo = equipo.grupo
        temporada = equipo.temporada

        # Create a text widget

        self.textbox.insert(tk.END, f"Liga: {liga}\n")
        self.textbox.insert(tk.END, f"Grupo: {grupo}\n")
        self.textbox.insert(tk.END, f"Temporada: {temporada}\n")
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    def actualizar_filtro(self, event):
        filtro = self.seleccion.get().lower()

        # Filtra los valores que coinciden con el filtro y actualiza el Combobox
        valores_filtrados = [equipo for equipo in self.nombres_equipos if filtro in equipo.lower()]
        self.menu_desplegable['values'] = valores_filtrados

    def mostrar_estaditicas_partidos(self, estadisticas):

        self.textbox = tk.Text(self, height=10, width=35, font=self.master.fuentes["textos"])
        self.textbox.tag_configure("center", justify="center")
        self.textbox.tag_configure("right", justify="right")
        self.textbox.tag_configure("left", justify="left")
        self.textbox.tag_add("center", "1.0", "end")
        self.textbox.tag_add("right", "1.0", "end")
        self.textbox.tag_add("left", "1.0", "end")
        self.textbox.insert(tk.END, "GF\t")
        self.textbox.insert(tk.END, f"{estadisticas.get('avg_GF')} ± {estadisticas.get('sd_GF')}\n")
        self.textbox.insert(tk.END, "GC\t")
        self.textbox.insert(tk.END, f"{estadisticas.get('avg_GC')} ± {estadisticas.get('sd_GC')}\n")
        self.textbox.insert(tk.END, "DIF\t")
        self.textbox.insert(tk.END, f"{estadisticas.get('avg_DIF')} ± {estadisticas.get('sd_DIF')}\n\n")
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def mostrar_graficos(self, df):
        frame = tk.Frame(self, width=200, height=200)
        frame.grid(row=2, column=1, padx=10, pady=10, rowspan=2)

        columnas = ['GolesEquipo', 'GolesRival']
        df = df[columnas]

        # Rename columns
        df = df.rename(columns={'GolesEquipo': self.seleccion.get(), 'GolesRival': 'Rival'})

        # Crear un boxplot usando seaborn (más fácil de manejar para este caso)
        sns.set(style="whitegrid")
        fig, ax = plt.subplots()
        sns.boxplot(data=df, ax=ax, palette="Set3")  # Paleta de colores
        ax.set_ylabel("Goles")
        ax.set_title("Goles por partido")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def cargar_equipos(self):
        urls = []
        for enlace in self.competiciones.enlaces:
            urls.append(enlace)
        self.partidos = []
        for i, url in enumerate(urls):
            print(f"Descargando {i + 1} de {len(urls)}: {url}")
            soup = analisis.get_soup(url)
            partidos_url = (analisis.cargar_partidos(soup)[0])
            for partido in partidos_url:
                self.partidos.append(partido)

        print(f"Total partidos {len(self.partidos)}")

        self.equipos = analisis.crear_equipos(self.partidos)
        self.nombres_equipos = self.equipos.get_nombre_equipos()
        self.nombres_equipos.sort()

    def mostrar_tabla_partidos(self, estadisticas):
        victorias_locales = estadisticas["victorias_locales"]
        victorias_visitantes = estadisticas["victorias_visitantes"]
        empates_locales = estadisticas["empates_locales"]
        empates_visitantes = estadisticas["empates_visitantes"]
        derrotas_locales = estadisticas["derrotas_locales"]
        derrotas_visitantes = estadisticas["derrotas_visitantes"]

        # Crear Treeview
        self.treeview = ttk.Treeview(self, columns=("Tipo", "Victorias", "Empates", "Derrotas", "Total"),
                                     show="headings")
        self.treeview.heading("#1", text="Tipo")
        self.treeview.heading("#2", text="Victorias")
        self.treeview.heading("#3", text="Empates")
        self.treeview.heading("#4", text="Derrotas")
        self.treeview.heading("#5", text="Total")
        # Insertar datos en el Treeview
        self.treeview.insert("", "end", values=("Locales", victorias_locales, empates_locales, derrotas_locales,
                                                victorias_locales + empates_locales + derrotas_locales))
        self.treeview.insert("", "end",
                             values=("Visitantes", victorias_visitantes, empates_visitantes, derrotas_visitantes,
                                     victorias_visitantes + empates_visitantes + derrotas_visitantes))
        self.treeview.insert("", "end",
                             values=(
                             "Total", victorias_locales + victorias_visitantes, empates_locales + empates_visitantes,
                             derrotas_locales + derrotas_visitantes,
                             victorias_locales + empates_locales + derrotas_locales + victorias_visitantes + empates_visitantes + derrotas_visitantes))
        # Alinear columnas a la izquierda
        for col in ("Tipo", "Victorias", "Empates", "Derrotas"):
            self.treeview.column(col, anchor="w")

        self.treeview.column("#1", width=75)
        self.treeview.column("#2", width=75)
        self.treeview.column("#3", width=75)
        self.treeview.column("#4", width=75)
        self.treeview.column("#5", width=75)
        self.treeview.configure(height=10)

        self.treeview.grid(row=2, column=0, padx=10, pady=10)

    def mostrar_clasificacion(self, df_clasificacion):

        self.treeview_clasificacion = ttk.Treeview(self, columns=(
        "Puesto", "Equipo", "Puntos", "Jugados", "Ganados", "Empatados", "Perdidos", "GF", "GC", "DIF"),
                                                   show="headings")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeview_clasificacion.yview)
        self.treeview_clasificacion.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, rowspan=2, padx=10, pady=10, sticky="ns")
        self.treeview_clasificacion.heading("#1", text="#")
        self.treeview_clasificacion.heading("#2", text="Equipo")
        self.treeview_clasificacion.heading("#3", text="Ptos")
        self.treeview_clasificacion.heading("#4", text="J")
        self.treeview_clasificacion.heading("#5", text="V")
        self.treeview_clasificacion.heading("#6", text="E")
        self.treeview_clasificacion.heading("#7", text="D")
        self.treeview_clasificacion.heading("#8", text="GF")
        self.treeview_clasificacion.heading("#9", text="GC")
        self.treeview_clasificacion.heading("#10", text="DIF")

        # Insertar datos en el Treeview
        for i, row in df_clasificacion.iterrows():
            self.treeview_clasificacion.insert("", "end", values=(
            i, row["Equipo"], row["P"], row["PJ"], row["V"], row["E"], row["D"], row["GF"], row["GC"], row["DIF"]))

        # Alinear columnas a la izquierda
        for col in ("Equipo", "Puntos", "Jugados", "Ganados", "Empatados", "Perdidos", "GF", "GC", "DIF"):
            self.treeview_clasificacion.column(col, anchor="w", width=30)

        self.treeview_clasificacion.column("#1", width=30)

        self.treeview_clasificacion.column("#2", width=200)
        self.treeview_clasificacion.column("#3", width=50)

        self.treeview_clasificacion.configure(height=10)
        self.treeview_clasificacion.grid(row=1, column=1, rowspan=1, padx=10, pady=10)

        # On double click
        self.treeview_clasificacion.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        item = self.treeview_clasificacion.selection()[0]
        equipo = self.treeview_clasificacion.item(item, "values")[1]
        self.seleccion.set(equipo)
        self.mostrar_seleccion()


class VentanaConfiguracion(tk.Toplevel):
    def __init__(self, master=None, nombre=None, archivo=None):
        super().__init__(master)
        self.title("Configurar " + nombre)
        if archivo is None:
            messagebox.showerror("Error", "Error al cargar la configuración")
            return
        self.archivo = archivo
        self.vars_control = {}
        self.configuracion = self.cargar_configuracion()
        print(self.configuracion)

    def crear_interfaz(self):
        # Crear y configurar los widgets
        for variable, valor in self.configuracion.items():
            # Etiqueta
            ttk.Label(self, text=variable).pack(pady=5)

            # Checkbox
            var_control = tk.BooleanVar(value=valor)
            self.vars_control[variable] = var_control
            checkbox = ttk.Checkbutton(self, variable=var_control,
                                       command=lambda v=variable: self.actualizar_configuracion(v))
            checkbox.pack()

    def actualizar_configuracion(self, variable):
        # Actualizar el valor de la configuración
        self.configuracion[variable] = self.vars_control[variable].get()

        # Guardar la configuración actualizada
        self.guardar_configuracion()

    def cargar_configuracion(self):
        try:
            with open(self.archivo, "r", encoding="utf-8") as archivo:
                configuracion = json.load(archivo)
            self.configuracion = configuracion
            self.crear_interfaz()
        except FileNotFoundError:
            # Manejar el caso en el que el archivo no existe
            messagebox.showerror("Error", f"El archivo '{self.archivo}' no se encuentra.")
            return {}
        return configuracion

    def guardar_configuracion(self):
        try:
            with open(self.archivo, "w", encoding="utf-8") as archivo:
                json.dump(self.configuracion, archivo, indent=2)
        except Exception as e:
            # Manejar errores al guardar la configuración
            messagebox.showerror("Error", f"Error al guardar la configuración: {e}")


class ExportarVentana():
    def __init__(self, df=None):

        if df is None:
            # Create a error messagebox
            messagebox.showerror("Error", "No hay datos para exportar.")
            return
        self.df = df

        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                    filetypes=[("Excel", "*.xlsx"),
                                                               ("CSV", "*.csv"),
                                                               ("JSON", "*.json")])
        if ruta_archivo:
            try:
                if ruta_archivo.endswith(".xlsx"):
                    self.df.to_excel(ruta_archivo, index=False)
                elif ruta_archivo.endswith(".csv"):
                    self.df.to_csv(ruta_archivo, index=False)
                elif ruta_archivo.endswith(".json"):
                    self.df.to_json(ruta_archivo, index=False)
                else:
                    messagebox.showerror("Error", "Extensión no soportada.")

            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar los datos: {e}")
        else:
            messagebox.showerror("Error", "No se ha seleccionado un archivo para exportar.")


if __name__ == "__main__":
    app = VentanaMain()
    app.mainloop()

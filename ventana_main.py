import io
import json
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, filedialog
from ventana_liga import SegundaVentana
from ventana_exportar import ExportarVentana
from clases import competicion
from tkinter import ttk
import pandas as pd
from SH_Stats_back import analisis
import os
import matplotlib.pyplot as plt


class VentanaMain(tk.Tk):
    def __init__(self):
        super().__init__()
        self.fuentes = {}
        try:
            with open("config/fonts.json", "r") as archivo:
                self.fuentes = json.load(archivo)
        except FileNotFoundError:
            print("No se ha encontrado el archivo fonts.json")
            self.fuentes = {"titulos": ("Arial", 20), "botones": ("Arial", 20), "textos": ("Arial", 10)}

        if not os.path.exists("exports"):
            os.mkdir("exports")
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
        self.title("SH Stats")
        self.geometry("1000x400")

        self.competiciones = []
        self.df_estadisticas = None
        self.df_partidos = None

        # Barra de menú
        self.barra_menu = tk.Menu(self)
        self.config(menu=self.barra_menu)

        # Menú Archivo
        menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        menu_archivo.add_command(label="Abrir", command=self.abrir_archivo)
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo)
        menu_archivo.add_command(label="Borrar competiciones", command=self.borrar_competiciones)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salir)
        self.barra_menu.add_cascade(label="Archivo", menu=menu_archivo)


        # Menú Ayuda
        menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self.acerca_de)
        self.barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        # Columna de Enlaces
        self.label_enlaces = ttk.Label(self, text="Competiciones", style="Title.TLabel")
        self.label_enlaces.grid(row=0, column=0, padx=10, pady=3)
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE , font=self.fuentes["textos"])
        self.listbox.grid(row=2, rowspan = 2, column=0, padx=10, pady=10, sticky="nsew")

        # Botón para añadir Liga
        self.boton_anadir_competicion = ttk.Button(self, text="Añadir Competición", command=self.anadir_liga, style="Boton.TButton")
        self.boton_anadir_competicion.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Columna de Tabla
        self.label_tabla = ttk.Label(self, text="Estadísticas", style="Title.TLabel")
        self.label_tabla.grid(row=0, column=1, padx=10, pady=3)

        boton = ttk.Button(self, text=f"Configurar Estadísticas",
                          command=lambda : self.mostrar_mensaje(f"Configurar Tabla"), style="Boton.TButton")
        boton.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Ver Estadísticas",
                          command=lambda : self.mostrar_dataframe(), style="Boton.TButton")
        boton.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Exportar Estadísticas",
                          command =  lambda:  self.abrir_ventana_exportar(), style="Boton.TButton")
        boton.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        # Columna de Partidos
        self.label_partidos = ttk.Label(self, text="Partidos", style="Title.TLabel")
        self.label_partidos.grid(row=0, column=2, padx=10, pady=3)
        boton = ttk.Button(self, text=f"Configurar Partidos",
                            command=lambda : self.mostrar_mensaje(f"Configurar Tabla"), style="Boton.TButton")
        boton.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Ver Partidos",
                            command=lambda : self.mostrar_partidos(), style="Boton.TButton")
        boton.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Exportar Partidos",
                            command =  lambda:  self.exportar_partidos(), style="Boton.TButton")
        boton.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")


        # Columna de Gráficos
        self.label_graficos = ttk.Label(self, text="Gráficos", style="Title.TLabel")
        self.label_graficos.grid(row=0, column=3, padx=10, pady=3)

        boton = ttk.Button(self, text=f"Configurar Gráficos",
                          command=lambda : self.mostrar_mensaje(f"Configurar Gráficos"), style="Boton.TButton")
        boton.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Ver Gráficos",
                          command=lambda : self.mostrar_graficos(), style="Boton.TButton")
        boton.grid(row=2, column=3, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Exportar Gráficos",
                          command =  lambda:  self.mostrar_mensaje(f"Exportar Gráficos"), style="Boton.TButton")
        boton.grid(row=3, column=3, padx=10, pady=10, sticky="nsew")


        # Otras cosas
        self.cargar_configuracion()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)



    def on_select(self, event):
        # display element selected on list
        try:
            index = self.listbox.curselection()[0]
            self.mostrar_segunda_ventana(self.competiciones[index])
        except IndexError:
            pass


    def borrar_competiciones(self):
        self.competiciones = []
        self.actualizar_listbox()
        self.guardar_configuracion()
        self.df_estadisticas = None
        self.df_partidos = None

    def abrir_archivo(self):
        # Agrega la lógica para abrir un archivo
        file_path = filedialog.askopenfilename(filetypes=[("Archivo SHStats", "*.shs"), ("Todos los archivos", "*.*")])
        if file_path:
            # Agrega la lógica para abrir el archivo seleccionado
            with open(file_path, "r") as archivo:
                #delete ligas.json content

                with open("config/ligas.shs", "w") as ligas:
                    ligas.write(archivo.read())
            self.cargar_configuracion()
            self.actualizar_listbox()

    def guardar_archivo(self):
        # Abre un cuadro de diálogo para elegir la ubicación de guardado
        file_path = filedialog.asksaveasfilename(defaultextension=".shs",
                                                   filetypes=[("Archivo SHStats", "*.shs"), ("Todos los archivos", "*.*")])
        if file_path:
            # Agrega la lógica para guardar el archivo en la ubicación seleccionada
            with open(file_path, "w") as archivo:
                # Copy content from ligas.json to the new file
                with open("config/ligas.shs", "r") as ligas:
                    archivo.write(ligas.read())

    def salir(self):
        self.destroy()

    def acerca_de(self):
        # Agrega la lógica para mostrar información acerca de la aplicación
        print("Acerca de")
    def mostrar_graficos(self):
        if self.df_estadisticas is None:
            self.df_estadisticas = self.get_dataframe()
        if self.df_estadisticas is None:
            return
        plt.bar(self.df_estadisticas["nombre"], self.df_estadisticas["avg_goles"], color ="blue")
        plt.title("Goles por partido")
        plt.show()
        plt.bar(self.df_estadisticas["nombre"], self.df_estadisticas["avg_DIF_total"], color ="blue")
        plt.title("Diferencia de goles por partido")
        plt.show()
        # plt.bar(self.df["nombre"], self.df["avg_GF_en_victorias"], color = "blue")
        # plt.bar(self.df["nombre"], self.df["avg_GC_en_victorias"], color = "red")
        # plt.title("Goles en victorias")
        # plt.show()

    def mostrar_partidos(self):
        urls = []
        if self.df_partidos is None:
            for liga in self.competiciones:
                urls.extend(liga.enlaces)
            partidos = analisis.comparar_partidos(urls)
        else:
            partidos = self.df_partidos
        if partidos is None:
            return
        ventana_partidos = tk.Toplevel(self)
        ventana_partidos.title("Ventana de Partidos")
        # Crear un widget tk.Treeview para mostrar el DataFrame en la nueva ventana
        tree = ttk.Treeview(ventana_partidos)
        tree["columns"] = list(partidos.columns)
        #tree.heading("#0", text="Índice")
        for col in partidos.columns:
            tree.heading(col, text=col)

        # Agregar filas al tk.Treeview
        for index, row in partidos.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(padx=10, pady=10)
        self.df_partidos = partidos

    def exportar_partidos(self):
        urls = []
        if self.df_partidos is None:
            for liga in self.competiciones:
                urls.extend(liga.enlaces)
            self.df_partidos = analisis.comparar_partidos(urls)
        if self.df_partidos is None:
            return
        ventana_exportar = ExportarVentana(self, self.df_partidos)






    def abrir_ventana_exportar(self):
        if self.df_estadisticas is None:
            self.df_estadisticas = self.get_dataframe()
        if self.df_estadisticas is None:
            return
        ventana_exportar = ExportarVentana(self, self.df_estadisticas)
    def mostrar_segunda_ventana(self, liga):
        segunda_ventana = SegundaVentana(self, liga)

    def actualizar_boton_liga(self, liga):
        # Buscar el botón que corresponde a la liga usando index
        for boton in self.grid_slaves(column=0):
            if boton.grid_info()["row"] == liga.index + 2:
                boton.config(text=liga.nombre)

    def borrar_boton_liga(self, liga):
        # Buscar el botón que corresponde a la liga usando index
        if liga in self.competiciones:
            self.competiciones.remove(liga)
            self.actualizar_listbox()


    def get_dataframe(self):
        #Hacemos la tarea
        liga = None
        try:
            ligas_y_enlaces = {}
            for liga in self.competiciones:
                ligas_y_enlaces[liga.nombre] = liga.enlaces
            df = analisis.comparar_ligas(ligas_y_enlaces)
            #Terminamos la tarea
            self.df_estadisticas = df
            return df
        except Exception as e:
            if len(self.competiciones) == 0:
                messagebox.showerror("Error", "No hay ligas para comparar.\nAñade ligas para poder compararlas.")
            else:
                messagebox.showerror("Error", f"Ha ocurrido un error al intentar obtener las estadísticas de \"{liga.nombre}\".\nVerifica que las urls sean correctas.")

            print(e)
            return None
    def mostrar_dataframe(self):
        if self.df_estadisticas is None:
            self.get_dataframe()
        if self.df_estadisticas is None:
            return

        ventana_dataframe = tk.Toplevel(self)
        ventana_dataframe.title("Ventana del DataFrame")

        # Crear un widget tk.Treeview para mostrar el DataFrame en la nueva ventana
        tree = ttk.Treeview(ventana_dataframe)
        tree["columns"] = list(self.df_estadisticas.columns)
        #tree.heading("#0", text="Índice")
        for col in self.df_estadisticas.columns:
            tree.heading(col, text=col)

        # Agregar filas al tk.Treeview
        for index, row in self.df_estadisticas.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(padx=10, pady=10)



    def anadir_liga(self):
        nueva_liga = competicion()
        self.mostrar_segunda_ventana(nueva_liga)


    def anadir_boton_liga(self, liga, index = None):
        estilo_boton = ttk.Style()
        estilo_boton.configure("BotonVerde.TButton", padding=6, relief="flat",
        background="white", foreground="green", anchor="center", borderwidth=4, font = self.fuentes["textos"])
        boton = ttk.Button(self, text=liga.nombre, command=lambda: self.mostrar_segunda_ventana(liga), style="BotonPequeño.TButton")
        if index != None:
            boton.grid(row=index + 2, column=0, padx=10, pady=10, sticky="nsew")
        else:
            boton.grid(row=len(self.competiciones) + 1, column=0, padx=10, pady=10, sticky="nsew")

    def mostrar_mensaje(self, mensaje):
        mensaje = mensaje + "\nFunción no implementada."
        messagebox.showinfo("Mensaje", mensaje)

    def guardar_configuracion(self):
        # Guardar la configuración en un archivo JSON
        configuracion = {"ligas": [{"nombre": liga.nombre, "index": liga.index, "enlaces": liga.enlaces} for liga in self.competiciones]}
        with open("config/ligas.shs", "w") as archivo:
            json.dump(configuracion, archivo)

    def cargar_configuracion(self):
        try:
            # Cargar la configuración desde el archivo JSON
            with open("config/ligas.shs", "r") as archivo:
                configuracion = json.load(archivo)
                ligas = configuracion.get("ligas", [])
                self.competiciones = [competicion(nombre=liga["nombre"], enlaces=liga["enlaces"]) for liga in ligas]
                self.actualizar_listbox()

        except FileNotFoundError:
            # Si el archivo no existe, no hay configuración para cargar
            pass

    def actualizar_listbox(self):
        self.listbox.delete(0, tk.END)
        self.df_estadisticas = None
        for liga in self.competiciones:
            self.listbox.insert(tk.END, liga.nombre)



if __name__ == "__main__":
    app = VentanaMain()
    app.mainloop()
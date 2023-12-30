import io
import json
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from ventana_liga import SegundaVentana
from ventana_exportar import ExportarVentana
from clases import liga_favorita
from tkinter import ttk
import pandas as pd
from SH_Stats_back import analisis
import os


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
        self.geometry("800x400")

        self.ligas_favoritas = []

        # Columna de Enlaces
        self.label_enlaces = ttk.Label(self, text="Competiciones", style="Title.TLabel")
        self.label_enlaces.grid(row=0, column=0, padx=10, pady=3)

        # Botón para añadir Liga
        self.boton_anadir_liga = ttk.Button(self, text="Añadir Competición", command=self.anadir_liga, style="Boton.TButton")
        self.boton_anadir_liga.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Columna de Tabla
        self.label_tabla = ttk.Label(self, text="Tabla", style="Title.TLabel")
        self.label_tabla.grid(row=0, column=1, padx=10, pady=3)

        boton = ttk.Button(self, text=f"Configurar Tabla",
                          command=lambda : self.mostrar_mensaje(f"Configurar Tabla"), style="Boton.TButton")
        boton.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Ver Tabla",
                          command=lambda : self.mostrar_dataframe(), style="Boton.TButton")
        boton.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Exportar Tabla",
                          command =  lambda:  self.abrir_ventana_exportar(), style="Boton.TButton")
        boton.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")


        # Columna de Gráficos
        # self.label_graficos = ttk.Label(self, text="Gráficos", style="Title.TLabel")
        # self.label_graficos.grid(row=0, column=2, padx=10, pady=3)
        #
        # boton = ttk.Button(self, text=f"Configurar Gráficos",
        #                   command=lambda : self.mostrar_mensaje(f"Configurar Gráficos"), style="Boton.TButton")
        # boton.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        # boton = ttk.Button(self, text=f"Ver Gráficos",
        #                   command=lambda : self.mostrar_mensaje(f"Ver Gráficos"), style="Boton.TButton")
        # boton.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        # boton = ttk.Button(self, text=f"Exportar Gráficos",
        #                   command =  lambda:  self.mostrar_mensaje(f"Exportar Gráficos"), style="Boton.TButton")
        # boton.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")


        # Otras cosas
        self.cargar_configuracion()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)




    def ajustar_pantalla(self, event):
        self.geometry(f"{event.width}x{event.height}")

    def abrir_ventana_exportar(self):
        df = self.get_dataframe()
        ventana_exportar = ExportarVentana(self, df)
    def mostrar_segunda_ventana(self, liga):
        segunda_ventana = SegundaVentana(self, liga)

    def actualizar_boton_liga(self, liga):
        # Buscar el botón que corresponde a la liga usando index
        for boton in self.grid_slaves(column=0):
            if boton.grid_info()["row"] == liga.index + 2:
                boton.config(text=liga.nombre)

    def borrar_boton_liga(self, liga):
        # Buscar el botón que corresponde a la liga usando index
        for boton in self.grid_slaves(column=0):
            if boton.grid_info()["row"] == liga.index + 2:
                boton.destroy()
        self.ligas_favoritas.remove(liga)
        # Reajustar los índices de las ligas
        for index, liga in enumerate(self.ligas_favoritas):
            liga.index = index
        for boton in self.grid_slaves(column=0):
            if boton.grid_info()["row"] > 1:
                #remove the old button
                boton.destroy()
        for liga in self.ligas_favoritas:
            self.anadir_boton_liga(liga, index= liga.index)


    def get_dataframe(self):
        #Hacemos la tarea
        liga = None
        try:
            ligas_y_enlaces = {}
            for liga in self.ligas_favoritas:
                ligas_y_enlaces[liga.nombre] = liga.enlaces
            df = analisis.comparar_ligas(ligas_y_enlaces)
            #Terminamos la tarea
            return df
        except Exception as e:
            if len(self.ligas_favoritas) == 0:
                messagebox.showerror("Error", "No hay ligas para comparar.\nAñade ligas para poder compararlas.")
            else:
                messagebox.showerror("Error", f"Ha ocurrido un error al intentar obtener las estadísticas de \"{liga.nombre}\".\nVerifica que las urls sean correctas.")

            print(e)
            return None
    def mostrar_dataframe(self):

        df = self.get_dataframe()
        if df is None:
            return

        ventana_dataframe = tk.Toplevel(self)
        ventana_dataframe.title("Ventana del DataFrame")

        # Crear un widget tk.Treeview para mostrar el DataFrame en la nueva ventana
        tree = ttk.Treeview(ventana_dataframe)
        tree["columns"] = list(df.columns)
        #tree.heading("#0", text="Índice")
        for col in df.columns:
            tree.heading(col, text=col)

        # Agregar filas al tk.Treeview
        for index, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        tree.pack(padx=10, pady=10)



    def anadir_liga(self):
        ventana_annadir_liga = tk.Toplevel(self)
        ventana_annadir_liga.title("Añadir Competición")
        ttk.Label(ventana_annadir_liga, text="Añadir Competición:", style="Title.TLabel").pack(pady=5)

        self.entry_nombre_liga = ttk.Entry(ventana_annadir_liga, font = self.fuentes["botones"], width = 30)
        self.entry_nombre_liga.pack(padx=10, pady=5)

        def obtener_nombre_liga():
            nombre_liga = self.entry_nombre_liga.get()
            if nombre_liga:
                nueva_liga = liga_favorita(index=len(self.ligas_favoritas), nombre=nombre_liga)
                self.ligas_favoritas.append(nueva_liga)
                self.anadir_boton_liga(nueva_liga)
                self.mostrar_segunda_ventana(nueva_liga)
                ventana_annadir_liga.destroy()
        # Botón para aceptar
        boton_aceptar = ttk.Button(ventana_annadir_liga, text="Aceptar", style = "Boton.TButton",command=obtener_nombre_liga)
        boton_aceptar.pack(pady=10)


    def anadir_boton_liga(self, liga, index = None):
        estilo_boton = ttk.Style()
        estilo_boton.configure("BotonVerde.TButton", padding=6, relief="flat",
        background="white", foreground="green", anchor="center", borderwidth=4, font = self.fuentes["textos"])
        boton = ttk.Button(self, text=liga.nombre, command=lambda: self.mostrar_segunda_ventana(liga), style="BotonPequeño.TButton")
        if index != None:
            boton.grid(row=index + 2, column=0, padx=10, pady=10, sticky="nsew")
        else:
            boton.grid(row=len(self.ligas_favoritas) + 1, column=0, padx=10, pady=10, sticky="nsew")

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Mensaje", mensaje)

    def guardar_configuracion(self):
        # Guardar la configuración en un archivo JSON
        configuracion = {"ligas": [{"nombre": liga.nombre, "index": liga.index, "enlaces": liga.enlaces} for liga in self.ligas_favoritas]}
        with open("config/ligas.json", "w") as archivo:
            json.dump(configuracion, archivo)

    def cargar_configuracion(self):
        try:
            # Cargar la configuración desde el archivo JSON
            with open("config/ligas.json", "r") as archivo:
                configuracion = json.load(archivo)
                ligas = configuracion.get("ligas", [])
                self.ligas_favoritas = [liga_favorita(nombre=liga["nombre"], index = liga["index"], enlaces=liga["enlaces"]) for liga in ligas]
                for liga in self.ligas_favoritas:
                    self.anadir_boton_liga(liga, index = liga.index)

        except FileNotFoundError:
            # Si el archivo no existe, no hay configuración para cargar
            pass




if __name__ == "__main__":
    app = VentanaMain()
    app.mainloop()
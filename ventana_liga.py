import json
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from SH_Stats_back import funciones_auxiliares
from SH_Stats_back import analisis
from ventana_equipos import VentanaEquipos
from ventana_exportar import ExportarVentana


class SegundaVentana(tk.Toplevel):
    def __init__(self, parent, liga, fonts = None):
        super().__init__(parent)
        if fonts is None:
            try:
                with open("config/fonts.json", "r") as archivo:
                    self.fuentes = json.load(archivo)
            except FileNotFoundError:
                print("No se ha encontrado el archivo fonts.json")
                self.fuentes = {"titulos": ("Arial", 20), "botones": ("Arial", 12)}

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

        self.title(f"Liga: {liga.nombre}")
        self.geometry("1000x400")
        self.liga = liga
        self.df = None



        # Columna 1
        self.label_col1 = ttk.Label(self, text="Links", style="Title.TLabel")
        self.label_col1.grid(row=0, column=0, padx=10, pady=10)
        # Botón para añadir Liga
        self.boton_anadir_enlace = ttk.Button(self, text="Añadir Enlace", command=self.anadir_enlace,
                                           style="Boton.TButton")
        self.boton_anadir_enlace.grid(row=1, column=0, padx=10, pady=10)
        self.listbox_enlaces = tk.Listbox(self, font=self.fuentes["textos"])
        self.listbox_enlaces.grid(row=2, rowspan = 2, column=0, padx=10, pady=10)

        self.boton_cerrar = ttk.Button(self, text="Guardar", command=lambda: self.guardar_liga(liga),
                                       style="BotonVerde.TButton")
        self.boton_cerrar.grid(row=4, column=0, columnspan = 2, padx=10, pady=10, sticky="nsew")

        # Columna 2 - Nombre
        self.label_nombre = ttk.Label(self, text="Nombre", style="Title.TLabel")
        self.label_nombre.grid(row=0, column=1, padx=10, pady=10)

        self.entry_nombre = ttk.Entry(self, font=self.fuentes["botones"])
        self.entry_nombre.insert(0, liga.nombre)
        self.entry_nombre.grid(row=1, column=1, padx=10, pady=10)

        # Columna 3
        self.label_col3 = ttk.Label(self, text="Opciones", style="Title.TLabel")
        self.label_col3.grid(row=0, column=2, padx=10, pady=10)

        boton = ttk.Button(self, text=f"Configurar Tabla Partidos",
                          command=lambda: self.mostrar_mensaje(f"Configurar Tabla Partidos"),
                            style="Boton.TButton")
        boton.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Ver Tabla Partidos",
                          command=lambda: self.mostrar_dataframe(),
                          style="Boton.TButton")
        boton.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        boton = ttk.Button(self, text=f"Exportar Tabla Partidos",
                          command=lambda: self.exportar_dataframe(),
                          style="Boton.TButton")
        boton.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")
        self.boton_borrar = ttk.Button(self, text="Borrar", command=lambda: self.borrar_liga(liga),
                                       style="BotonRojo.TButton")
        self.boton_borrar.grid(row=4, column=2, padx=10, pady=10, sticky="nsew")

        # Columna 4

        self.label_col4 = ttk.Label(self, text="Equipos", style="Title.TLabel")
        self.label_col4.grid(row=0, column=3, padx=10, pady=10)
        self.boton_equipos = ttk.Button(self, text="Ver Equipos", command=lambda: self.cargar_ventana_equipos(),
                                        style="Boton.TButton")
        self.boton_equipos.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")



        self.actualizar_botones_enlaces()

        self.listbox_enlaces.bind("<<ListboxSelect>>", self.on_select)

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
            messagebox.showerror("Error", "Ha ocurrido un error al intentar obtener los datos.\nVerifica que los enlaces sean correctos.")
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
            messagebox.showerror("Error", "Ha ocurrido un error al intentar exportar los datos.\nVerifica que el nombre del archivo sea correcto.")
        ventana.destroy()
    def exportar_a_csv(self, df, nombre_archivo):
        try:
            df.to_csv("exports/" + nombre_archivo + ".csv")
            print(f"Exportado a CSV: {nombre_archivo}")
            messagebox.showinfo("Exportado", "Los datos se han exportado correctamente en la carpeta exports.")
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Ha ocurrido un error al intentar exportar los datos.\nVerifica que el nombre del archivo sea correcto.")
    def anadir_enlace(self):
        ventana_annadir_enlace = tk.Toplevel(self)
        ventana_annadir_enlace.title("Añadir Enlace")
        ttk.Label(ventana_annadir_enlace, text="Añadir Enlace:", style="Title.TLabel").pack(pady=5)
        entry_enlace = ttk.Entry(ventana_annadir_enlace, font=self.fuentes["botones"], width=50)
        entry_enlace.pack(pady=5)
        def guardar_enlace():
            nuevo_enlace = entry_enlace.get()
            nuevo_enlace = funciones_auxiliares.convert_url(nuevo_enlace)
            self.liga.enlaces.append(nuevo_enlace)
            self.actualizar_botones_enlaces()
            ventana_annadir_enlace.destroy()
        btn_guardar = ttk.Button(ventana_annadir_enlace, text="Guardar", command=guardar_enlace, style="BotonVerde.TButton")
        btn_guardar.pack(pady=5)


    def edicion_enlace(self, enlace):
        enlace_en_uso = enlace
        # Crear una nueva ventana para la edición del enlace
        ventana_edicion = tk.Toplevel(self)
        ventana_edicion.title("Edición de Enlace")

        # Etiqueta y caja de texto para editar el enlace
        ttk.Label(ventana_edicion, text="Editar Enlace:", style="Title.TLabel").grid(row=0, column=0, columnspan=2,padx=10, pady=10)
        entry_enlace = ttk.Entry(ventana_edicion, font=self.fuentes["botones"], width=50)
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
                               command=lambda: self.borrar_enlace(enlace_en_uso, ventana_edicion),style="BotonRojo.TButton")
        btn_borrar.grid(row=2, column=1, padx=10, pady=10)

    def borrar_enlace(self, enlace, ventana_edicion): # Aquí puedes realizar acciones para borrar el enlace, por ejemplo, actualizar tu lista de enlaces
            if enlace in self.liga.enlaces:
                self.liga.enlaces.remove(enlace)
                self.actualizar_botones_enlaces()
            ventana_edicion.destroy()

    def actualizar_botones_enlaces(self):
        self.df = None
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
            if liga not in self.master.competiciones:
                self.master.competiciones.append(liga)
            liga.nombre = nombre_nuevo
            self.master.actualizar_listbox()
            self.master.guardar_configuracion()  # Guarda la configuración al actualizar la liga
        self.destroy()
    def borrar_liga(self, liga):
        self.master.borrar_boton_liga(liga)
        self.master.guardar_configuracion()
        self.destroy()
    def mostrar_mensaje(self, mensaje):
        mensaje = mensaje + "\n (Esta función aún no está implementada)"
        messagebox.showinfo("Mensaje", mensaje)

    def cargar_ventana_equipos(self):
        ventana_equipos = VentanaEquipos(self.liga)
        ventana_equipos.mainloop()
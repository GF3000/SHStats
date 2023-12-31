import json
import tkinter as tk
from tkinter import ttk, messagebox


class VentanaConfiguracion(tk.Toplevel):
    def __init__(self, master=None, nombre = None, archivo = None):
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
            checkbox = ttk.Checkbutton(self, variable=var_control, command=lambda v=variable: self.actualizar_configuracion(v))
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
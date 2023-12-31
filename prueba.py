import tkinter as tk
from tkinter import ttk, messagebox
import json

class ConfiguracionEstadisticas:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuración de Estadísticas")

        # Cargar configuración desde el archivo JSON
        self.configuracion = self.cargar_configuracion()

        # Diccionario para almacenar las variables de control
        self.vars_control = {}

        # Crear y mostrar la interfaz gráfica
        self.crear_interfaz()

    def cargar_configuracion(self):
        try:
            with open("config/config_estadisticas.json", "r", encoding="utf-8") as archivo:
                configuracion = json.load(archivo)
            return configuracion
        except FileNotFoundError:
            # Manejar el caso en el que el archivo no existe
            messagebox.showerror("Error", "El archivo 'config/config_estadisticas.json' no se encuentra.")
            return {}

    def guardar_configuracion(self):
        try:
            with open("config/config_estadisticas.json", "w", encoding="utf-8") as archivo:
                json.dump(self.configuracion, archivo, indent=2)
        except Exception as e:
            # Manejar errores al guardar la configuración
            messagebox.showerror("Error", f"Error al guardar la configuración: {e}")

    def crear_interfaz(self):
        # Crear y configurar los widgets
        for variable, valor in self.configuracion.items():
            # Etiqueta
            ttk.Label(self.root, text=variable).pack(pady=5)

            # Checkbox
            var_control = tk.BooleanVar(value=valor)
            self.vars_control[variable] = var_control
            checkbox = ttk.Checkbutton(self.root, variable=var_control, command=lambda v=variable: self.actualizar_configuracion(v))
            checkbox.pack()

    def actualizar_configuracion(self, variable):
        # Actualizar el valor de la configuración
        self.configuracion[variable] = self.vars_control[variable].get()

        # Guardar la configuración actualizada
        self.guardar_configuracion()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguracionEstadisticas(root)
    root.mainloop()

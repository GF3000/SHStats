import tkinter as tk
from tkinter import ttk, messagebox
import openpyxl


class ExportarVentana(tk.Toplevel):
    def __init__(self, master=None, df = None):
        super().__init__(master)
        self.title("Exportar Datos")
        if df is None:
            #Create a error messagebox
            messagebox.showerror("Error", "No hay datos para exportar.")
            return
        self.df = df


        # Etiqueta y caja de texto para el nombre del archivo
        ttk.Label(self, text="Nombre del archivo:").pack(pady=5)
        self.nombre_archivo_entry = ttk.Entry(self)
        self.nombre_archivo_entry.pack(pady=5)

        # Botones para exportar a Excel y CSV
        ttk.Button(self, text="Exportar a Excel", command=self.exportar_a_excel).pack(pady=5)
        ttk.Button(self, text="Exportar a CSV", command=self.exportar_a_csv).pack(pady=5)

    def exportar_a_excel(self):
        # Lógica para exportar a Excel
        try:
            nombre_archivo = self.nombre_archivo_entry.get()
            self.df.to_excel("exports/" + nombre_archivo + ".xlsx")
            print(f"Exportado a Excel: {nombre_archivo}")
            messagebox.showinfo("Exportado", "Los datos se han exportado correctamente en la carpeta exports.")

            #destroy the window
            self.destroy()
        except Exception as e:
            print(e)
            #Create a error messagebox
            messagebox.showerror("Error", "Ha ocurrido un error al intentar exportar los datos.\nVerifica que el nombre del archivo sea correcto.")

    def exportar_a_csv(self):
        #Check if exports folder exists

        # Lógica para exportar a CSV
        try:
            nombre_archivo = self.nombre_archivo_entry.get()
            self.df.to_csv("exports/" + nombre_archivo + ".csv")
            print(f"Exportado a CSV: {nombre_archivo}")
            messagebox.showinfo("Exportado", "Los datos se han exportado correctamente en la carpeta exports.")
            #destroy the window
            self.destroy()

        except Exception as e:
            print(e)
            #Create a error messagebox
            messagebox.showerror("Error", "Ha ocurrido un error al intentar exportar los datos.\nVerifica que el nombre del archivo sea correcto.")
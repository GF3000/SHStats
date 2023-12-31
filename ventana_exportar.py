import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import openpyxl


class ExportarVentana():
    def __init__(self, df = None):

        if df is None:
            #Create a error messagebox
            messagebox.showerror("Error", "No hay datos para exportar.")
            return
        self.df = df

        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")])
        if ruta_archivo:
            try:
                if ruta_archivo.endswith(".xlsx"):
                    self.df.to_excel(ruta_archivo, index=False)
                else:
                    self.df.to_csv(ruta_archivo, index=False)
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar los datos: {e}")
        else:
            messagebox.showerror("Error", "No se ha seleccionado un archivo para exportar.")

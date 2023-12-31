import tkinter as tk
from tkinter import ttk, filedialog

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Barra de Opciones")

        # Barra de menú
        self.barra_menu = tk.Menu(self.root)
        self.root.config(menu=self.barra_menu)

        # Menú Archivo
        menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        menu_archivo.add_command(label="Abrir", command=self.abrir_archivo)
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salir)
        self.barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        # Menú Ayuda
        menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self.acerca_de)
        self.barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

    def abrir_archivo(self):
        # Agrega la lógica para abrir un archivo
        print("Abrir archivo")

    def guardar_archivo(self):
        # Abre un cuadro de diálogo para elegir la ubicación de guardado
        file_path = filedialog.asksaveasfilename(defaultextension=".shs",
                                                   filetypes=[("Archivo SHStats", "*.shs"), ("Todos los archivos", "*.*")])
        if file_path:
            # Agrega la lógica para guardar el archivo en la ubicación seleccionada
            print(f"Guardar en: {file_path}")

    def salir(self):
        self.root.destroy()

    def acerca_de(self):
        # Agrega la lógica para mostrar información acerca de la aplicación
        print("Acerca de")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()

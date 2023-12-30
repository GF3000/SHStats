import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class TreeviewApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Treeview Example")

        # Crear un Treeview con una sola columna
        self.treeview = ttk.Treeview(self.master, columns=("Nombre",))
        self.treeview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Agregar encabezado
        self.treeview.heading("#0", text="Nombre")

        # Agregar datos
        self.treeview.insert("", "end", text="Juan")
        self.treeview.insert("", "end", text="María")
        self.treeview.insert("", "end", text="Carlos")

        # Configurar opciones de peso para centrar
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Botón Eliminar
        self.boton_eliminar = ttk.Button(self.master, text="Eliminar", command=self.eliminar_seleccion)
        self.boton_eliminar.grid(row=1, column=0, pady=10)

        # Configurar el evento de selección
        self.treeview.bind("<ButtonRelease-1>", self.mostrar_mensaje)

    def eliminar_seleccion(self):
        # Obtener la selección actual
        seleccion = self.treeview.selection()
        if seleccion:
            # Eliminar la entrada seleccionada
            self.treeview.delete(seleccion)

    def mostrar_mensaje(self, event):
        # Obtener el elemento seleccionado
        item = self.treeview.selection()
        if item:
            # Obtener el texto del elemento seleccionado
            texto = self.treeview.item(item, "text")

            # Mostrar un cuadro de mensaje con el texto
            messagebox.showinfo("Nombre Seleccionado", f"Nombre: {texto}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TreeviewApp(root)
    root.mainloop()

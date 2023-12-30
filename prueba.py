import tkinter as tk
from tkinter import ttk

class MiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ejemplo de ttk con fuente personalizada")

        # Crear una fuente personalizada
        fuente_personalizada = ("Arial", 12)

        # Crear un estilo de ttk y configurar la fuente en el estilo
        estilo = ttk.Style()
        estilo.configure("TButton", font=fuente_personalizada)

        # Crear un widget de ttk con el estilo configurado
        boton_ttk = ttk.Button(self, text="Hacer algo", command=self.hacer_algo, style="TButton")
        boton_ttk.pack(pady=20)

    def hacer_algo(self):
        print("¡Haciendo algo!")

if __name__ == "__main__":
    app = MiApp()
    app.mainloop()

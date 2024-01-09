import tkinter
from tkinter import ttk, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from pandastable import Table

import pandas as pd

from SH_Stats_back import analisis
from SH_Stats_back import clases


class VentanaEquipos(tkinter.Toplevel):

    def __init__(self, competiciones):
        tkinter.Toplevel.__init__(self)
        self.competiciones = competiciones
        self.title("Equipos")
        self.geometry("1000x800")
        self.resizable(True, False)
        self.config(bg="white")
        self.equipos = None
        self.nombres_equipos = None
        self.partidos = None
        self.df_partidos = None

        self.cargar_equipos()
        self.crear_widgets()







    def crear_widgets(self):


        # Variable de control para el menú desplegable
        self.seleccion = tkinter.StringVar()

        # Menú desplegable
        self.menu_desplegable = ttk.Combobox(self, textvariable=self.seleccion, values=self.nombres_equipos, state="normal", width=50)
        self.menu_desplegable.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.menu_desplegable.bind('<KeyRelease>', self.actualizar_filtro)
        self.menu_desplegable.bind('<<ComboboxSelected>>', self.mostrar_seleccion)
        df_clasificacion = analisis.get_clasificacion(self.partidos)
        self.mostrar_clasificacion(df_clasificacion)

        #Select the first item
        self.menu_desplegable.current(0)
        self.mostrar_seleccion()
    def mostrar_seleccion(self, event=None):
        # Mostrar la selección en un messagebox
        seleccion = self.seleccion.get()
        equipo = self.equipos.buscar_por_nombre(seleccion)
        df = analisis.get_df_partidos(equipo)
        # frame = tkinter.Frame(self, width=100, height=200)
        # frame.grid(row=1, column=0, padx=10, pady=10, )
        # self.visualizador_df = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True, width=200, height=200)
        # self.visualizador_df.show()
        estadisticas = analisis.get_stats_de_partidos_de_equipos(equipo)
        self.mostrar_estaditicas_partidos(estadisticas)
        self.mostrar_info_equipo(equipo)
        self.mostrar_graficos(df)
        self.mostrar_tabla_partidos(estadisticas)


    def mostrar_info_equipo(self, equipo):

        liga = equipo.liga
        grupo = equipo.grupo
        temporada = equipo.temporada

        # Create a text widget

        self.textbox.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.textbox.insert(tkinter.END, f"Liga: {liga}\n")
        self.textbox.insert(tkinter.END, f"Grupo: {grupo}\n")
        self.textbox.insert(tkinter.END, f"Temporada: {temporada}\n")
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    def actualizar_filtro(self, event):
        filtro = self.seleccion.get().lower()

        # Filtra los valores que coinciden con el filtro y actualiza el Combobox
        valores_filtrados = [equipo for equipo in self.nombres_equipos if filtro in equipo.lower()]
        self.menu_desplegable['values'] = valores_filtrados

    def mostrar_estaditicas_partidos(self, estadisticas):



        self.textbox = tkinter.Text(self, height=10,  width=50)
        self.textbox.tag_configure("center", justify="center")
        self.textbox.tag_configure("right", justify="right")
        self.textbox.tag_configure("left", justify="left")
        self.textbox.tag_add("center", "1.0", "end")
        self.textbox.tag_add("right", "1.0", "end")
        self.textbox.tag_add("left", "1.0", "end")
        self.textbox.insert(tkinter.END, "GF\t")
        self.textbox.insert(tkinter.END, f"{estadisticas.get('avg_GF')} ± {estadisticas.get('sd_GF')}\n")
        self.textbox.insert(tkinter.END, "GC\t")
        self.textbox.insert(tkinter.END, f"{estadisticas.get('avg_GC')} ± {estadisticas.get('sd_GC')}\n")
        self.textbox.insert(tkinter.END, "DIF\t")
        self.textbox.insert(tkinter.END, f"{estadisticas.get('avg_DIF')} ± {estadisticas.get('sd_DIF')}\n\n")
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


    def mostrar_graficos(self, df):
        frame = tkinter.Frame(self, width=600, height=200)
        frame.grid(row=2, column=2, padx=10, pady=10, rowspan=2)

        columnas = ['GolesEquipo', 'GolesRival']
        df = df[columnas]

        # Rename columns
        df = df.rename(columns={'GolesEquipo': self.seleccion.get(), 'GolesRival': 'Rival'})


        # Crear un boxplot usando seaborn (más fácil de manejar para este caso)
        sns.set(style="whitegrid")
        fig, ax = plt.subplots()
        sns.boxplot(data=df, ax=ax, palette="Set3")  # Paleta de colores
        ax.set_ylabel("Goles")
        ax.set_title("Goles por partido")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def cargar_equipos(self):
        urls = []
        for enlace in self.competiciones.enlaces:
            urls.append(enlace)
        self.partidos = []
        for i, url in enumerate(urls):
            print(f"Descargando {i + 1} de {len(urls)}: {url}")
            soup = analisis.get_soup(url)
            partidos_url = (analisis.cargar_partidos(soup)[0])
            for partido in partidos_url:
                self.partidos.append(partido)

        print(f"Total partidos {len(self.partidos)}")

        self.equipos = analisis.crear_equipos(self.partidos)
        self.nombres_equipos = self.equipos.get_nombre_equipos()
        self.nombres_equipos.sort()

    def mostrar_tabla_partidos(self, estadisticas):
        victorias_locales = estadisticas["victorias_locales"]
        victorias_visitantes = estadisticas["victorias_visitantes"]
        empates_locales = estadisticas["empates_locales"]
        empates_visitantes = estadisticas["empates_visitantes"]
        derrotas_locales = estadisticas["derrotas_locales"]
        derrotas_visitantes = estadisticas["derrotas_visitantes"]

        # Crear Treeview
        self.treeview = ttk.Treeview(self, columns=("Tipo", "Victorias", "Empates", "Derrotas", "Total"), show="headings")
        self.treeview.heading("#1", text="Tipo")
        self.treeview.heading("#2", text="Victorias")
        self.treeview.heading("#3", text="Empates")
        self.treeview.heading("#4", text="Derrotas")
        self.treeview.heading("#5", text="Total")
        # Insertar datos en el Treeview
        self.treeview.insert("", "end", values=("Locales", victorias_locales, empates_locales, derrotas_locales, victorias_locales + empates_locales + derrotas_locales))
        self.treeview.insert("", "end",
                             values=("Visitantes", victorias_visitantes, empates_visitantes, derrotas_visitantes, victorias_visitantes + empates_visitantes + derrotas_visitantes))
        self.treeview.insert("", "end",
                             values=("Total", victorias_locales + victorias_visitantes, empates_locales + empates_visitantes, derrotas_locales + derrotas_visitantes, victorias_locales + empates_locales + derrotas_locales + victorias_visitantes + empates_visitantes + derrotas_visitantes))
        # Alinear columnas a la izquierda
        for col in ("Tipo", "Victorias", "Empates", "Derrotas"):
            self.treeview.column(col, anchor="w")

        self.treeview.column("#1", width=75)
        self.treeview.column("#2", width=75)
        self.treeview.column("#3", width=75)
        self.treeview.column("#4", width=75)
        self.treeview.column("#5", width=75)
        self.treeview.configure(height=10)

        self.treeview.grid(row = 2, column = 0, padx=10, pady=10)

    def mostrar_clasificacion(self, df_clasificacion):

        self.treeview_clasificacion = ttk.Treeview(self, columns=("Puesto", "Equipo", "Puntos", "Jugados", "Ganados", "Empatados", "Perdidos", "GF", "GC", "DIF"), show="headings")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeview_clasificacion.yview)
        self.treeview_clasificacion.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, rowspan = 2, padx=10, pady=10, sticky="ns")
        self.treeview_clasificacion.heading("#1", text = "#")
        self.treeview_clasificacion.heading("#2", text="Equipo")
        self.treeview_clasificacion.heading("#3", text="Ptos")
        self.treeview_clasificacion.heading("#4", text="J")
        self.treeview_clasificacion.heading("#5", text="V")
        self.treeview_clasificacion.heading("#6", text="E")
        self.treeview_clasificacion.heading("#7", text="D")
        self.treeview_clasificacion.heading("#8", text="GF")
        self.treeview_clasificacion.heading("#9", text="GC")
        self.treeview_clasificacion.heading("#10", text="DIF")


        # Insertar datos en el Treeview
        for i, row in df_clasificacion.iterrows():

            self.treeview_clasificacion.insert("", "end", values=(i, row["Equipo"], row["P"], row["PJ"], row["V"], row["E"], row["D"], row["GF"], row["GC"], row["DIF"]))

        # Alinear columnas a la izquierda
        for col in ("Equipo", "Puntos", "Jugados", "Ganados", "Empatados", "Perdidos", "GF", "GC", "DIF"):
            self.treeview_clasificacion.column(col, anchor="w", width=30)

        self.treeview_clasificacion.column("#1", width=30)

        self.treeview_clasificacion.column("#2", width=200)
        self.treeview_clasificacion.column("#3", width=50)

        self.treeview_clasificacion.configure(height=10)
        self.treeview_clasificacion.grid(row=0, column=2,rowspan = 2, padx=10, pady=10)

        #On double click
        self.treeview_clasificacion.bind("<Double-1>", self.on_double_click)
    def on_double_click(self, event):
        item = self.treeview_clasificacion.selection()[0]
        equipo = self.treeview_clasificacion.item(item, "values")[1]
        self.seleccion.set(equipo)
        self.mostrar_seleccion()

if __name__ == "__main__":
    app = VentanaEquipos()
    app.mainloop()
import json
import sqlite3
import os
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from SH_Stats_back import creacion_df, conexion, funciones_auxiliares



class Competicion:
    """
    Clase que representa una competición
    """
    def __init__(self, lista_urls = [], nombre_bd=None,nombre =None,  competicion_id=None, actualizar_al_iniciar = True, ultima_actualizacion=None):
        """
        Constructor de la clase Competicion
        :param lista_urls: listado de strings con las urls de las páginas de resultados de la competición
        :param nombre_bd: nombre del archivo de la base de datos
        :param nombre: nombre de la competición
        :param competicion_id: id de la competición
        :param actualizar_al_iniciar: booleano que indica si se debe actualizar la base de datos al iniciar
        :param ultima_actualizacion: fecha de la última actualización de la base de datos
        """

        if isinstance(lista_urls, str):
            lista_urls = [lista_urls]
        self.enlaces = lista_urls
        self.nombre = nombre
        self.ultima_actualizacion = ultima_actualizacion
        self.competicion_id = competicion_id
        self.nombre_archivo_bd = nombre_bd
        self.crear_bd()


        if actualizar_al_iniciar:
            self.actualizar_bd()


    def __str__(self):
        return f"Competicion: {self.nombre} - Archivo: {self.nombre_archivo_bd} - Ultima actualizacion: {self.ultima_actualizacion} - Enlaces: {self.enlaces})"
    def __repr__(self):
        return f"Competicion: {self.nombre} - Archivo: {self.nombre_archivo_bd} - Ultima actualizacion: {self.ultima_actualizacion} - Enlaces: {self.enlaces})"

    def add_enlace(self, enlace):
        """
        Añade un enlace a la lista de enlaces de la competición
        :param enlace: enlace a añadir
        :return:
        """
        self.enlaces.append(enlace)

    def get_nombre(self):
        """
        Devuelve el nombre de la competición
        :return: nombre de la competición
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT nombre_competicion FROM Competiciones WHERE competicion_id=?''', (self.competicion_id,))
        nombre = cursor.fetchone()[0]
        conn.close()
        return nombre


    def url_to_JSON(self):
        """
        Devuelve un JSON con los enlaces de la competición
        :return: json con los enlaces de la competición
        """
        return json.dumps(self.enlaces)



    def remove_enlace(self, enlace):
        """
        Elimina un enlace de la lista de enlaces de la competición
        :param enlace: enlace a eliminar
        :return:
        """
        self.enlaces.remove(enlace)

    def to_dict(self):
        """
        Devuelve un diccionario con los atributos de la competición
        :return: diccionario con los atributos de la competición
        """
        return {
            "nombre_competicion": self.nombre,
            "nombre_archivo_bd": self.nombre_archivo_bd,
            "ultima_actualizacion": str(self.ultima_actualizacion),
            "lista_urls": self.enlaces
        }
    def to_json(self):
        """
        Devuelve un JSON con los atributos de la competición
        :return: json con los atributos de la competición
        """
        return json.dumps(self.to_dict())
    def crear_equipos(self, df_partidos, equipos_existentes = []):
        """
        Crea una lista de diccionarios con los equipos de la competición
        :param df_partidos: DataFrame con los partidos de la competición
        :param equipos_existentes: Lista de diccionarios con los equipos existentes
        :return: lista de diccionarios con los equipos de la competición
        """
        def check_in( equipo, lista):
            """
            Comprueba si un equipo está en una lista de equipos. Se considera que un equipo está en la lista si tiene el mismo nombre y temporada
            :param equipo: Equipo a comprobar
            :param lista: Lista de diccionarios con los equipos
            :return: booleano que indica si el equipo está en la lista
            """
            for e in lista:
                if e["nombre"] == equipo["nombre"] and e["temporada"] == equipo["temporada"]:
                   return True
            return False
        equipos = equipos_existentes
        for index, row in df_partidos.iterrows():
            local = {"nombre": row['local'], "liga": row['liga'], "grupo": row['grupo'], "temporada": row['temporada']}
            visitante = {"nombre": row['visitante'], "liga": row['liga'], "grupo": row['grupo'], "temporada": row['temporada']}
            if not check_in(local, equipos):
                equipos.append(local)
            if not check_in(visitante, equipos):
                equipos.append(visitante)

        return equipos


    def crear_bd(self):
        """
        Crea la base de datos si no existe. Si existe, no hace nada
        :return:
        """

        if not os.path.exists(funciones_auxiliares.resource_path("res/panel.db")):
            # Create an empty .db file
            open(funciones_auxiliares.resource_path("res/panel.db"), 'w').close()
            self.crear_tabla_equipos([])
            self.crear_tabla_partidos(pd.DataFrame())




    def actualizar_bd(self):
        """
        Actualiza la base de datos con los enlaces de la competición.
        :return:
        """
        if self.nombre_archivo_bd is None:
            raise Exception("No se ha especificado el nombre del archivo de la base de datos")
        if self.enlaces is None:
            raise Exception("No se han especificado los enlaces de la competición")
        if self.enlaces == []:
            self.crear_tabla_equipos([])
            self.crear_tabla_partidos(pd.DataFrame())


        self.crear_bd()
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Partidos WHERE competicion_id=?''', (self.competicion_id,))
        cursor.execute('''DELETE FROM Equipos WHERE competicion_id=?''', (self.competicion_id,))
        conn.commit()
        conn.close()

        equipos_existentes_dict = []
        listado_df_partidos = []
        for url in self.enlaces:
            mi_soup = conexion.get_soup(url)
            listado_df_partidos.append(creacion_df.get_df_partidos(mi_soup))
            equipos_existentes_dict = self.crear_equipos(listado_df_partidos[-1], equipos_existentes_dict)

        self.crear_tabla_equipos(equipos_existentes_dict)
        df_partidos = pd.concat(listado_df_partidos)
        self.crear_tabla_partidos(df_partidos)
        self.set_ultima_actualizacion(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        print("Base de datos actualizada")

    def set_ultima_actualizacion(self, ultima_actualizacion):
        """
        Actualiza la fecha de la última actualización de la competición
        :param ultima_actualizacion: fecha de la última actualización
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''UPDATE Competiciones SET ultima_actualizacion=? WHERE competicion_id=?''', (ultima_actualizacion, self.competicion_id))
        conn.commit()
        conn.close()
        self.ultima_actualizacion = ultima_actualizacion

    def crear_tabla_equipos(self, equipos):
        """
        Crea la tabla de equipos en la base de datos si no existe. Si existe, inserta los equipos en la tabla
        :param equipos: lista de diccionarios con los equipos a insertar
        :return:
        """

        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;') # Necesario para que funcionen las claves foráneas

        # Crear tabla de Equipos
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Equipos (
                        equipo_id INTEGER PRIMARY KEY,
                        nombre_equipo TEXT,
                        liga TEXT,
                        grupo TEXT,
                        temporada TEXT, 
                        competicion_id INTEGER,
                        FOREIGN KEY (competicion_id) REFERENCES Competiciones(competicion_id) ON DELETE CASCADE
                    )
                ''')

        for equipo in equipos:
            cursor.execute('''INSERT INTO Equipos (nombre_equipo, liga, grupo, temporada, competicion_id) VALUES (?,?,?,?,?)''',
                           (equipo["nombre"], equipo["liga"], equipo["grupo"], equipo["temporada"], self.competicion_id))

        conn.commit()
        conn.close()


    def crear_tabla_partidos(self, df_partidos):
        """
        Crea la tabla de partidos en la base de datos si no existe. Si existe, inserta los partidos en la tabla
        :param df_partidos: DataFrame con los partidos a insertar
        :return:
        """

        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')


        # Crear tabla de Partidos
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Partidos (
                        partido_id INTEGER PRIMARY KEY,
                        equipo_local_id INTEGER,
                        equipo_visitante_id INTEGER,
                        goles_local INTEGER,
                        goles_visitante INTEGER,
                        federacion TEXT,
                        fecha TEXT,
                        competicion_id INTEGER,
                        FOREIGN KEY (equipo_local_id) REFERENCES Equipos(equipo_id) ON DELETE CASCADE
                        FOREIGN KEY (equipo_visitante_id) REFERENCES Equipos(equipo_id) ON DELETE CASCADE
                    )
                ''')

        for index, row in df_partidos.iterrows():
            local = row['local']
            local = self.get_id_equipo(local)
            visitante = row['visitante']
            visitante = self.get_id_equipo(visitante)
            gl = row['gl']
            gv = row['gv']
            fecha = row['fecha']
            federacion = row['federacion']
            cursor.execute('''INSERT INTO Partidos (equipo_local_id, equipo_visitante_id, goles_local, goles_visitante, federacion, fecha, competicion_id) VALUES (?,?,?,?,?,?, ?)''',
                            (local, visitante, gl, gv, federacion, fecha, self.competicion_id))

        conn.commit()
        conn.close()


    def get_id_equipo(self, nombre_equipo):
        """
        Devuelve el id de un equipo a partir de su nombre
        :param nombre_equipo: nombre del equipo
        :return: id del equipo
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT equipo_id FROM Equipos WHERE nombre_equipo=? AND competicion_id=?''', (nombre_equipo, self.competicion_id))
        equipo_id = cursor.fetchone()[0]
        conn.close()
        return equipo_id

    def get_equipos(self):
        """
        Devuelve una lista de objetos de tipo Equipo con los equipos de la competición
        :return: lista de objetos de tipo Equipo con los equipos de la competición
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Equipos WHERE competicion_id=?''', (self.competicion_id,))
        equipos = cursor.fetchall()
        conn.close()
        lista_obj_equipos = []
        for equipo in equipos:
            lista_obj_equipos.append(Equipo(equipo[1], equipo[2], equipo[3], equipo[4]))
        return lista_obj_equipos

    def get_partidos(self):
        """
        Devuelve una lista de objetos de tipo Partido con los partidos de la competición
        :return: lista de objetos de tipo Partido con los partidos de la competición
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        # Use join to get the names of the teams
        cursor.execute('''
            SELECT Partidos.partido_id, EquiposLocal.nombre_equipo AS local, EquiposVisitante.nombre_equipo AS visitante, 
                   Partidos.goles_local,Partidos. goles_visitante,  Partidos.federacion, EquiposLocal.liga, EquiposLocal.grupo,  Partidos.fecha
            FROM Partidos
            JOIN Equipos AS EquiposLocal ON Partidos.equipo_local_id = EquiposLocal.equipo_id
            JOIN Equipos AS EquiposVisitante ON Partidos.equipo_visitante_id = EquiposVisitante.equipo_id
            WHERE EquiposLocal.competicion_id = ? AND EquiposVisitante.competicion_id = ?
        ''', (self.competicion_id, self.competicion_id))

        partidos = cursor.fetchall()
        conn.close()


        listado_obj_partidos = []
        for partido in partidos:
            listado_obj_partidos.append(Partido(local=partido[1], visitante=partido[2], gl=partido[3], gv=partido[4], federacion=partido[5], liga=partido[6], grupo=partido[7], fecha=partido[8]))
        return listado_obj_partidos

    def partidos_to_df(self):
        """
        Devuelve un DataFrame con los partidos de la competición
        :return: DataFrame con los partidos de la competición
        """
        partidos = self.get_partidos()
        listado_partidos = []
        for partido in partidos:
            listado_partidos.append([partido.local, partido.visitante, partido.gl, partido.gv, partido.federacion, partido.liga, partido.grupo, partido.fecha, self.nombre])
        df = pd.DataFrame(listado_partidos, columns=['local', 'visitante', 'gl', 'gv', 'federacion', 'liga', 'grupo', 'fecha', 'competicion'])
        return df



    def get_partidos_equipo(self, nombre_equipo):
        """
        Devuelve una lista de objetos de tipo Partido con los partidos de un equipo
        :param nombre_equipo: nombre del equipo
        :return: lista de objetos de tipo Partido con los partidos del equipo especificado
        """
        if isinstance(nombre_equipo, Equipo):
            nombre_equipo = nombre_equipo.nombre
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''
                    SELECT Partidos.partido_id, EquiposLocal.nombre_equipo AS local, EquiposVisitante.nombre_equipo AS visitante, 
                           Partidos.goles_local, Partidos.goles_visitante,Partidos.federacion, EquiposLocal.liga, EquiposLocal.grupo, Partidos.fecha
                    FROM Partidos
                    JOIN Equipos AS EquiposLocal ON Partidos.equipo_local_id = EquiposLocal.equipo_id
                    JOIN Equipos AS EquiposVisitante ON Partidos.equipo_visitante_id = EquiposVisitante.equipo_id
                    WHERE (EquiposLocal.nombre_equipo = ? OR EquiposVisitante.nombre_equipo = ?) AND EquiposLocal.competicion_id = ? AND EquiposVisitante.competicion_id = ?
                ''', (nombre_equipo, nombre_equipo, self.competicion_id, self.competicion_id))

        partidos = cursor.fetchall()
        conn.close()
        listado_obj_partidos = []
        for partido in partidos:
            listado_obj_partidos.append(Partido(partido[1], partido[2], partido[3], partido[4], partido[5], partido[6], partido[7], partido[8]))
        return listado_obj_partidos

    def get_partidos_equipo_df(self, nombre_equipo):
        """
        Devuelve un DataFrame con los partidos de un equipo
        :param nombre_equipo: nombre del equipo
        :return: DataFrame con los partidos del equipo especificado
        """
        partidos = self.get_partidos_equipo(nombre_equipo)
        listado_partidos = []
        for partido in partidos:
            listado_partidos.append([partido.local, partido.visitante, partido.gl, partido.gv, partido.federacion, partido.liga, partido.grupo, partido.fecha, self.nombre])
        df = pd.DataFrame(listado_partidos, columns=['local', 'visitante', 'gl', 'gv', 'federacion', 'liga', 'grupo', 'fecha', 'competicion'])
        return df

    def get_equipo(self, nombre_equipo):
        """
        Devuelve un objeto de tipo Equipo con los datos de un equipo
        :param nombre_equipo: nombre del equipo
        :return: objeto de tipo Equipo con los datos del equipo especificado
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.nombre_archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Equipos WHERE nombre_equipo=? AND competicion_id=?''', (nombre_equipo, self.competicion_id))
        equipo = cursor.fetchone()
        conn.close()
        equipo = Equipo(equipo[1], equipo[2], equipo[3], equipo[4])
        return equipo

    def get_coeficientes(self, clasificacion_df = None):
        """
        Devuelve un diccionario con los coeficientes de Pearson y Spearman entre los puntos y los GF y GC de los equipos
        :return: diccionario con dos coeficientes de Pearson
        """
        clasificacion_df = self.get_clasificacion() if clasificacion_df is None else clasificacion_df
        coeficientes = {}
        clasificacion_df["gf/part"] = clasificacion_df["gf"] / (clasificacion_df["victorias"] + clasificacion_df["derrotas"] + clasificacion_df["empates"])
        clasificacion_df["gc/part"] = clasificacion_df["gc"] / (clasificacion_df["victorias"] + clasificacion_df["derrotas"] + clasificacion_df["empates"])
        coeficientes["GF_Pearson"] = clasificacion_df['gf/part'].corr(clasificacion_df['puntos'], method='pearson')
        coeficientes["GC_Pearson"] = clasificacion_df['gc/part'].corr(clasificacion_df['puntos'], method='pearson')
        # coeficientes["GF_Spearman"] = clasificacion_df['gf'].corr(clasificacion_df['puntos'], method='spearman')
        # coeficientes["GC_Spearman"] = clasificacion_df['gc'].corr(clasificacion_df['puntos'], method='spearman')
        return coeficientes

    def get_clasificacion(self):
        """
        Devuelve un DataFrame con la clasificación de la competición
        :return: DataFrame con la clasificación de la competición
        """
        equipos = self.get_equipos()
        listado_equipos = []
        for equipo in equipos:
            partidos = self.get_partidos_equipo(equipo)

            gf = 0
            gc = 0
            victorias = 0
            derrotas = 0
            empates = 0
            for partido in partidos:
                if partido.local == equipo.nombre: # es local
                    gf += partido.gl
                    gc += partido.gv
                    if partido.gl > partido.gv:
                        victorias += 1
                    elif partido.gl < partido.gv:
                        derrotas += 1
                    else:
                        empates += 1
                else: # es visitante
                    gf += partido.gv
                    gc += partido.gl
                    if partido.gl > partido.gv:
                        derrotas += 1
                    elif partido.gl < partido.gv:
                        victorias += 1
                    else:
                        empates += 1
            listado_equipos.append((equipo.nombre, equipo.liga, equipo.grupo, equipo.temporada, gf, gc, victorias, derrotas, empates))

        # Create df
        df = pd.DataFrame(listado_equipos, columns=['nombre', 'liga', 'grupo', 'temporada', 'gf', 'gc', 'victorias', 'derrotas', 'empates'])
        df['puntos'] = df['victorias'] * 2 + df['empates']
        df['dif_goles'] = df['gf'] - df['gc']
        df = df.sort_values(by=['puntos', 'dif_goles'], ascending=False)
        df.index.name = 'Puesto'
        for i, index in enumerate(df.index):
            df = df.rename(index={index: str(i + 1) + '. '})
        return df

    def get_datos_equipo_local(self, equipo):
        """
        Devuelve un diccionario con el número de victorias, derrotas y empates de un equipo como local
        :param equipo: objeto de tipo Equipo
        :return: diccionario con el número de victorias, derrotas y empates de un equipo como local
        """
        partidos = self.get_partidos_equipo(equipo)
        victorias = 0
        derrotas = 0
        empates = 0
        for partido in partidos:
            if partido.local == equipo.nombre:
                if partido.gl > partido.gv:
                    victorias += 1
                elif partido.gl < partido.gv:
                    derrotas += 1
                else:
                    empates += 1
        return {"victorias": victorias, "derrotas": derrotas, "empates": empates}

    def get_datos_equipo_visitante(self, equipo):
        """
        Devuelve un diccionario con el número de victorias, derrotas y empates de un equipo como visitante
        :param equipo: objeto de tipo Equipo
        :return: diccionario con el número de victorias, derrotas y empates de un equipo como visitante
        """
        partidos = self.get_partidos_equipo(equipo)
        victorias = 0
        derrotas = 0
        empates = 0
        for partido in partidos:
            if partido.visitante == equipo.nombre:
                if partido.gl > partido.gv:
                    derrotas += 1
                elif partido.gl < partido.gv:
                    victorias += 1
                else:
                    empates += 1
        return {"victorias": victorias, "derrotas": derrotas, "empates": empates}

    def get_estadisticas_equipo(self, equipo, df_partidos=None, df_clasificacion=None):
        """
        Devuelve un diccionario con las estadísticas de un equipo. Las estadísticas son:
        - Media de goles a favor
        - Media de goles en contra
        - Desviación estándar de goles a favor
        - Desviación estándar de goles en contra
        - Número de victorias como local
        - Número de derrotas como local
        - Número de empates como local
        - Número de victorias como visitante
        - Número de derrotas como visitante
        - Número de empates como visitante
        - Número de victorias
        - Número de derrotas
        - Número de empates
        - Mayor racha de victorias
        - Mayor racha de derrotas
        - Mayor racha de empates
        - Últimos 5 partidos
        - Número de goles en las victorias
        - Número de goles en las derrotas
        - Mejor victoria
        - Peor derrota
        - Mejor diferencia de goles
        - Peor diferencia de goles
        - Clasificación
        - Goles a favor esperados (regresión lineal)
        - Goles en contra esperados (regresión lineal)
        - Goles a favor por partido esperados (regresión lineal)
        - Goles en contra por partido esperados (regresión lineal)

        :param equipo: objeto de tipo Equipo del que se quieren obtener las estadísticas
        :param df_partidos: DataFrame con los partidos de la competición
        :param df_clasificacion: DataFrame con la clasificación de la competición
        :return: diccionario con las estadísticas del equipo
        """

        #Datos como locales y visitantes
        dict_datos_locales = self.get_datos_equipo_local(equipo)
        victorias_locales = dict_datos_locales["victorias"]
        derrotas_locales = dict_datos_locales["derrotas"]
        empates_locales = dict_datos_locales["empates"]
        dict_datos_visitantes = self.get_datos_equipo_visitante(equipo)
        victorias_visitantes = dict_datos_visitantes["victorias"]
        derrotas_visitantes = dict_datos_visitantes["derrotas"]
        empates_visitantes = dict_datos_visitantes["empates"]

        # Creamos las listas de goles, victorias, derrotas y empates
        partidos = self.get_partidos_equipo(equipo)
        gf = []
        gc = []
        victorias = []
        derrotas = []
        empates = []
        gf_en_victorias = []
        gc_en_victorias = []
        gt_y_diferencia = []
        mejor_victoria = None
        mejor_diferencia = 0
        peor_derrota = None
        peor_diferencia = 0

        for partido in partidos:
            if partido.local == equipo.nombre: # es local
                gf.append(partido.gl)
                gc.append(partido.gv)
                gt_y_diferencia.append((partido.gl + partido.gv, partido.gl - partido.gv))
                if partido.gl > partido.gv: # victoria
                    gf_en_victorias.append(partido.gl)
                    gc_en_victorias.append(partido.gv)
                    victorias.append(1)
                    derrotas.append(0)
                    empates.append(0)
                    if mejor_victoria is None:
                        mejor_victoria = partido
                    elif partido.gl - partido.gv > mejor_diferencia:
                        mejor_victoria = partido
                        mejor_diferencia = partido.gl - partido.gv

                elif partido.gl < partido.gv: # derrota
                    victorias.append(0)
                    derrotas.append(1)
                    empates.append(0)
                    if peor_derrota is None:
                        peor_derrota = partido
                    elif partido.gl - partido.gv < peor_diferencia:
                        peor_derrota = partido
                        peor_diferencia = partido.gl - partido.gv
                else: # empate

                    victorias.append(0)
                    derrotas.append(0)
                    empates.append(1)
            else: # es visitante

                gf.append(partido.gv)
                gc.append(partido.gl)
                gt_y_diferencia.append((partido.gl + partido.gv, partido.gv - partido.gl))
                if partido.gl > partido.gv: # derrota

                    victorias.append(0)
                    derrotas.append(1)
                    empates.append(0)
                    if peor_derrota is None:
                        peor_derrota = partido
                    elif partido.gv - partido.gl < peor_diferencia:
                        peor_derrota = partido
                        peor_diferencia = partido.gv - partido.gl


                elif partido.gl < partido.gv: # victoria
                    gf_en_victorias.append(partido.gv)
                    gc_en_victorias.append(partido.gl)
                    victorias.append(1)
                    derrotas.append(0)
                    empates.append(0)
                    if mejor_victoria is None:
                        mejor_victoria = partido
                    elif partido.gv - partido.gl > mejor_diferencia:
                        mejor_victoria = partido
                        mejor_diferencia = partido.gv - partido.gl
                else: # empate
                    victorias.append(0)
                    derrotas.append(0)
                    empates.append(1)
        mayor_racha_victorias = 0
        mayor_racha_derrotas = 0
        mayor_racha_empates = 0

        # Calculamos media de goles y desviacion estandar
        avg_gf = np.average(gf)
        avg_gf = round(avg_gf, 2)
        avg_gc = np.average(gc)
        avg_gc = round(avg_gc, 2)
        std_gf = np.std(gf)
        std_gf = round(std_gf, 2)
        std_gc = np.std(gc)
        std_gc = round(std_gc, 2)



        # Calculamos las rachas
        for i, victoria in enumerate(victorias):
            if victoria == 1:
                racha = 1
                for j in range(i + 1, len(victorias)):
                    if victorias[j] == 1:
                        racha += 1
                    else:
                        break
                if racha > mayor_racha_victorias:
                    mayor_racha_victorias = racha
            elif derrotas[i] == 1:
                racha = 1
                for j in range(i + 1, len(victorias)):
                    if derrotas[j] == 1:
                        racha += 1
                    else:
                        break
                if racha > mayor_racha_derrotas:
                    mayor_racha_derrotas = racha
            else:
                racha = 1
                for j in range(i + 1, len(victorias)):
                    if empates[j] == 1:
                        racha += 1
                    else:
                        break
                if racha > mayor_racha_empates:
                    mayor_racha_empates = racha

        # Últimos 5 partidos
        ultimos_5_partidos = partidos[-5:]
        victorias_ultimos_5 = 0
        derrotas_ultimos_5 = 0
        empates_ultimos_5 = 0
        gf_ultimos_5 = []
        gc_ultimos_5 = []
        for partido in ultimos_5_partidos:
            if partido.local == equipo.nombre:
                gf_ultimos_5.append(partido.gl)
                gc_ultimos_5.append(partido.gv)
                if partido.gl > partido.gv:
                    victorias_ultimos_5 += 1
                elif partido.gl < partido.gv:
                    derrotas_ultimos_5 += 1
                else:
                    empates_ultimos_5 += 1
            else:
                gf_ultimos_5.append(partido.gv)
                gc_ultimos_5.append(partido.gl)
                if partido.gl > partido.gv:
                    derrotas_ultimos_5 += 1
                elif partido.gl < partido.gv:
                    victorias_ultimos_5 += 1
                else:
                    empates_ultimos_5 += 1
        avg_gf_ultimos_5 = np.average(gf_ultimos_5)
        avg_gf_ultimos_5 = round(avg_gf_ultimos_5, 2)
        avg_gc_ultimos_5 = np.average(gc_ultimos_5)
        avg_gc_ultimos_5 = round(avg_gc_ultimos_5, 2)
        std_gf_ultimos_5 = np.std(gf_ultimos_5)
        std_gf_ultimos_5 = round(std_gf_ultimos_5, 2)
        std_gc_ultimos_5 = np.std(gc_ultimos_5)
        std_gc_ultimos_5 = round(std_gc_ultimos_5, 2)

        # Clasicacion
        clasificacion = self.get_clasificacion() if df_clasificacion is None else df_clasificacion
        puesto = clasificacion[clasificacion['nombre'] == equipo.nombre].index[0]
        puesto = int(puesto.split(".")[0])
        goles_esperados = self.get_goles_esperados(puesto, clasificacion)
        gf_esperados_por_partido = goles_esperados["gf"]
        gc_esperados_por_partido = goles_esperados["gc"]

        return {"avg_gf": avg_gf, "avg_gc": avg_gc, "std_gf": std_gf, "std_gc": std_gc,
                "gf": gf, "gc": gc, "victorias": victorias, "derrotas": derrotas, "empates": empates,
                "victorias_visitantes": victorias_visitantes, "derrotas_visitantes": derrotas_visitantes,
                "empates_visitantes": empates_visitantes, "victorias_locales": victorias_locales, "derrotas_locales": derrotas_locales,
                "empates_locales": empates_locales,
                "mayor_racha_victorias": mayor_racha_victorias, "mayor_racha_derrotas": mayor_racha_derrotas,
                "mayor_racha_empates": mayor_racha_empates,
                "gf_en_victorias": gf_en_victorias, "gc_en_victorias": gc_en_victorias,
                "gt_y_diferencia": gt_y_diferencia,
                "mejor_victoria": mejor_victoria, "peor_derrota": peor_derrota,
                "victorias_ultimos_5": victorias_ultimos_5, "derrotas_ultimos_5": derrotas_ultimos_5, "empates_ultimos_5": empates_ultimos_5,
                "avg_gf_ultimos_5": avg_gf_ultimos_5, "avg_gc_ultimos_5": avg_gc_ultimos_5, "std_gf_ultimos_5": std_gf_ultimos_5, "std_gc_ultimos_5": std_gc_ultimos_5,
                "puesto": puesto,
                "gf_esperados_por_partido": gf_esperados_por_partido, "gc_esperados_por_partido": gc_esperados_por_partido}

    def get_goles_esperados(self, puesto, clasificacion_df = None):
        """
        Devuelve los valores de GF por partido y GC por partido esperados dados el puesto. Se calculan a partir de una regresión linea
        :param puesto: puesto en la clasificación
        :param clasificacion_df: DataFrame con la clasificación de la competición
        :return: Diccionario con los valores de GF y GC esperados
        """
        clasificacion = self.get_clasificacion() if clasificacion_df is None else clasificacion_df

        X = []
        for i in range(1, len(clasificacion.index) + 1):
            X.append(i)
        Y = []
        Z = []
        for index, row in clasificacion.iterrows():
            Y.append(row['gf'] / (row['victorias'] + row['derrotas'] + row['empates']))
            Z.append(row['gc'] / (row['victorias'] + row['derrotas'] + row['empates']))
        coef = np.polyfit(X, Y, 1)
        poly1d_fn = np.poly1d(coef)
        gf_esperados = round(poly1d_fn(puesto), 2)
        coef = np.polyfit(X, Z, 1)
        poly1d_fn = np.poly1d(coef)
        gc_esperados = round(poly1d_fn(puesto), 2)
        return {"gf": gf_esperados, "gc": gc_esperados}


    def get_estadisticas_competicion(self):
        """
        Devuelve un diccionario con las estadísticas de la competición. Las estadísticas son:
        - Número de equipos
        - Número de partidos
        - Número de victorias locales
        - Número de victorias visitantes
        - Número de empates
        - Media de goles por partido
        - Desviación estándar de goles por partido
        - Media de goles de los ganadores
        - Desviación estándar de goles de los ganadores
        - Media de goles de los perdedores
        - Desviación estándar de goles de los perdedores
        - Lista con los goles por partido
        - Lista con los goles de los ganadores
        - Lista con los goles de los perdedores

        :return: diccionario con las estadísticas de la competición
        """
        equipos = self.get_equipos()
        partidos = self.get_partidos()

        victorias_locales = 0
        victorias_visitantes = 0
        empates = 0
        goles_por_partido = []
        goles_ganadores = []
        goles_perdedores = []

        for partido in partidos:
            goles_por_partido.append(partido.gl + partido.gv)
            if partido.gl > partido.gv:
                goles_ganadores.append(partido.gl)
                goles_perdedores.append(partido.gv)
                victorias_locales += 1
            elif partido.gl < partido.gv:
                goles_ganadores.append(partido.gv)
                goles_perdedores.append(partido.gl)
                victorias_visitantes += 1
            else:
                empates += 1



        return {"numero_equipos": len(equipos), "numero_partidos": len(partidos),
                "victorias_locales": victorias_locales, "victorias_visitantes": victorias_visitantes,
                "empates": empates,
                "media_goles_por_partido": round(np.average(goles_por_partido), 2),
                "std_goles_por_partido": round(np.std(goles_por_partido), 2),
                "goles_por_partido": goles_por_partido, "goles_ganadores": goles_ganadores,
                "goles_perdedores": goles_perdedores,
                "media_goles_ganadores": round(np.average(goles_ganadores), 2),
                "std_goles_ganadores": round(np.std(goles_ganadores), 2),
                "media_goles_perdedores": round(np.average(goles_perdedores), 2),
                "std_goles_perdedores": round(np.std(goles_perdedores), 2)}


class Equipo:
    """
    Clase que representa a un equipo
    """
    def __init__(self, nombre, liga, grupo, temporada):
        """
        Constructor de la clase Equipo
        :param nombre: nombre del equipo
        :param liga: liga del equipo
        :param grupo: grupo del equipo
        :param temporada:
        """
        self.nombre = nombre
        self.liga = liga
        self.grupo = grupo
        self.temporada = temporada
        self.partidos = []

    def __str__(self):
        return f"Equipo: {self.nombre} - Liga: {self.liga} - Grupo: {self.grupo} - Temporada: {self.temporada}"
    def __repr__(self):
        return f"Equipo: {self.nombre} - Liga: {self.liga} - Grupo: {self.grupo} - Temporada: {self.temporada}"


class Partido:
    """
    Clase que representa a un partido
    """
    def __init__(self, local = None, visitante = None, gl = 0, gv=  0, federacion = None, liga = None, grupo = None, fecha = None):
        """
        Constructor de la clase Partido
        :param local:
        :param visitante:
        :param gl: Goles local
        :param gv: Goles visitante
        :param federacion:
        :param liga:
        :param grupo:
        :param fecha:
        """
        self.local = local
        self.visitante = visitante
        self.gl = gl
        self.gv = gv
        self.federacion = federacion
        self.liga = liga
        self.grupo = grupo
        self.fecha = fecha
    def __str__(self):
        return f"Partido: {self.local} - {self.gl} - {self.gv} - {self.visitante} - {self.federacion} - {self.liga} - {self.grupo} - {self.fecha}"
    def __repr__(self):
        return f"Partido: {self.local} - {self.gl} - {self.gv} - {self.visitante} - {self.federacion} - {self.liga} - {self.grupo} - {self.fecha}"



class Panel:
    """
    Clase que representa al panel de competiciones. Un panel de competiciones es un objeto que contiene una lista de
    competiciones y que permite añadir, eliminar y modificar competiciones.
    """
    def __init__(self, archivo_bd = None, lista_competiciones = []):
        """
        Constructor de la clase Panel
        :param archivo_bd: Archivo de la base de datos
        :param lista_competiciones: Lista de competiciones
        """
        self.lista_competiciones = lista_competiciones
        self.archivo_bd = "res/panel.db" # Archivo de la base de datos
        self.crear_tabla_panel()

    def add_competicion(self, competicion):
        """
        Añade una competición al panel
        :param competicion: objeto de tipo Competicion
        :return:
        """



        if isinstance(competicion, Competicion):
            print("Añadiendo competición al panel")

            competicion.crear_tabla_equipos([])
            #empty dataframe
            competicion.crear_tabla_partidos(pd.DataFrame(columns=['local', 'visitante', 'gl', 'gv', 'federacion', 'liga', 'grupo', 'fecha', 'competicion']))
            conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
            cursor = conn.cursor()
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor.execute('''INSERT INTO Competiciones (nombre_competicion, nombre_archivo_bd, lista_urls, ultima_actualizacion) VALUES (?,?,?,?)''',
                           (competicion.nombre, competicion.nombre_archivo_bd, competicion.url_to_JSON(), competicion.ultima_actualizacion))

            conn.commit()
            conn.close()
        else:
            raise Exception("Se ha intentado añadir al panel una competición que no es de tipo Competicion")

    def crear_tabla_panel(self):
        """
        Crea la tabla de competiciones en la base de datos si no existe
        :return:
        """
        if not os.path.exists(funciones_auxiliares.resource_path(self.archivo_bd)):
            # Create an empty .db file
            open(funciones_auxiliares.resource_path(self.archivo_bd), 'w').close()
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')

        # Crear tabla de Competiciones
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Competiciones (
                        competicion_id INTEGER PRIMARY KEY,
                        nombre_competicion TEXT,
                        nombre_archivo_bd TEXT,
                        lista_urls JSON,
                        ultima_actualizacion DATE
                    )
                ''')
        conn.commit()
        conn.close()


    def actualizar_tabla_panel(self):
        """
        Actualiza la tabla de competiciones en la base de datos. Borra todas las competiciones y las vuelve a añadir
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = OFF;') # Desactivar las foreign keys para poder actualizar las competiciones
        cursor.execute('''DELETE FROM Competiciones''')
        competiciones =self.get_competiciones()
        for competicion in competiciones:
            cursor.execute('''INSERT INTO Competiciones (nombre_competicion, nombre_archivo_bd, lista_urls, ultima_actualizacion) VALUES (?,?,?,?)''',
                           (competicion.nombre, competicion.nombre_archivo_bd, competicion.url_to_JSON(), competicion.ultima_actualizacion))
        conn.commit()
        conn.close()

    def get_id_competicion(self, nombre_competicion):
        """
        Devuelve el id de una competición a partir de su nombre
        :param nombre_competicion: nombre de la competición
        :return: id de la competición
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT competicion_id FROM Competiciones WHERE nombre_competicion=?''', (nombre_competicion,))
        competicion_id = cursor.fetchone()[0]
        conn.close()
        return competicion_id

    def get_competicion(self, nombre_competicion):
        """
        Devuelve un objeto de tipo Competicion a partir de su nombre
        :param nombre_competicion: nombre de la competición
        :return: objeto de tipo Competicion
        """
        self.lista_competiciones = self.get_competiciones()
        for competicion in self.lista_competiciones:
            if competicion.nombre == nombre_competicion:
                return competicion
        return None

    def annadir_enlace_a_competicion(self, nombre_competicion, enlace):
        """
        Añade un enlace a una competición. Preprocesa el enlace para que sea válido. El enlace debe contener los parámetros "seleccion" e "id"
        :param nombre_competicion: nombre de la competición
        :param enlace: enlace a añadir
        :return:
        """

        # Preprocesar el enlace
        if ("id=" not in enlace) or ("seleccion=" not in enlace):

            soup = conexion.get_soup(enlace)
            etiqueta = soup.find_all('div', class_='capa_jornada btn-default')
            seleccion = etiqueta[0].a['href'].split("seleccion=")[1].split("&")[0]
            id = etiqueta[0].a['href'].split("id=")[1].split("&")[0]

        else:
            seleccion = enlace.split("seleccion=")[1].split("&")[0]
            id = enlace.split("id=")[1].split("&")[0]

        nuevo_enlace = f"https://www.rfebm.com/competiciones/resultados_completos.php?seleccion={seleccion}&id={id}"


        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        competicion_id = self.get_id_competicion(nombre_competicion)
        cursor.execute('''SELECT lista_urls FROM Competiciones WHERE competicion_id=?''', (competicion_id,))
        lista_urls = cursor.fetchone()[0]
        lista_urls = json.loads(lista_urls)
        lista_urls.append(nuevo_enlace)
        cursor.execute('''UPDATE Competiciones SET lista_urls=? WHERE competicion_id=?''', (json.dumps(lista_urls), competicion_id))
        conn.commit()
        conn.close()
        

    def set_enlaces_a_competicion(self, nombre_competicion, lista_enlaces):
        """
        Modifica los enlaces de una competición
        :param nombre_competicion: nombre de la competición
        :param lista_enlaces: lista de enlaces a añadir
        :return:
        """
        competicion = self.get_competicion(nombre_competicion)
        competicion.enlaces = lista_enlaces
        self.actualizar_competicion(competicion)
        self.actualizar_tabla_panel()

    def eliminar_enlace_a_competicion(self, nombre_competicion, enlace):
        """
        Elimina un enlace de una competición
        :param nombre_competicion: nombre de la competición
        :param enlace: enlace a eliminar
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        competicion_id = self.get_id_competicion(nombre_competicion)
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT lista_urls FROM Competiciones WHERE competicion_id=?''', (competicion_id,))
        lista_urls = cursor.fetchone()[0]
        lista_urls = json.loads(lista_urls)
        lista_urls.remove(enlace)
        cursor.execute('''UPDATE Competiciones SET lista_urls=? WHERE competicion_id=?''', (json.dumps(lista_urls), competicion_id))
        conn.commit()
        conn.close()


    def eliminar_enlaces_a_competicion(self, nombre_competicion):
        """
        Elimina todos los enlaces de una competición
        :param nombre_competicion: nombre de la competición
        :return:
        """
        competicion = self.get_competicion(nombre_competicion)
        competicion.enlaces = []
        self.actualizar_competicion(competicion)
        self.actualizar_tabla_panel()

    def set_fecha_ultima_actualizacion(self, nombre_competicion, fecha):
        """
        Modifica la fecha de la última actualización de una competición
        :param nombre_competicion: nombre de la competición
        :param fecha: fecha de la última actualización
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        competicion_id = self.get_id_competicion(nombre_competicion)
        cursor.execute('''UPDATE Competiciones SET ultima_actualizacion=? WHERE competicion_id=?''', (fecha, competicion_id))
        conn.commit()
        conn.close()

    def get_competiciones(self):
        """
        Devuelve una lista de objetos de tipo Competicion con las competiciones del panel
        :return: lista con las competiciones del panel
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Competiciones''')
        competiciones = cursor.fetchall()
        conn.close()
        lista_obj_competiciones = []
        for competicion in competiciones:
            lista_obj_competiciones.append(Competicion(lista_urls= json.loads(competicion[3]), nombre_bd=self.archivo_bd, nombre=competicion[1], competicion_id=competicion[0], actualizar_al_iniciar=False, ultima_actualizacion=competicion[4]))
        return lista_obj_competiciones

    def actualizar_competiciones(self):
        """
        Actualiza todas las competiciones del panel
        :return:
        """
        competiciones = self.get_competiciones()
        for competicion in competiciones:
            self.actualizar_competicion(competicion)

    def actualizar_competicion(self, competicion):
        """
        Actualiza una competición del panel
        :param competicion: objeto de tipo Competicion
        :return:
        """
        if isinstance(competicion, Competicion):
            competicion.actualizar_bd()
        else:
            competicion = self.get_competicion(competicion)

            competicion.actualizar_bd()
        self.actualizar_tabla_panel()



    def eliminar_competicion(self, competicion):
        """
        Elimina una competición del panel
        :param competicion: objeto de tipo Competicion
        :return:
        """
        if isinstance(competicion, Competicion):
            nombre = competicion.nombre
        else:
            nombre = competicion
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones WHERE nombre_competicion=?''', (nombre,))
        conn.commit()
        conn.close()

    def eliminar_competicion_por_nombre(self, nombre_competicion):
        """
        Elimina una competición del panel a partir de su nombre
        :param nombre_competicion: nombre de la competición
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones WHERE nombre_competicion=?''', (nombre_competicion,))
        conn.commit()
        conn.close()

    def eliminar_competicion_por_id(self, competicion_id):
        """
        Elimina una competición del panel a partir de su id
        :param competicion_id: id de la competición
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones WHERE competicion_id=?''', (competicion_id,))
        conn.commit()
        conn.close()

    def eliminar_competiciones(self):
        """
        Elimina todas las competiciones del panel
        :return:
        """
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones''')
        conn.commit()
        conn.close()

    def get_estadisticas_competicion(self, competicion):
        """
        Devuelve un diccionario con las estadísticas de una competición
        :param competicion: objeto de tipo Competicion
        :return:
        """
        if isinstance(competicion, Competicion):
            competicion = competicion.nombre
        competicion = self.get_competicion(competicion)
        return competicion.get_estadisticas_competicion()
    def competiciones_to_df(self):
        """
        Devuelve un dataframe con las estadísticas de todas las competiciones del panel. Las estadísticas son:
        - Nombre de la competición
        - Número de equipos
        - Número de partidos
        - Número de victorias locales
        - Número de victorias visitantes
        - Número de empates
        - Media de goles por partido
        - Desviación estándar de goles por partido
        - Media de goles de los ganadores
        - Desviación estándar de goles de los ganadores
        - Media de goles de los perdedores
        - Desviación estándar de goles de los perdedores

        :return: dataframe con las estadísticas de todas las competiciones del panel
        """
        competiciones = self.get_competiciones()
        listado_competiciones = []
        for competicion in competiciones:
            estadisticas = competicion.get_estadisticas_competicion()
            listado_competiciones += [[competicion.nombre, estadisticas["numero_equipos"], estadisticas["numero_partidos"],
                                        estadisticas["victorias_locales"], estadisticas["victorias_visitantes"],
                                        estadisticas["empates"], estadisticas["media_goles_por_partido"],
                                        estadisticas["std_goles_por_partido"], estadisticas["media_goles_ganadores"],
                                        estadisticas["std_goles_ganadores"], estadisticas["media_goles_perdedores"],
                                        estadisticas["std_goles_perdedores"]]]
        df = pd.DataFrame(listado_competiciones, columns=['nombre', 'numero_equipos', 'numero_partidos', 'victorias_locales',
                                                          'victorias_visitantes', 'empates', 'media_goles_por_partido',
                                                          'std_goles_por_partido', 'media_goles_ganadores',
                                                          'std_goles_ganadores', 'media_goles_perdedores',
                                                          'std_goles_perdedores'])
        return df
    def partidos_to_df(self):
        """
        Devuelve un dataframe con todos los partidos de todas las competiciones del panel. Las columnas son:
        - Local
        - Goles local
        - Goles visitante
        - Visitante
        - Federación
        - Liga
        - Grupo
        - Fecha
        - Competición

        :return: dataframe con todos los partidos de todas las competiciones del panel
        """

        dataframes = []
        for competicion in self.get_competiciones():
            dataframes.append(competicion.partidos_to_df())
        return pd.concat(dataframes)

    def modificar_nombre_competicion(self, competicion, nuevo_nombre):
        """
        Modifica el nombre de una competición
        :param competicion: objeto de tipo Competicion
        :param nuevo_nombre: nuevo nombre de la competición
        :return: None
        """
        if isinstance(competicion, Competicion):
            competicion = competicion.nombre
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''UPDATE Competiciones SET nombre_competicion=? WHERE nombre_competicion=?''', (nuevo_nombre, competicion))
        conn.commit()
        conn.close()

    def modificar_enlace_a_competicion(self, competicion, enlace, nuevo_enlace):
        """
        Modifica un enlace de una competición
        :param competicion: objeto de tipo Competicion
        :param enlace: enlace a modificar
        :param nuevo_enlace: nuevo enlace por el que se sustituye el anterior
        :return:
        """
        if isinstance(competicion, Competicion):
            competicion = competicion.nombre
        conn = sqlite3.connect(funciones_auxiliares.resource_path(self.archivo_bd))
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        competicion_id = self.get_id_competicion(competicion)
        cursor.execute('''SELECT lista_urls FROM Competiciones WHERE competicion_id=?''', (competicion_id,))
        lista_urls = cursor.fetchone()[0]
        lista_urls = json.loads(lista_urls)
        lista_urls.remove(enlace)
        lista_urls.append(nuevo_enlace)
        cursor.execute('''UPDATE Competiciones SET lista_urls=? WHERE competicion_id=?''', (json.dumps(lista_urls), competicion_id))
        conn.commit()
        conn.close()





    def __str__(self):
        competiciones = self.get_competiciones()
        return f"Panel: {self.archivo_bd} - Competiciones: {competiciones}"
    def __repr__(self):
        competiciones = self.get_competiciones()
        return f"Panel: {self.archivo_bd} - Competiciones: {competiciones}"
    def to_dict(self):
        """
        Devuelve un diccionario con la información del panel
        :return: diccionario con la información del panel
        """
        competiciones = self.get_competiciones()
        dict_lista_competiciones = []

        for competicion in competiciones:
            dict_lista_competiciones.append(competicion.to_json())
        return {
            "archivo": self.archivo_bd,
            "lista_competiciones": dict_lista_competiciones
        }
    def to_json(self):
        """
        Devuelve un string en formato JSON con la información del panel
        :return:
        """
        return json.dumps(self.to_dict())

def competicion_from_json(json_string):
    """
    Devuelve un objeto de tipo Competicion a partir de un string en formato JSON
    :param json_string: string en formato JSON
    :return: objeto de tipo Competicion
    """
    diccionario = json.loads(json_string)
    return Competicion( lista_urls=diccionario["lista_urls"],
                        nombre_bd=diccionario["nombre_archivo_bd"],
                        nombre=diccionario["nombre_competicion"],
                        ultima_actualizacion=diccionario["ultima_actualizacion"],
                        actualizar_al_iniciar=False)
def panel_from_json(json_string):
    """
    Devuelve un objeto de tipo Panel a partir de un string en formato JSON
    :param json_string: string en formato JSON
    :return: objeto de tipo Panel
    """

    diccionario = json.loads(json_string)


    for i, competicion in enumerate(diccionario["lista_competiciones"]):
        diccionario["lista_competiciones"][i] = competicion_from_json(competicion)
    return Panel(diccionario["nombre"], diccionario["lista_competiciones"])



def panel_from_db(ruta_abs, ruta_rel):
    """
    Devuelve un objeto de tipo Panel a partir de un archivo de base de datos
    :param nombre_archivo: nombre del archivo de base de datos
    :return: objeto de tipo Panel
    """
    conn = sqlite3.connect(ruta_abs)
    cursor = conn.cursor()
    try:
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Competiciones''')
        competiciones = cursor.fetchall()
        conn.close()
        lista_obj_competiciones = []
        for competicion in competiciones:
            lista_obj_competiciones.append(
                Competicion(lista_urls=json.loads(competicion[3]), nombre_bd=ruta_rel, nombre=competicion[1],
                            competicion_id=competicion[0], actualizar_al_iniciar=False,
                            ultima_actualizacion=competicion[4]))
        return Panel(ruta_rel, lista_obj_competiciones)

    except sqlite3.OperationalError:
        conn.close()
        print("Error en panel_from_db")
        return Panel(ruta_rel)



if __name__ == "__main__":
    mi_panel = panel_from_db("panel.db", "panel.db")
    mi_panel.actualizar_competiciones()
    mi_compe = mi_panel.get_competiciones()[0]
    partidos = mi_compe.get_partidos()
    equipos = mi_compe.get_equipos()

    print(mi_compe.get_estadisticas_competicion())
    for equipo in equipos:
        print(equipo)






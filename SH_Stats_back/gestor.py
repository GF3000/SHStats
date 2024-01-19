import json
import sqlite3
import os
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from SH_Stats_back import creacion_df, conexion



class Competicion:
    def __init__(self, lista_urls = [], nombre_bd=None,nombre =None,  competicion_id=None, actualizar_al_iniciar = True, ultima_actualizacion=None):
        if isinstance(lista_urls, str):
            lista_urls = [lista_urls]
        self.enlaces = lista_urls
        self.nombre = nombre
        self.ultima_actualizacion = ultima_actualizacion
        self.competicion_id = competicion_id
        self.nombre_archivo_bd = nombre_bd #if nombre_bd else "db/" + nombre.replace(" ", "_") + ".db"
        self.crear_bd()

        if actualizar_al_iniciar:
            self.actualizar_bd()


    def __str__(self):
        return f"Competicion: {self.nombre} - Archivo: {self.nombre_archivo_bd} - Ultima actualizacion: {self.ultima_actualizacion} - Enlaces: {self.enlaces})"
    def __repr__(self):
        return f"Competicion: {self.nombre} - Archivo: {self.nombre_archivo_bd} - Ultima actualizacion: {self.ultima_actualizacion} - Enlaces: {self.enlaces})"

    def add_enlace(self, enlace):
        self.enlaces.append(enlace)

    def get_nombre(self):
        conn = sqlite3.connect(self.nombre_archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT nombre_competicion FROM Competiciones WHERE competicion_id=?''', (self.competicion_id,))
        nombre = cursor.fetchone()[0]
        conn.close()
        return nombre


    def url_to_JSON(self):
        return json.dumps(self.enlaces)



    def remove_enlace(self, enlace):
        self.enlaces.remove(enlace)

    def to_dict(self):
        return {
            "nombre_competicion": self.nombre,
            "nombre_archivo_bd": self.nombre_archivo_bd,
            "ultima_actualizacion": str(self.ultima_actualizacion),
            "lista_urls": self.enlaces
        }
    def to_json(self):
        return json.dumps(self.to_dict())
    def crear_equipos(self, df_partidos):
        equipos = []
        for index, row in df_partidos.iterrows():
            local = {"nombre": row['local'], "liga": row['liga'], "grupo": row['grupo'], "temporada": row['temporada']}
            visitante = {"nombre": row['visitante'], "liga": row['liga'], "grupo": row['grupo'], "temporada": row['temporada']}
            if local not in equipos:
                equipos.append(local)
            if visitante not in equipos:
                equipos.append(visitante)
        return equipos


    def crear_bd(self):
        if not os.path.exists(self.nombre_archivo_bd):
            # Create an empty .db file
            open(self.nombre_archivo_bd, 'w').close()
            self.crear_tabla_equipos([])
            self.crear_tabla_partidos(pd.DataFrame())




    def actualizar_bd(self):
        if self.nombre_archivo_bd is None:
            raise Exception("No se ha especificado el nombre del archivo de la base de datos")
        if self.enlaces is None:
            raise Exception("No se han especificado los enlaces de la competición")
        if self.enlaces == []:
            self.crear_tabla_equipos([])
            self.crear_tabla_partidos(pd.DataFrame())


        self.crear_bd()
        conn = sqlite3.connect(self.nombre_archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Partidos WHERE competicion_id=?''', (self.competicion_id,))
        cursor.execute('''DELETE FROM Equipos WHERE competicion_id=?''', (self.competicion_id,))
        conn.commit()
        conn.close()


        for url in self.enlaces:
            mi_soup = conexion.get_soup(url)
            df_partidos = creacion_df.get_df_partidos(mi_soup)
            equipos = self.crear_equipos(df_partidos)
            self.crear_tabla_equipos(equipos)
            self.crear_tabla_partidos(df_partidos)
        self.set_ultima_actualizacion(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        print("Base de datos actualizada")

    def set_ultima_actualizacion(self, ultima_actualizacion):
        conn = sqlite3.connect(self.nombre_archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''UPDATE Competiciones SET ultima_actualizacion=? WHERE competicion_id=?''', (ultima_actualizacion, self.competicion_id))
        conn.commit()
        conn.close()
        self.ultima_actualizacion = ultima_actualizacion

    def crear_tabla_equipos(self, equipos):

        conn = sqlite3.connect(self.nombre_archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')

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
        # equipo = {"nombre_equipo": "Real Madrid", "liga": "Liga Santander", "grupo": "A", "temporada": "2020-2021"}
        for equipo in equipos:
            cursor.execute('''INSERT INTO Equipos (nombre_equipo, liga, grupo, temporada, competicion_id) VALUES (?,?,?,?,?)''',
                           (equipo["nombre"], equipo["liga"], equipo["grupo"], equipo["temporada"], self.competicion_id))

        conn.commit()
        conn.close()


    def crear_tabla_partidos(self, df_partidos):

        conn = sqlite3.connect(self.nombre_archivo_bd)
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
        conn = sqlite3.connect(self.nombre_archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT equipo_id FROM Equipos WHERE nombre_equipo=? AND competicion_id=?''', (nombre_equipo, self.competicion_id))
        equipo_id = cursor.fetchone()[0]
        conn.close()
        return equipo_id

    def get_equipos(self):
        conn = sqlite3.connect(self.nombre_archivo_bd)
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
        conn = sqlite3.connect(self.nombre_archivo_bd)
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
        partidos = self.get_partidos()
        listado_partidos = []
        for partido in partidos:
            listado_partidos.append([partido.local, partido.visitante, partido.gl, partido.gv, partido.federacion, partido.liga, partido.grupo, partido.fecha, self.nombre])
        df = pd.DataFrame(listado_partidos, columns=['local', 'visitante', 'gl', 'gv', 'federacion', 'liga', 'grupo', 'fecha', 'competicion'])
        return df



    def get_partidos_equipo(self, nombre_equipo):
        if isinstance(nombre_equipo, Equipo):
            nombre_equipo = nombre_equipo.nombre
        conn = sqlite3.connect(self.nombre_archivo_bd)
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

    def get_equipo(self, nombre_equipo):
        conn = sqlite3.connect(self.nombre_archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Equipos WHERE nombre_equipo=? AND competicion_id=?''', (nombre_equipo, self.competicion_id))
        equipo = cursor.fetchone()
        conn.close()
        equipo = Equipo(equipo[1], equipo[2], equipo[3], equipo[4])
        return equipo

    def get_clasificacion(self):
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

    def get_estadisticas_equipo(self, equipo):

        #Datos como locales y visitantes
        victorias_locales = self.get_datos_equipo_local(equipo)["victorias"]
        derrotas_locales = self.get_datos_equipo_local(equipo)["derrotas"]
        empates_locales = self.get_datos_equipo_local(equipo)["empates"]
        victorias_visitantes = self.get_datos_equipo_visitante(equipo)["victorias"]
        derrotas_visitantes = self.get_datos_equipo_visitante(equipo)["derrotas"]
        empates_visitantes = self.get_datos_equipo_visitante(equipo)["empates"]

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
                "avg_gf_ultimos_5": avg_gf_ultimos_5, "avg_gc_ultimos_5": avg_gc_ultimos_5, "std_gf_ultimos_5": std_gf_ultimos_5, "std_gc_ultimos_5": std_gc_ultimos_5}

    def get_estadisticas_competicion(self):
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
    def __init__(self, nombre, liga, grupo, temporada):
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
    def __init__(self, local = None, visitante = None, gl = 0, gv=  0, federacion = None, liga = None, grupo = None, fecha = None):
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
    def __init__(self, archivo_bd = None, lista_competiciones = []):
        self.lista_competiciones = lista_competiciones
        self.archivo_bd = archivo_bd
        self.crear_tabla_panel()

    def add_competicion(self, competicion):

        if isinstance(competicion, Competicion):
            conn = sqlite3.connect(self.archivo_bd)
            cursor = conn.cursor()
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor.execute('''INSERT INTO Competiciones (nombre_competicion, nombre_archivo_bd, lista_urls, ultima_actualizacion) VALUES (?,?,?,?)''',
                           (competicion.nombre, competicion.nombre_archivo_bd, competicion.url_to_JSON(), competicion.ultima_actualizacion))

            conn.commit()
            conn.close()
        else:
            raise Exception("Se ha intentado añadir al panel una competición que no es de tipo Competicion")

    def crear_tabla_panel(self):
        if not os.path.exists(self.archivo_bd):
            # Create an empty .db file
            open(self.archivo_bd, 'w').close()
        conn = sqlite3.connect(self.archivo_bd)
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
        conn = sqlite3.connect(self.archivo_bd)
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
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT competicion_id FROM Competiciones WHERE nombre_competicion=?''', (nombre_competicion,))
        competicion_id = cursor.fetchone()[0]
        conn.close()
        return competicion_id

    def get_competicion(self, nombre_competicion):
        self.lista_competiciones = self.get_competiciones()
        for competicion in self.lista_competiciones:
            if competicion.nombre == nombre_competicion:
                return competicion
        return None

    def annadir_enlace_a_competicion(self, nombre_competicion, enlace):
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        competicion_id = self.get_id_competicion(nombre_competicion)
        cursor.execute('''SELECT lista_urls FROM Competiciones WHERE competicion_id=?''', (competicion_id,))
        lista_urls = cursor.fetchone()[0]
        lista_urls = json.loads(lista_urls)
        lista_urls.append(enlace)
        cursor.execute('''UPDATE Competiciones SET lista_urls=? WHERE competicion_id=?''', (json.dumps(lista_urls), competicion_id))
        conn.commit()
        conn.close()
        

    def set_enlaces_a_competicion(self, nombre_competicion, lista_enlaces):
        competicion = self.get_competicion(nombre_competicion)
        competicion.enlaces = lista_enlaces
        self.actualizar_competicion(competicion)
        self.actualizar_tabla_panel()

    def eliminar_enlace_a_competicion(self, nombre_competicion, enlace):
        conn = sqlite3.connect(self.archivo_bd)
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
        competicion = self.get_competicion(nombre_competicion)
        competicion.enlaces = []
        self.actualizar_competicion(competicion)
        self.actualizar_tabla_panel()

    def set_fecha_ultima_actualizacion(self, nombre_competicion, fecha):
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        competicion_id = self.get_id_competicion(nombre_competicion)
        cursor.execute('''UPDATE Competiciones SET ultima_actualizacion=? WHERE competicion_id=?''', (fecha, competicion_id))
        conn.commit()
        conn.close()

    def get_competiciones(self):
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Competiciones''')
        competiciones = cursor.fetchall()
        conn.close()
        lista_obj_competiciones = []
        for competicion in competiciones:
            lista_obj_competiciones.append(Competicion(lista_urls= json.loads(competicion[3]), nombre_bd=competicion[2], nombre=competicion[1], competicion_id=competicion[0], actualizar_al_iniciar=False, ultima_actualizacion=competicion[4]))
        return lista_obj_competiciones

    def actualizar_competiciones(self):
        competiciones = self.get_competiciones()
        for competicion in competiciones:
            self.actualizar_competicion(competicion)

    def actualizar_competicion(self, competicion):
        if isinstance(competicion, Competicion):
            competicion.actualizar_bd()
        else:
            competicion = self.get_competicion(competicion)

            competicion.actualizar_bd()
        self.actualizar_tabla_panel()



    def eliminar_competicion(self, competicion):
        if isinstance(competicion, Competicion):
            nombre = competicion.nombre
        else:
            nombre = competicion
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones WHERE nombre_competicion=?''', (nombre,))
        conn.commit()
        conn.close()

    def eliminar_competicion_por_nombre(self, nombre_competicion):
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones WHERE nombre_competicion=?''', (nombre_competicion,))
        conn.commit()
        conn.close()

    def eliminar_competicion_por_id(self, competicion_id):
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones WHERE competicion_id=?''', (competicion_id,))
        conn.commit()
        conn.close()

    def eliminar_competiciones(self):
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''DELETE FROM Competiciones''')
        conn.commit()
        conn.close()

    def get_estadisticas_competicion(self, competicion):
        if isinstance(competicion, Competicion):
            competicion = competicion.nombre
        competicion = self.get_competicion(competicion)
        return competicion.get_estadisticas_competicion()
    def competiciones_to_df(self):
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

        dataframes = []
        for competicion in self.get_competiciones():
            dataframes.append(competicion.partidos_to_df())
        return pd.concat(dataframes)

    def modificar_nombre_competicion(self, competicion, nuevo_nombre):
        if isinstance(competicion, Competicion):
            competicion = competicion.nombre
        conn = sqlite3.connect(self.archivo_bd)
        cursor = conn.cursor()
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''UPDATE Competiciones SET nombre_competicion=? WHERE nombre_competicion=?''', (nuevo_nombre, competicion))
        conn.commit()
        conn.close()

    def modificar_enlace_a_competicion(self, competicion, enlace, nuevo_enlace):
        if isinstance(competicion, Competicion):
            competicion = competicion.nombre
        conn = sqlite3.connect(self.archivo_bd)
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
        competiciones = self.get_competiciones()
        dict_lista_competiciones = []

        for competicion in competiciones:
            dict_lista_competiciones.append(competicion.to_json())
        return {
            "archivo": self.archivo_bd,
            "lista_competiciones": dict_lista_competiciones
        }
    def to_json(self):
        return json.dumps(self.to_dict())

def competicion_from_json(json_string):
    diccionario = json.loads(json_string)
    return Competicion( lista_urls=diccionario["lista_urls"],
                        nombre_bd=diccionario["nombre_archivo_bd"],
                        nombre=diccionario["nombre_competicion"],
                        ultima_actualizacion=diccionario["ultima_actualizacion"],
                        actualizar_al_iniciar=False)
def panel_from_json(json_string):
    diccionario = json.loads(json_string)


    for i, competicion in enumerate(diccionario["lista_competiciones"]):
        diccionario["lista_competiciones"][i] = competicion_from_json(competicion)
    return Panel(diccionario["nombre"], diccionario["lista_competiciones"])



def panel_from_db(nombre_archivo):
    conn = sqlite3.connect(nombre_archivo)
    cursor = conn.cursor()
    try:
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('''SELECT * FROM Competiciones''')
        competiciones = cursor.fetchall()
        conn.close()
        lista_obj_competiciones = []
        for competicion in competiciones:
            lista_obj_competiciones.append(
                Competicion(lista_urls=json.loads(competicion[3]), nombre_bd=competicion[2], nombre=competicion[1],
                            competicion_id=competicion[0], actualizar_al_iniciar=False,
                            ultima_actualizacion=competicion[4]))
        return Panel(nombre_archivo, lista_obj_competiciones)

    except sqlite3.OperationalError:
        conn.close()
        return Panel(nombre_archivo)



if __name__ == "__main__":
    mi_panel = panel_from_db("panel.db")
    # mi_panel.actualizar_competiciones()
    mi_compe = mi_panel.get_competiciones()[0]
    mi_equipo = mi_compe.get_equipos()[0]
    clasificacion = mi_compe.get_clasificacion()
    print(clasificacion)







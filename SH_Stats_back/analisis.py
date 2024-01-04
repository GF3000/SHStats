from bs4 import BeautifulSoup
import requests
import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from SH_Stats_back import clases, funciones_auxiliares

def get_soup(url, tiempo = False):
    tiempo_inicio = datetime.datetime.now()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="ISO-8859-1")
    if(tiempo):
        tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
        return soup, tiempo_ejecucion
    else:
        return soup


def get_info(soup):
    tiempo_inicio = datetime.datetime.now()
    resultados = soup.find_all('div', class_='titulos pull-left')
    resultados = str(resultados[0])
    resultados = resultados.split("<h4>")[1]
    resultados = resultados.split("</h4>")[0]
    liga = resultados.split(" - ")[0]
    grupo = resultados.split(" - ")[1:]
    grupo = " ".join(grupo)

    # Search id = select2-temporadas-container
    span_element = str(soup.find_all("div", class_="container-fluid noprint")[0])
    temporada = span_element.split('id=\"id_temporada_actual\" type=\"hidden\" value=\"')[1]
    temporada = temporada.split("\"")[0]
    federacion = span_element.split('id=\"id_territorial\" type=\"hidden\" value=\"')[1]
    federacion = federacion.split("\"")[0]

    liga = funciones_auxiliares.acortar_campo(liga)
    grupo = funciones_auxiliares.acortar_campo(grupo)
    federacion = funciones_auxiliares.get_federacion_by_index(federacion)

    tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio

    return federacion, liga, grupo, temporada, tiempo_ejecucion


def create_list_dates(fecha_div):
    fecha_texto = []
    for fecha in fecha_div:
        fecha_texto.append(fecha.text)
    lista = []
    for elemento in fecha_texto:
        lista.append(datetime.datetime.strptime(elemento, '%d/%m/%Y'))
    return lista


def cargar_partidos(soup):
    tiempo_inicio = datetime.datetime.now()
    federacion, liga, grupo, temporada, tiempo_ejecucion = get_info(soup)

    fecha_div = soup.find_all('div', class_='negrita')
    fechas = create_list_dates(fecha_div)

    resultados = soup.find_all('td', class_='p-t-20')
    atributos = []
    partidos = []

    for resultado in resultados:
        texto = resultado.text
        atributos.append(resultado)

        if texto == "VER DIRECTO":  # Fin de fila
            equipos = [a.text for a in atributos[0].find_all('a')]
            gl_str, gv_str = atributos[1].text.split(" - ")
            gl = int(gl_str) if gl_str.strip() != "" else None
            gv = int(gv_str) if gv_str.strip() != "" else None

            if gl == None or gv == None:
                pass
            else:
                fecha = fechas[len(partidos)]
                local, visitante = equipos[0], equipos[1]

                este_partido = clases.partido(
                    local, visitante, gl=gl, gv=gv,
                    liga=liga, grupo=grupo, temporada=temporada,
                    federacion=federacion, fecha=fecha
                )

                partidos.append(este_partido)

            atributos = []
        tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
    return partidos, tiempo_ejecucion

def crear_equipos(partidos, tiempo = False):
    tiempo_inicio = datetime.datetime.now()
    equipos = clases.listado_equipos()
    print(f"total equipos: {len(equipos)}")
    for partido in partidos:
        local = clases.equipo(partido.local, federacion = partido.federacion, liga = partido.liga, grupo = partido.grupo, temporada=  partido.temporada)
        visitante = clases.equipo(partido.visitante, federacion = partido.federacion, liga = partido.liga, grupo = partido.grupo, temporada=  partido.temporada)
        # print("Local: " + local.nombre + " Visitante: " + visitante.nombre)
        if (local in equipos): #Si ya existe el equipo, lo buscamos
            local = equipos.buscar(local)
        else: #Si no existe el equipo, lo añadimos
            equipos.add(local)
        if (visitante in equipos):#Si ya existe el equipo, lo buscamos
            visitante = equipos.buscar(visitante)
        else: #Si no existe el equipo, lo añadimos
            equipos.add(visitante)

        local.add_partido(partido)
        visitante.add_partido(partido)
    tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
    if (tiempo):
        return equipos, tiempo_ejecucion
    else:
        return equipos

def get_clasificacion(partidos, tiempo = False):
    tiempo_inicio = datetime.datetime.now()
    equipos = crear_equipos(partidos)
    equipos_dict = equipos.to_dict()

    pd.set_option('display.max_columns', None)  # Muestra todas las columnas
    pd.set_option('display.expand_frame_repr', False)  # Evita dividir las columnas en varias líneas

    # Convertir el diccionario a un DataFrame
    df = pd.DataFrame.from_dict(equipos_dict, orient='index')

    # Crear columnas puntos y diferencia de goles
    df['puntos'] = df['victorias']*2 + df['empates']
    df['dif_goles'] = df['gf'] - df['gc']

    # Rename columns
    df = df.rename(columns={"nombre": "Equipo", 'partidos': 'PJ', "federacion": "Federación", 'gf': 'GF', 'gc': 'GC', 'victorias': 'V', 'derrotas': 'D', 'empates': 'E', 'puntos': 'P', 'dif_goles': 'DIF', 'temporada': 'Temporada', 'grupo': 'Grupo', 'liga': 'Liga'})

    # Ordenar por puntos y diferencia de goles
    df = df.sort_values(by=['P', 'DIF'], ascending=False)



    # Añadir columna posición
    df.index.name = 'Puesto'
    for i, index in enumerate(df.index):
        df = df.rename(index={index: str(i+1) + '. '})

    if (tiempo):
        tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
        return df, tiempo_ejecucion
    else:
        return df


def get_GF_en_victorias(partidos):
    GF_en_victorias = []
    for partido in partidos:
        if (partido.gl > partido.gv):
            GF_en_victorias.append(partido.gl)
        elif (partido.gl < partido.gv):
            GF_en_victorias.append(partido.gv)
    return GF_en_victorias

def get_GC_en_victorias(partidos):
    GC_en_victorias = []
    for partido in partidos:
        if (partido.gl > partido.gv):
            GC_en_victorias.append(partido.gv)
        elif (partido.gl < partido.gv):
            GC_en_victorias.append(partido.gl)
    return GC_en_victorias

def get_goles_en_empates(partidos):
    GF_en_empates = []
    for partido in partidos:
        if (partido.gl == partido.gv):
            GF_en_empates.append(partido.gl)
    return GF_en_empates

def get_diferencias(partidos):
    diferencias = []
    for partido in partidos:
        diferencias.append(abs(partido.gl - partido.gv))
    return diferencias

def total_goles(partidos):
    total = []
    for partido in partidos:
        goles_partido = 0
        goles_partido += partido.gl
        goles_partido += partido.gv
        total.append(goles_partido)
    return total


def get_stats_de_url(url, decimales=1, tiempo=False):
    tabla = []
    soup, tiempo_soup = get_soup(url, tiempo=True)
    federacion, liga, grupo, temporada, tiempo_info = get_info(soup)
    if (liga == None or len(liga) == 0 or liga == "" or liga == " "):
        url = url.replace("seleccion=0", "seleccion=1")
        soup, tiempo_soup = get_soup(url, tiempo=True)
        tiempo_aux = tiempo_info
        federacion, liga, grupo, temporada, tiempo_info = get_info(soup)
        tiempo_info += tiempo_aux
    liga = funciones_auxiliares.acortar_campo(liga)
    grupo = funciones_auxiliares.acortar_campo(grupo)

    partidos, tiempo_partidos = cargar_partidos(soup)
    if (len(partidos) == 0):
        tiempo_ejecucion = tiempo_soup + tiempo_info + tiempo_partidos
        return None, tiempo_ejecucion
    avg_goles = round(np.mean(total_goles(partidos)), decimales)
    sd_goles = round(np.std(total_goles(partidos)), decimales)
    avg_DIF_total = round(np.mean(get_diferencias(partidos)), decimales)
    sd_DIF_total = round(np.std(get_diferencias(partidos)), decimales)
    avg_GF_en_victorias = round(np.mean(get_GF_en_victorias(partidos)), decimales)
    avg_GC_en_victorias = round(np.mean(get_GC_en_victorias(partidos)), decimales)
    sd_GC_en_victorias = round(np.std(get_GC_en_victorias(partidos)), decimales)
    sd_GF_en_victorias = round(np.std(get_GF_en_victorias(partidos)), decimales)
    num_partidos = len(partidos)

    tabla.append({"federacion": federacion,
                  "liga": liga,
                  "grupo": grupo,
                  "temporada": temporada,
                  "num_partidos": num_partidos,
                  "avg_goles": avg_goles,
                  "sd_goles": sd_goles,
                  "avg_DIF_total": avg_DIF_total,
                  "sd_DIF_total": sd_DIF_total,
                  "avg_GF_en_victorias": avg_GF_en_victorias,
                  "sd_GF_en_victorias": sd_GF_en_victorias,
                  "avg_GC_en_victorias": avg_GC_en_victorias,
                  "sd_GC_en_victorias": sd_GC_en_victorias,
                  "url": url})

    # Make a DataFrame from the dictionary
    df = pd.DataFrame(tabla)
    if (tiempo):
        tiempo_ejecucion = tiempo_soup + tiempo_info + tiempo_partidos
        return df, tiempo_ejecucion
    else:
        return df


def get_stats_de_partidos(partidos, nombre = None, federacion=None, liga=None, grupo=None, temporada=None, url = None,decimales=1, tiempo=False):
    tiempo_inicio = datetime.datetime.now()
    tabla = []

    liga = funciones_auxiliares.acortar_campo(liga) if liga != None else None
    grupo = funciones_auxiliares.acortar_campo(grupo) if grupo != None else None
    if (len(partidos) == 0):
        tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
        return None, tiempo_ejecucion
    avg_goles = round(np.mean(total_goles(partidos)), decimales)
    sd_goles = round(np.std(total_goles(partidos)), decimales)
    avg_DIF_total = round(np.mean(get_diferencias(partidos)), decimales)
    sd_DIF_total = round(np.std(get_diferencias(partidos)), decimales)
    avg_GF_en_victorias = round(np.mean(get_GF_en_victorias(partidos)), decimales)
    avg_GC_en_victorias = round(np.mean(get_GC_en_victorias(partidos)), decimales)
    sd_GC_en_victorias = round(np.std(get_GC_en_victorias(partidos)), decimales)
    sd_GF_en_victorias = round(np.std(get_GF_en_victorias(partidos)), decimales)
    num_partidos = len(partidos)

    tabla.append({"nombre": nombre,
                  "federacion": federacion,
                  "liga": liga,
                  "grupo": grupo,
                  "temporada": temporada,
                  "num_partidos": num_partidos,
                  "avg_goles": avg_goles,
                  "sd_goles": sd_goles,
                  "avg_DIF_total": avg_DIF_total,
                  "sd_DIF_total": sd_DIF_total,
                  "avg_GF_en_victorias": avg_GF_en_victorias,
                  "sd_GF_en_victorias": sd_GF_en_victorias,
                  "avg_GC_en_victorias": avg_GC_en_victorias,
                  "sd_GC_en_victorias": sd_GC_en_victorias,
                  "url": url})
    df = pd.DataFrame(tabla)
    tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
    if (tiempo):
        return df, tiempo_ejecucion
    else:
        return df

def get_stats_de_partidos_de_equipos(equipo):
    partidos = equipo.partidos
    goles_equipo = []
    goles_rival = []
    diferencias = []
    victorias_locales = 0
    victorias_visitantes = 0
    derrotas_locales = 0
    derrotas_visitantes = 0
    empates_locales = 0
    empates_visitantes = 0
    for partido in partidos:
        if (equipo.es_local(partido)):
            goles_equipo.append(partido.gl)
            goles_rival.append(partido.gv)
            diferencias.append(partido.gl - partido.gv)
            if (partido.gl > partido.gv):
                victorias_locales += 1
            elif (partido.gl < partido.gv):
                derrotas_locales += 1
            else:
                empates_locales += 1

        else:
            goles_equipo.append(partido.gv)
            goles_rival.append(partido.gl)
            diferencias.append(partido.gv - partido.gl)
            if (partido.gl > partido.gv):
                derrotas_visitantes += 1
            elif (partido.gl < partido.gv):
                victorias_visitantes += 1
            else:
                empates_visitantes += 1
    victorias = 0
    derrotas = 0
    empates = 0
    for diferencia in diferencias:
        if (diferencia > 0):
            victorias += 1
        elif (diferencia < 0):
            derrotas += 1
        else:
            empates += 1


    avg_GF = round(np.mean(goles_equipo), 1)
    sd_GF = round(np.std(goles_equipo), 1)
    avg_GC = round(np.mean(goles_rival), 1)
    sd_GC = round(np.std(goles_rival), 1)
    avg_DIF_total = round(np.mean(diferencias), 1)
    sd_DIF_total = round(np.std(diferencias), 1)
    num_partidos = len(partidos)

    return {"num_partidos": num_partidos,
            "victorias": victorias,
            "derrotas": derrotas,
            "empates": empates,
            "victorias_locales" : victorias_locales,
            "victorias_visitantes": victorias_visitantes,
            "derrotas_locales": derrotas_locales,
            "derrotas_visitantes": derrotas_visitantes,
            "empates_locales": empates_locales,
            "empates_visitantes": empates_visitantes,
            "avg_GF": avg_GF,
            "sd_GF": sd_GF,
            "avg_GC": avg_GC,
            "sd_GC": sd_GC,
            "avg_DIF": avg_DIF_total,
            "sd_DIF": sd_DIF_total}




def comparar_ligas(ligas, decimales = 1, tiempo = False):
    tiempo_inicio = datetime.datetime.now()
    listado_dfs = []
    for i,nombre in enumerate(ligas):
        print("Descargando liga " + str(i+1) + " de " + str(len(ligas)) + ": " + nombre)
        liga = ligas[nombre]
        listado_partidos = []
        mi_soup = None
        for i, url in enumerate(liga):
            url = funciones_auxiliares.convert_url(url)
            print("Descargando link " + str(i+1) + " de " + str(len(liga)) + ": " + url)
            mi_soup = get_soup(url)
            partidos, tiempo_partidos = cargar_partidos(mi_soup)
            listado_partidos.append(partidos)
        #Plain listado_partidos
        listado_partidos = [partido for lista in listado_partidos for partido in lista]
        federecion, liga, grupo, temporada= get_info(mi_soup)[:4]
        df, tiempo_df = get_stats_de_partidos(listado_partidos, nombre=nombre, decimales = decimales,federacion= federecion, liga = liga, temporada=temporada,  tiempo=True)
        listado_dfs.append(df)
    df = pd.concat(listado_dfs)
    df.index = np.arange(1, len(df) + 1)
    df = df.rename_axis('Num')
    del df ['url']
    del df ['grupo']

    tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
    if (tiempo):
        return df, tiempo_ejecucion
    else:
        return df

def get_partidos(liga, decimales = 1, tiempo = False):
    tiempo_inicio = datetime.datetime.now()
    listado_partidos = []
    mi_soup = None
    for i, url in enumerate(liga):
        url = funciones_auxiliares.convert_url(url)
        print("Descargando link " + str(i+1) + " de " + str(len(liga)) + ": " + url)
        mi_soup = get_soup(url)
        partidos, tiempo_partidos = cargar_partidos(mi_soup)
        listado_partidos.append(partidos)
    # Plain listado_partidos
    listado_partidos = [partido.to_dict() for lista in listado_partidos for partido in lista]
    df = pd.DataFrame(listado_partidos)
    df.index = np.arange(1, len(df) + 1)
    df = df.rename_axis('#')
    df = df.rename(columns={"local": "Local", "visitante": "Visitante", "gl": "GL", "gv": "GV", "liga": "Liga", "grupo": "Grupo", "temporada": "Temporada", "federacion": "Federación", "fecha": "Fecha"})
    df = df[["Local", "Visitante", "GL", "GV", "Liga", "Grupo", "Temporada", "Federación", "Fecha"]]
    tiempo_ejecucion = datetime.datetime.now() - tiempo_inicio
    if (tiempo):
        return df, tiempo_ejecucion
    else:
        return df

def get_df_partidos(equipo):
    partidos = equipo.partidos
    partidos_dict = []
    for partido in partidos:
        partidos_dict.append(partido.to_dict())
    df = pd.DataFrame(partidos_dict)
    df.index = np.arange(1, len(df) + 1)
    df = df.rename_axis('#')
    df = df.rename(columns={"local": "Local", "gl": "GL", "gv": "GV", "visitante": "Visitante", "liga": "Liga", "grupo": "Grupo", "temporada": "Temporada", "federacion": "Federación", "fecha": "Fecha"})
    df = df[["Local",  "GL", "GV","Visitante", "Liga", "Grupo", "Temporada", "Federación", "Fecha"]]

    def asignar_goles(row):
        if equipo.nombre == row["Local"]:
            return pd.Series({"GolesEquipo": row["GL"], "GolesRival": row["GV"], "Diferencia": row["GL"] - row["GV"]})
        else:
            return pd.Series({"GolesEquipo": row["GV"], "GolesRival": row["GL"], "Diferencia": row["GV"] - row["GL"]})

    # Aplicar la función a lo largo de las filas del DataFrame
    df[['GolesEquipo', 'GolesRival', 'Diferencia']] = df.apply(asignar_goles, axis=1)

    return df





if __name__ == "__main__":
    url ="https://www.rfebm.com/competiciones/resultados_completos.php?seleccion=0&id=1012878"


    partidos, tiempo = cargar_partidos(get_soup(url))
    equipos = crear_equipos(partidos)
    #print(equipos)
    mi_equipo = equipos.elementos[0]
    print(mi_equipo)
    df = get_df_partidos(mi_equipo)

    columnas = ['GolesEquipo', 'GolesRival']
    df = df[columnas]
    plt.figure(figsize=(8, 6))
    df.boxplot(column=['GolesEquipo', 'GolesRival'])
    plt.title('Boxplot de GolesEquipo y GolesRival')
    plt.ylabel('Número de Goles')
    plt.show()

    #Force df to show all columns
    pd.set_option('display.max_columns', None)  # Muestra todas las columnas
    pd.set_option('display.expand_frame_repr', False)  # Evita dividir las columnas en varias líneas
    print(df)


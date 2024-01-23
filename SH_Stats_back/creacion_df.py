import pandas as pd
import datetime
from SH_Stats_back import funciones_auxiliares
from SH_Stats_back import gestor


#Funciones que reciben un objeto de tipo BeautifulSoup y devuelven un DataFrame
def create_list_dates(fecha_div):
    # TODO: Ahora mismo no funciona
    fecha_texto = []
    for fecha in fecha_div:
        fecha_texto.append(fecha.text)
    lista = []
    for elemento in fecha_texto:
        # lista.append(datetime.datetime.strptime(elemento, '%d/%m/%Y'))
        lista.append(None)
    return lista


def get_info(soup):
    """
    Función que devuelve la federación, liga, grupo y temporada de una página de resultados
    :param soup: objeto de tipo BeautifulSoup
    :return: federación, liga, grupo y temporada
    """

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

    federacion=funciones_auxiliares.get_federacion_by_index(federacion)


    return federacion, liga, grupo, temporada

def get_df_partidos(soup):
    """
    Función que devuelve un DataFrame con los partidos de una página de resultados
    :param soup: objeto de tipo BeautifulSoup
    :return: DataFrame con los partidos de una página de resultados
    """
    federacion, liga, grupo, temporada = get_info(soup)

    fecha_div = soup.find_all('div', class_='negrita')
    fechas = create_list_dates(fecha_div)

    resultados = soup.find_all('td', class_='p-t-20')
    atributos = []
    partidos = []
    # Columnas del DataFrame
    columnas = ['local', 'visitante', 'gl', 'gv', 'liga', 'grupo', 'temporada', 'federacion', 'fecha']
    df_partidos = pd.DataFrame(columns=columnas)

    for resultado in resultados:
        texto = resultado.text
        atributos.append(resultado)

        if texto == "VER DIRECTO":  # Fin de fila
            equipos = [a.text for a in atributos[0].find_all('a')]
            gl_str, gv_str = atributos[1].text.split(" - ")
            gl = int(gl_str) if gl_str.strip() != "" else None
            gv = int(gv_str) if gv_str.strip() != "" else None

            if gl is None or gv is None:
                pass
            else:
                # fecha = fechas[len(partidos)]
                fecha = None
                local, visitante = equipos[0], equipos[1]
                nuevo_partido = {"local": local, "visitante": visitante, "gl": gl, "gv": gv, "liga": liga, "grupo": grupo,
                           "temporada": temporada, "federacion": federacion, "fecha": fecha}

                df_partidos = pd.concat([df_partidos, pd.DataFrame([nuevo_partido])], ignore_index=True)

            atributos = []

    return df_partidos






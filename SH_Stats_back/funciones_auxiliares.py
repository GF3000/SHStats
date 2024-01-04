import re


def acortar_campo(campo):
    campo = campo.replace("PRIMERA", "1a")
    campo = campo.replace("SEGUNDA", "2a")
    campo = campo.replace("TERCERA", "3a")
    campo = campo.replace("CUARTA", "4a")
    campo = campo.replace("QUINTA", "5a")
    campo = re.sub(r'\bDIVI\S*', 'DIV.', campo)
    campo = campo.replace("NACIONAL", "NAC.")
    campo = re.sub(r'\bNACIO\w*', 'NAC.', campo)

    campo = re.sub(r'\bAUTON\w*', 'AUT.', campo)
    campo = campo.replace("PROVINCIAL", "PROV.")
    campo = campo.replace("TERRITORIAL", "TER.")
    campo = campo.replace("MASCULINA", "MASC.")
    campo = campo.replace("FEMENINA", "FEM.")
    campo = re.sub(r'\bJUVEN\w*', 'JUV.', campo)
    campo = re.sub(r'\bCADET\w*', 'CAD.', campo)
    campo = re.sub(r'\bINFAN\w*', 'INF.', campo)
    campo = re.sub(r'\bALEV\w*', 'ALE.', campo)
    campo = re.sub(r'\bBENJ\w*', 'BEN.', campo)
    campo = re.sub(r'\bPREBNJ\w*', 'PREB.', campo)
    campo = re.sub(r'\bGRUP\w*', 'GR.', campo)

    return campo


def get_federacion_by_index(index):
    match index:
        case "9999":
            return "RFEBM"
        case "33":
            return "Fed. Valencia"
        case "36":
            return "Fed. Castilla y León"
        case "35":
            return "Fed. Cantabra"
        case "37":
            return "Fed. Canarias"
        case "31":
            return "Fed. Navarra"
        case "32":
            return "Fed. Rioja"
        case "17":
            return "Fed. Cataluña"
        case "24":
            return "Fed. Ceuta"
        case "22":
            return "Fed Murcia"
        case "19":
            return "Fed. Extremadura"
        case "20":
            return "Fed. Galicia"
        case "25":
            return "Fed. Melilla"
        case "28":
            return "Fed. Asturias"
        case "16":
            return "Fed. Castilla la Mancha"
        case "26":
            return "Fed. Andalucía"
        case "29":
            return "Fed. Baleares"
        case "27":
            return "Fed. Aragón"
        case "21":
            return "Fed. Madrid"
        case "18":
            return "Fed. Vasca"
        case _:
            return index

def convert_url(url_entrada):
    try:
        seleccion = url_entrada.split("seleccion=")[1][0]
        id = url_entrada.split("id=")[1]
        id = id.split("&")[0]
        url_nuevo = f"https://www.rfebm.com/competiciones/resultados_completos.php?seleccion={seleccion}&id={id}"
        return url_nuevo
    except:
        return url_entrada

if __name__ == "__main__":
    url = "https://www.rfebm.com/competiciones/resultados_completos.php?seleccion=0&id=1018419"
    print(convert_url(url))


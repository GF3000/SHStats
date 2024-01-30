from bs4 import BeautifulSoup
import requests
#Funciones que reciben una url y devuelven un objeto de tipo BeautifulSoup



def get_soup(url):
    """
    Función que devuelve un objeto de tipo BeautifulSoup a partir de una url
    :param url: url de la página a scrapear
    :return: objeto de tipo BeautifulSoup
    """

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except Exception as e:
        print(e)
        return None

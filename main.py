import sys
from io import BytesIO
from find_spn_param import find_spn
import requests
from PIL import Image, ImageDraw, ImageFont
import math
from random import choice

# Пусть наше приложение предполагает запуск:
# python main.py Москва, улица Тимура Фрунзе, 11к8
# Тогда запрос к геокодеру формируется следующим образом:
cities = ['Москва', 'Санкт-Петербург', 'Будимирово']
types = ['sat', 'map']
toponym_to_find = choice(cities)
typ = choice(types)
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}
response = requests.get(geocoder_api_server, params=geocoder_params)
if not response:
    # обработка ошибочной ситуации
    pass
# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
deltax, deltay = find_spn(toponym_to_find)
# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([deltax, deltay] if typ == 'sat' else [str(float(deltax) / 25), str(float(deltay) / 25)]),
    "l": typ
}
map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
Image.open(BytesIO(
    response.content)).show()
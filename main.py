import sys
from io import BytesIO
from find_spn_param import find_spn
import requests
from PIL import Image, ImageDraw, ImageFont
import math
from random import choice
import time
import pygame
import os

# Пусть наше приложение предполагает запуск:
# python main.py Москва, улица Тимура Фрунзе, 11к8
# Тогда запрос к геокодеру формируется следующим образом:
cities = ['Москва', 'Санкт-Петербург', 'Будимирово']
types = ['sat', 'map']


def pic(las):
    typ = choice(types)
    toponym_to_find = choice(cities)
    while las == toponym_to_find:
        toponym_to_find = choice(cities)
    klj = toponym_to_find
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
        response.content)).convert('RGB').save('data/1.png')
    return klj


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print('Файл с изображением не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


if __name__ == '__main__':
    try:
        pygame.init()
        all_sprites = pygame.sprite.Group()
        size = width, height = 500, 500
        screen = pygame.display.set_mode(size)
        pygame.display.flip()
        screen.fill('white')
        clock = pygame.time.Clock()
        ukaz = pygame.sprite.Sprite(all_sprites)
        pas = pic('')
        ukaz.image = pygame.transform.scale(load_image("1.png"), (500, 500))
        ukaz.rect = ukaz.image.get_rect()
        ukaz.rect.x, ukaz.rect.y = 0, 0
        clock = pygame.time.Clock()
        running = True
        while running:
            screen.fill('white')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                pas = pic(pas)
                ukaz.image = load_image("1.png")
                ukaz.rect = ukaz.image.get_rect()
                ukaz.rect.x, ukaz.rect.y = 0, 0
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(10)
        pygame.quit()
    except Exception:
        pygame.quit()
        print('Неправильный формат ввода')

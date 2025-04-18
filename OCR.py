import easyocr
from collections import defaultdict
import cv2
from loguru import logger
import sys
import re
import numpy as np

logger.remove()
logger.add(sys.stderr, level="INFO")

# Функция для поиска координат цен
def search_price_coord(result: list, tolerance: int)->list:

    numbs = []
    for (bbox, text, prob) in result:
        if re.fullmatch(r"^\d+[.,]\d+$", text):
            numbs.append([text,bbox])

    max_x = -1
    for text, bbox in numbs:
        if max_x < bbox[1][0]:
            max_x = bbox[1][0]

    price = []
    for text, bbox in numbs:
        if (max_x - bbox[1][0])<=tolerance:
            price.append([text,bbox])

    return price

# Функция для разделения входного изображения на небольшие картинки с названием, количеством, ценой
def picture_part(price: list, path: str)->list:
    image = cv2.imread(path)
    height, width = image.shape[:2]

    stripes = []
    for i in range(len(price) - 1):
        # Извлекаем Y-координаты (верхнюю и нижнюю границы)
        y_top = price[i][1][1][1]  # Верхняя граница (первая точка, Y-координата)
        y_bottom = price[i + 1][1][1][1]  # Нижняя граница (третья точка, Y-координата)

        # Вырезаем полосу по всей ширине изображения
        vertical_stripe = image[y_top:y_bottom, 0:width]  # 0:width - вся ширина
        stripes.append(vertical_stripe)

    return stripes

# Функция для объединения названия, количества, цены в один массив
def join_name_count_price(result: list) ->list[str]:

    name = ''
    for _, text, _ in result:
        if re.fullmatch(r"^\D+$", text):
            name+=text+' '

    join = [name]

    for _, text, _ in result:
        if re.fullmatch(r"^\d+[.,]\d+$", text):
            join.append(text)

    return join


def img_show(img_path: str, result):
    img = cv2.imread(img_path)

    for bbox, _, _ in result:
        cv2.rectangle(img,
                      (int(bbox[0][0]),int(bbox[0][1])),
                      (int(bbox[2][0]),int(bbox[2][1])),
                      (0,255,0),
                      thickness=2)
    cv2.imshow("", img)
    cv2.waitKey(0)

def OCR(img_path: str, show: bool = False):

    # Погрешность для группировки строк
    TOLERANCE = 20  # пикселей

    # Инициализация EasyOCR
    reader = easyocr.Reader(['ru', 'en'])

    # Распознавание текста с изображения чека
    result = reader.readtext(img_path)

    logger.info(result)

    if show:
        img_show(img_path, result)

    # Получаем список изображений
    image_stripes = picture_part(search_price_coord(result, TOLERANCE), img_path)

    # Обрабатываем каждое изображение
    for i, stripe in enumerate(image_stripes):
        result = reader.readtext(stripe)
        logger.info(result)
        print(f"Result for stripe {i}: {join_name_count_price(result)}")


if __name__ == '__main__':
    OCR('images/img.jpg', show=True)


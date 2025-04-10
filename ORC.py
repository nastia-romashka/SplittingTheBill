import easyocr
from collections import defaultdict
import cv2
from loguru import logger
import sys
import re
import numpy as np

logger.remove()
logger.add(sys.stderr, level="INFO")


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

def picture_part(price: list, path: str)->None:
    image = cv2.imread(path)
    height, width = image.shape[:2]

    count=0
    for i in range(len(price)-1):
        # Извлекаем Y-координаты (верхнюю и нижнюю границы)
        y_top = price[i][1][1][1]  # Верхняя граница (первая точка, Y-координата)
        y_bottom = price[i+1][1][1][1]  # Нижняя граница (третья точка, Y-координата)

        # Вырезаем полосу по всей ширине изображения
        vertical_stripe = image[y_top:y_bottom, 0:width]  # 0:width - вся ширина

        # Сохраняем результат
        cv2.imwrite(f'{i}.jpg', vertical_stripe)
        logger.debug(f"Вертикальная полоса сохранена.")
        count+=1

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
                      (bbox[0][0],bbox[0][1]),
                      (bbox[2][0],bbox[2][1]),
                      (0,255,0),
                      thickness=2)
    cv2.imshow("", img)
    cv2.waitKey(0)

def OCR(img_path: str):

    # Погрешность для группировки строк (подбирается экспериментально)
    TOLERANCE = 20  # пикселей


    # Инициализация EasyOCR
    reader = easyocr.Reader(['ru', 'en'])

    # Распознавание текста с изображения чека
    result = reader.readtext(img_path)

    logger.info(result)
    logger.info(search_price_coord(result, TOLERANCE))

    picture_part(search_price_coord(result, TOLERANCE), img_path)



    # Группировка текста по строкам с учетом погрешности
    lines = defaultdict(list)
    for (bbox, text, prob) in result:
        y_center = (bbox[0][1] + bbox[2][1]) / 2  # Средняя Y-координата

        # Проверяем, есть ли уже близкая строка
        found = False
        for existing_y in lines.keys():
            if abs(existing_y - y_center) <= TOLERANCE:
                lines[existing_y].append((bbox[0][0], text))  # Добавляем к существующей строке
                found = True
                break
        if not found:
            lines[y_center].append((bbox[0][0], text))  # Создаем новую строку

    # Сортировка строк по Y и слов по X внутри строки
    grouped_data = []
    for y in sorted(lines.keys()):
        line_texts = [text for (x, text) in sorted(lines[y], key=lambda x: x[0])]
        grouped_data.append(line_texts)

    # Формируем список [название, количество, цена]
    items = []
    for line in grouped_data:
        if len(line) >= 3:  # Если есть название, количество и цена
            name = line[0]
            quantity = line[1]
            price = line[-1]  # Цена обычно последняя
            items.append([name, quantity, price])

    # Вывод результата
    for item in items:
        print(item)

    img_show(img_path, result)

    return result

if __name__ == '__main__':
    #OCR('images/img.jpg')

    res = OCR('1.jpg')

    join_name_count_price(res)

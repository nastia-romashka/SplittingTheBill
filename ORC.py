import easyocr
from collections import defaultdict
import cv2

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
    # Инициализация EasyOCR
    reader = easyocr.Reader(['ru', 'en'])

    # Распознавание текста с изображения чека
    result = reader.readtext(img_path)

    # Погрешность для группировки строк (подбирается экспериментально)
    TOLERANCE = 10  # пикселей

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

if __name__ == '__main__':
    OCR('images/img.jpg')
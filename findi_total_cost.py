import pytesseract
from PIL import Image
import re

import cv2
import numpy as np

# Укажите путь к tesseract, если он не добавлен в PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image_path):
    """Улучшение качества изображения перед распознаванием"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Читаем в оттенках серого

    # # Применяем адаптивное пороговое преобразование
    # image = cv2.adaptiveThreshold(
    #     image, 255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY, 11, 2
    # )

    # # Увеличиваем резкость (опционально)
    # kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    # image = cv2.filter2D(image, -1, kernel)

    return Image.fromarray(image)

def extract_max_amount(image_path):
    # Загружаем изображение и применяем OCR
    processed_image = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_image, lang='rus')

    # with open(f'{image_path}.txt','w', encoding='utf-8') as file:
    #     file.write(text)

    # Ищем все числа с плавающей точкой (любое количество цифр до и 2 после разделителя)
    amounts = re.findall(r'\b\d+[,.]\d{2}\b', text.replace(' ', ''))

    if not amounts:
        return "Не найдено чисел в формате XXXXX.XX или XXXXX,XX"

    # Преобразуем в float (заменяем ',' на '.')
    amounts_float = [float(amount.replace(',', '.')) for amount in amounts]

    # Возвращаем максимальное значение
    return max(amounts_float)


# Пример использования
image_paths = ['images/img.jpg', 'images/img2.jpg','images/img3.jpg']
for path in image_paths:
    total = extract_max_amount(path)
    print(f"Файл: {path}, Максимальная сумма: {total:.2f}")


def extract_and_show_total_area(image_path, target_words):
    """
    Находит ключевое слово и вырезает область во всю ширину и высотой в 3 раза больше слова

    :param image_path: путь к изображению чека
    :param target_words: список слов для поиска
    """
    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")

    # Получаем высоту и ширину изображения
    img_height, img_width = image.shape[:2]

    # Распознавание текста с координатами
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, lang='rus', output_type=pytesseract.Output.DICT)

    found = False

    for i in range(len(data['text'])):
        text = data['text'][i].lower()
        conf = int(data['conf'][i])

        if not text.strip() or conf < 30:
            continue

        if any(target_word in text for target_word in target_words):
            found = True
            # Получаем координаты слова
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

            # Вычисляем область для вырезания:
            # По ширине - вся ширина изображения
            # По высоте - 3 высоты слова, центрированная вокруг слова
            roi_height = h * 4
            roi_y1 = max(0, y - (roi_height - h) // 2)
            roi_y2 = min(img_height, y + h + (roi_height - h) // 2)

            # Вырезаем область интереса
            roi = image[roi_y1:roi_y2, 0:img_width]

            # Показываем результат
            cv2.imshow(f'Область "{text}"', roi)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break

    if not found:
        print("Ключевые слова не найдены")


# Пример использования
extract_and_show_total_area('images/img.jpg', ['итог', 'итого'])


# Пример использования
image_paths = ['images/img.jpg', 'images/img2.jpg','images/img3.jpg']
for path in image_paths:
    extract_and_show_total_area(path, target_words=['итог', 'итого'])
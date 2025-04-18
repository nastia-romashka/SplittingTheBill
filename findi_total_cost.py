import pytesseract
import re
import cv2

# Укажите путь к tesseract, если он не добавлен в PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image):
    """Предварительная обработка изображения для улучшения распознавания"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return thresh


def extract_total_region(image_path):
    """
    Находит ключевое слово и возвращает область во всю ширину и высотой в 4 раза больше слова
    :param image_path: путь к изображению чека
    :return:изображение области
    """
    target_words = ['итог', 'итого']

    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")

    # Распознавание текста с координатами
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, lang='rus', output_type=pytesseract.Output.DICT)

    for i in range(len(data['text'])):
        text = data['text'][i].lower()
        conf = int(data['conf'][i])

        if not text.strip() or conf < 30:
            continue

        if any(target_word in text for target_word in target_words):
            # Получаем координаты слова
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

            # Вычисляем область для вырезания (4 высоты слова)
            roi_height = h * 4
            roi_y1 = max(0, y - (roi_height - h) // 2)
            roi_y2 = min(image.shape[0], y + h + (roi_height - h) // 2)

            # Вырезаем область интереса (вся ширина)
            roi = image[roi_y1:roi_y2, 0:image.shape[1]]
            return roi

    return None


def extract_max_amount(image):
    """
    Извлекает максимальную сумму из изображения области с итогом

    :param image: изображение области с суммой (в формате OpenCV BGR)
    :return: максимальная найденная сумма или сообщение об ошибке
    """
    if image is None:
        return "Не удалось обработать изображение"

    # Предварительная обработка
    processed_image = preprocess_image(image)

    # Распознавание текста
    text = pytesseract.image_to_string(processed_image, lang='rus', config='--psm 6')

    # Поиск чисел (включая форматы с разделителями тысяч)
    amounts = re.findall(r'(?:\d{1,3}[ ,.]?)+[.,]\d{2}', text.replace(' ', ''))

    if not amounts:
        return "Не найдено чисел в формате XXXXX.XX или XXXXX,XX"

    # Нормализация и преобразование в float
    amounts_float = []
    for amount in amounts:
        try:
            # Удаляем разделители тысяч и заменяем запятую на точку
            clean_amount = amount.replace(',', '.').replace(' ', '')
            amounts_float.append(float(clean_amount))
        except ValueError:
            continue

    return max(amounts_float) if amounts_float else "Не удалось извлечь сумму"


# Пример использования:
if __name__ == "__main__":

    for image_path in ['images/img.jpg', 'images/img_2.jpg',
                       'images/img2.jpg']:

        # 1. Получаем область с итогом
        roi = extract_total_region(image_path)

        if roi is not None:
            # 2. Извлекаем сумму из области
            total = extract_max_amount(roi)
            print(f"Итоговая сумма: {total}")
        else:
            print("Ключевые слова не найдены")

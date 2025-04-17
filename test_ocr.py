import cv2
import pytesseract
import re

# Настройка Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_receipt_data(image_path):
    # Загрузка изображения
    img = cv2.imread(image_path)
    if img is None:
        print(f"Ошибка: не удалось загрузить изображение {image_path}")
        return []

    # Простая предобработка
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Распознавание текста
    text = pytesseract.image_to_string(thresh, lang='rus')

    # Разбиваем текст на строки
    with open('text_test_ocr.txt','w', encoding='utf-8') as file:
        file.write(text)
    #
    # with open('text_test_ocr.txt','r') as file:
    #     content = file.read()
    #     print(content)

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Ищем строки с ценами (содержат два числа через пробелы)
    items = []
    previous_line = False
    for line in lines:
        # Ищем паттерн: текст + число + число
        match = re.search(r'(.+?)(\d+[.,]\d{2})\s+(\d+[.,]\d{2})$', line)
        if match:
            name = match.group(1).strip()
            quantity = match.group(2)
            price = match.group(3)
            items.append([name, quantity, price])
            previous_line = True
        else:
            if items:
                if re.fullmatch(r'^\D+$', line) and previous_line:
                    items[-1][0]+=f' {line}'
                else:
                    previous_line = False

    return items


# Обработка чека
result = extract_receipt_data('images/img_2.jpg')

# Вывод результатов
if not result:
    print("Не удалось распознать данные чека.")
else:
    print("Распознанные позиции:")
    for i, (name, qty, price) in enumerate(result, 1):
        print(f"{i}. {name} - {qty} шт. - {price} руб.")
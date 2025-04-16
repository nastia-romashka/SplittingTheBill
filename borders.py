import cv2
import pytesseract
# нужно установить Tesseract по ссылке:  https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # укажи свой путь тут

def crop_receipt_with_ocr(img_path, output_path='images/cropped_img.jpg'):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Адаптивная бинаризация
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # Используем pytesseract для получения координат текста
    data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT, lang='rus+eng')
    x_min, y_min = img.shape[1], img.shape[0]
    x_max, y_max = 0, 0
    found = False

    for i in range(len(data['text'])):
        text = data['text'][i]
        if text.strip() == '':
            continue

        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)
        found = True

    if not found:
        print("❌ Текст не найден — не удалось обрезать чек.")
        return None

    """# Добавим отступа
    pad = 10
    x_min = max(0, x_min - pad)
    y_min = max(0, y_min - pad)
    x_max = min(img.shape[1], x_max + pad)
    y_max = min(img.shape[0], y_max + pad)"""

    cropped = img[y_min:y_max, x_min:x_max]
    cv2.imwrite(output_path, cropped)

    #print(f"Чек обрезан и сохранён в {output_path}")

    return cropped, (x_min, y_min, x_max, y_max)

if __name__ == '__main__':
    img_path = 'images/img4.jpg'
    img, receipt_contour = crop_receipt_with_ocr(img_path)

import cv2
import numpy as np

def detect_receipt_contour(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Уменьшим шум
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Чёткий порог
    edged = cv2.Canny(blurred, 50, 150)

    # Найдём контуры
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    receipt_contour = None
    max_area = 0

    for cnt in contours:
        # Аппроксимация прямоугольника
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

        # Если это четырёхугольник и достаточно большой — возможно, чек
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > max_area:
                receipt_contour = approx
                max_area = area

    return img, receipt_contour

def crop_receipt_by_contour(img, contour, output_path='cropped_receipt.jpg'):
    if contour is None:
        print("Контур чека не найден.")
        return

    pts = contour.reshape(4, 2)

    # Упорядочим точки: [верх-лево, верх-право, низ-право, низ-лево]
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # Ширина и высота финального изображения
    (tl, tr, br, bl) = rect
    width = max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))
    height = max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))

    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Преобразуем перспективу
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (int(width), int(height)))

    cv2.imwrite(output_path, warped)
    print(f"Сохранено: {output_path}")


if __name__ == '__main__':
    img_path = 'images/receipt.jpg'
    img, receipt_contour = detect_receipt_contour(img_path)
    crop_receipt_by_contour(img, receipt_contour)

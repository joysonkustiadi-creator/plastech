import cv2
import numpy as np


def scan_qr_from_image(pil_image):
    """
    Scan QR code dari gambar menggunakan OpenCV (tanpa dependency pyzbar/zbar).

    Parameter:
        pil_image: PIL.Image

    Return:
        String hasil decode QR code, atau None jika tidak ada QR terdeteksi.
    """
    # Convert PIL -> OpenCV (BGR)
    img = np.array(pil_image.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)

    if not data:
        return None

    return data
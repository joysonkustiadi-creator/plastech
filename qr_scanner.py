import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np

def scan_qr_from_image(pil_image):
    # Convert PIL → OpenCV
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    decoded = decode(img)
    if not decoded:
        return None
    
    return decoded[0].data.decode("utf-8")

from PIL import Image
import io
import numpy as np

def image_to_bytes(image, format='PNG'):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def bytes_to_image(image_bytes):
    return Image.open(io.BytesIO(image_bytes))

def resize_image(image, max_width=800, max_height=600):
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

def prepare_image_for_yolo(image):
    return np.array(image)
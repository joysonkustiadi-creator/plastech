import qrcode
from PIL import Image

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Pastikan hasil berupa PIL.Image.Image
    if not isinstance(img, Image.Image):
        img = img.convert("RGB")

    return img


def generate_disposal_qr():
    # Satu QR untuk seluruh sistem demo
    qr_data = "PLASTECH_BIN_DEMO"
    return generate_qr_code(qr_data)
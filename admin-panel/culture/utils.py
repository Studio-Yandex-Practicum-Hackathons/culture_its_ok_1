import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

PHOTO_RESIZE_QUALITY = os.getenv('PHOTO_RESIZE_QUALITY', 'medium').lower()

MAX_PHOTO_SIZE = {
    'low': (1500, 1500),
    'medium': (3000, 3000),
    'high': (4500, 4500)
}


def resize_photo(photo_path: str):
    image = Image.open(photo_path)
    image.thumbnail(MAX_PHOTO_SIZE[PHOTO_RESIZE_QUALITY], Image.LANCZOS)
    image.save(photo_path)

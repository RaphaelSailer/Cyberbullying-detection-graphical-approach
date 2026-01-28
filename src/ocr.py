from dataclasses import dataclass
from PIL import Image
import pytesseract
import cv2
import numpy as np

@dataclass
class OCRResult:
    raw_text: str

def preprocess_for_ocr(img_path: str) -> np.ndarray:
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(img_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def ocr_image(img_path: str) -> OCRResult:
    processed = preprocess_for_ocr(img_path)
    pil_img = Image.fromarray(processed)
    text = pytesseract.image_to_string(pil_img)
    return OCRResult(raw_text=text)
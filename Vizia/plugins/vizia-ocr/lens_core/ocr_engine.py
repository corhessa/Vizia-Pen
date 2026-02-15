import os
import pytesseract
from PIL import Image

class ViziaOCREngine:
    def __init__(self):
        self.plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tessdata_dir = os.path.join(self.plugin_dir, "tessdata")
        
        # KESİN ÇÖZÜM: Tesseract'a doğrudan dil dosyalarının olduğu 'tessdata'
        # klasörünün tam yolunu öğretiyoruz. (Önceden bir üst klasörü vermiştik).
        os.environ["TESSDATA_PREFIX"] = self.tessdata_dir
        
        self._find_tesseract()

    def _find_tesseract(self):
        portable_path = os.path.join(self.plugin_dir, "tesseract_bin", "tesseract.exe")
        
        if os.path.exists(portable_path):
            pytesseract.pytesseract.tesseract_cmd = portable_path
            print(f"[Vizia Lens] Motor hazır: {portable_path}")
        else:
            print("[Vizia Lens] Kritik Hata: Tesseract taşınabilir motoru bulunamadı!")

    def extract_text(self, image_path, lang="eng"):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            print(f"OCR Hatası: {e}")
            return ""
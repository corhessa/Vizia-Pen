import os
import pytesseract
from PIL import Image

class ViziaOCREngine:
    def __init__(self):
        self.plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tessdata_dir = os.path.join(self.plugin_dir, "tessdata")
        self._find_tesseract()

    def _find_tesseract(self):
        # Tesseract'ı doğrudan kendi eklenti klasörümüzün içinde arıyoruz
        portable_path = os.path.join(self.plugin_dir, "tesseract_bin", "tesseract.exe")
        
        if os.path.exists(portable_path):
            pytesseract.pytesseract.tesseract_cmd = portable_path
        else:
            print("Kritik Hata: Tesseract taşınabilir motoru bulunamadı!")

    def extract_text(self, image_path, lang="eng"):
        try:
            # tessdata klasörünü özel olarak Tesseract'a bildiriyoruz
            config = f'--tessdata-dir "{self.tessdata_dir}"'
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang, config=config)
            return text.strip()
        except Exception as e:
            print(f"OCR Hatası: {e}")
            return ""
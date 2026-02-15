import os
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class LanguageDownloader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, lang_code, tessdata_dir):
        super().__init__()
        self.lang_code = lang_code
        self.tessdata_dir = tessdata_dir
        # Doğrudan Tesseract'ın resmi repolarından "tessdata_best" kalitesini çeker
        self.url = f"https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/{lang_code}.traineddata"

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded = 0
            
            save_path = os.path.join(self.tessdata_dir, f"{self.lang_code}.traineddata")
            
            with open(save_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    downloaded += len(data)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        self.progress.emit(percent)
                        
            self.finished.emit(True, self.lang_code)
        except Exception as e:
            self.finished.emit(False, str(e))

class LanguageManager:
    def __init__(self):
        self.plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tessdata_dir = os.path.join(self.plugin_dir, "tessdata")
        if not os.path.exists(self.tessdata_dir):
            os.makedirs(self.tessdata_dir)

    def is_installed(self, lang_code):
        path = os.path.join(self.tessdata_dir, f"{lang_code}.traineddata")
        return os.path.exists(path)

    def delete_language(self, lang_code):
        path = os.path.join(self.tessdata_dir, f"{lang_code}.traineddata")
        if os.path.exists(path):
            os.remove(path)
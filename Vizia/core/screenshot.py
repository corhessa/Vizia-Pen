# core/screenshot.py

import os
import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap

class ScreenshotManager:
    @staticmethod
    def save_screenshot(crop_rect=None, save_folder=None):
        try:
            screen = QApplication.primaryScreen()
            if not screen: return False
            
            pixmap = screen.grabWindow(0)
            
            if crop_rect and not crop_rect.isNull() and crop_rect.isValid():
                if crop_rect.width() > 0 and crop_rect.height() > 0:
                    pixmap = pixmap.copy(crop_rect)

            # Kayıt yeri kontrolü
            if not save_folder or not isinstance(save_folder, str) or not save_folder.strip():
                save_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Vizia Screenshots")
                
            if not os.path.exists(save_folder):
                try: os.makedirs(save_folder)
                except: save_folder = os.path.join(os.path.expanduser("~"), "Desktop") # Hata varsa masaüstüne dön

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Vizia_{timestamp}.png"
            full_path = os.path.join(save_folder, filename)
            
            pixmap.save(full_path, "png")
            return True
        except Exception as e:
            print(f"Screenshot Error: {e}")
            return False
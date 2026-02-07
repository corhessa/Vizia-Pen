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
            if not screen:
                print("Hata: Ekran algılanamadı.")
                return False
            
            # Tam ekran görüntüsünü al
            # grabWindow(0) tüm ekranı kapsar
            pixmap = screen.grabWindow(0)
            
            # Eğer kırpma alanı varsa ve geçerliyse kırp
            if crop_rect and not crop_rect.isNull() and crop_rect.isValid():
                # DPI ölçekleme sorunlarını önlemek için sınırları kontrol et
                if crop_rect.width() > 0 and crop_rect.height() > 0:
                    pixmap = pixmap.copy(crop_rect)

            # Kayıt klasörü kontrolü (Boşsa varsayılanı kullan)
            if not save_folder or not isinstance(save_folder, str) or not save_folder.strip():
                save_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Vizia Screenshots")
                
            # Klasör yoksa oluştur
            if not os.path.exists(save_folder):
                try:
                    os.makedirs(save_folder)
                except OSError:
                    # İzin hatası vb. olursa masaüstüne dön
                    save_folder = os.path.join(os.path.expanduser("~"), "Desktop")

            # Dosya adını oluştur
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Vizia_{timestamp}.png"
            full_path = os.path.join(save_folder, filename)
            
            # Kaydet
            success = pixmap.save(full_path, "png")
            return success

        except Exception as e:
            print(f"Screenshot Critical Error: {e}")
            return False
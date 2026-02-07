# core/screenshot.py

import os
import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QStandardPaths

class ScreenshotManager:
    @staticmethod
    def save_screenshot(crop_rect=None):
        """
        Ekran görüntüsünü alır ve Resimler klasörüne kaydeder.
        Başarılı olursa True döner.
        """
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0) # Tüm masaüstünü al
        
        # Eğer alan seçildiyse kırp
        if crop_rect:
            # High DPI ekranlar için piksel oranını hesapla
            dpr = screen.devicePixelRatio()
            x = int(crop_rect.x() * dpr)
            y = int(crop_rect.y() * dpr)
            w = int(crop_rect.width() * dpr)
            h = int(crop_rect.height() * dpr)
            screenshot = screenshot.copy(x, y, w, h)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pics = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        
        # Klasör yoksa oluştur (güvenlik için)
        if not os.path.exists(pics):
            os.makedirs(pics)
            
        path = os.path.join(pics, f"Vizia_{timestamp}.png")
        
        try:
            return screenshot.save(path)
        except Exception:
            return False
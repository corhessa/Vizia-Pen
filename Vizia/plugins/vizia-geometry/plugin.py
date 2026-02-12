import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication

# Plugin klasörünü path'e ekle
current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    sys.path.append(current_folder)

try:
    from toolbox import GeometryToolbox
except Exception as e:
    with open(os.path.join(current_folder, "hata_logu.txt"), "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    raise e

class ViziaPlugin:
    def __init__(self):
        self.name = "Geometri Stüdyosu"
        self.icon = "icons/geometry.png"
        self.id = "geometry_studio"
        self.toolbar = None

    def run(self, overlay):
        """Eklentiye tıklandığında araç çubuğunu başlatır."""
        try:
            if not self.toolbar:
                self.toolbar = GeometryToolbox(overlay)
                self._position_toolbar(overlay)
                
            self.toolbar.show()
            self.toolbar.raise_()
            
            if hasattr(overlay, 'plugin_windows'):
                overlay.plugin_windows.register(self.toolbar)
                
        except Exception as e:
            print(f"Plugin Run Hatası: {e}")
            with open(os.path.join(current_folder, "run_hata_logu.txt"), "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())

    def _position_toolbar(self, overlay):
        """Toolbox'ı ana Toolbar'ın yanına yerleştirir."""
        if not self.toolbar or not overlay: return
        
        # Ana Toolbar'ı bulmaya çalış
        main_toolbar = getattr(overlay, 'toolbar', None)
        
        target_x = 0
        target_y = 0
        
        if main_toolbar and main_toolbar.isVisible():
            # Ana toolbar'ın hemen sağına koy
            target_x = main_toolbar.x() + main_toolbar.width() + 15
            target_y = main_toolbar.y()
        else:
            # Toolbar yoksa sağ alt köşe civarına koy
            screen_geo = QApplication.primaryScreen().geometry()
            target_x = screen_geo.width() - self.toolbar.width() - 50
            target_y = screen_geo.height() - self.toolbar.height() - 100

        # Ekran dışına taşıyor mu kontrol et (Basit check)
        screen_w = overlay.width()
        if target_x + self.toolbar.width() > screen_w:
            # Sığmıyorsa toolbar'ın soluna almayı dene
            if main_toolbar:
                target_x = main_toolbar.x() - self.toolbar.width() - 15
        
        self.toolbar.move(int(target_x), int(target_y))
# plugins/vizia-geometry/plugin.py
import sys
import os
import traceback

# Plugin klasörünü path'e ekle
current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    sys.path.append(current_folder)

try:
    from toolbox import GeometryToolbox, ShapeCanvasOverlay
except Exception as e:
    # Hata oluşursa log dosyasına yaz
    with open(os.path.join(current_folder, "hata_logu.txt"), "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    raise e

class ViziaPlugin:
    def __init__(self):
        self.name = "Geometri Stüdyosu"
        self.icon = "icons/geometry.png"
        self.id = "geometry_studio"
        self.canvas_overlay = None
        self.toolbar = None

    def run(self, overlay):
        """Eklentiye tıklandığında canvas overlay ve araç çubuğunu başlatır."""
        try:
            if self.canvas_overlay is None or not self.canvas_overlay.isVisible():
                # Canvas overlay'i ana pencere üzerinde oluştur
                self.canvas_overlay = ShapeCanvasOverlay(overlay)
                self.canvas_overlay.setGeometry(overlay.rect())
                self.canvas_overlay.lower()  # Kalem katmanının arkasına gönder
                self.canvas_overlay.show()

                # Araç çubuğunu canvas'a bağla ve ANA OVERLAY'i parametre olarak ver
                self.toolbar = GeometryToolbox(self.canvas_overlay, overlay)
                self._position_toolbar(overlay)
                self.toolbar.show()
                
                # Pencereleri plugin window manager'a kaydet
                if hasattr(overlay, 'plugin_windows'):
                    overlay.plugin_windows.register(self.canvas_overlay)
                    overlay.plugin_windows.register(self.toolbar)
            else:
                self.toolbar.activateWindow()
                self.toolbar.raise_()
                
        except Exception as e:
            print(f"Plugin Run Hatası: {e}")
            with open(os.path.join(current_folder, "run_hata_logu.txt"), "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())

    def _position_toolbar(self, overlay):
        if self.toolbar and overlay:
            tw = min(self.toolbar.sizeHint().width(), overlay.width() - 40)
            self.toolbar.setFixedWidth(tw)
            x = overlay.x() + (overlay.width() - tw) // 2
            y = overlay.y() + overlay.height() - self.toolbar.height() - 30
            self.toolbar.move(x, y)
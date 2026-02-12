import sys
import os
import traceback

# Plugin klasörünü path'e ekle
current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    sys.path.append(current_folder)

try:
    from toolbox import GeometryToolbox
    # ShapeCanvasOverlay import etmiyoruz çünkü artık MainOverlay kullanıyoruz
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
                # Toolbox'a doğrudan ana overlay'i veriyoruz
                self.toolbar = GeometryToolbox(overlay)
                self._position_toolbar(overlay)
                
            self.toolbar.show()
            self.toolbar.raise_()
            
            # Pencereleri plugin window manager'a kaydet (Z-Order için)
            if hasattr(overlay, 'plugin_windows'):
                overlay.plugin_windows.register(self.toolbar)
                
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
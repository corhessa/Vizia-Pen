# plugins/vizia-geometry/plugin.py
import sys
import os

# Aynı klasördeki modülleri import edebilmek için yol ayarı
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toolbox import GeometryToolbox, ShapeCanvasOverlay


class ViziaPlugin:
    def __init__(self):
        self.name = "Geometri Stüdyosu"
        self.icon = "icons/geometry.png"
        self.id = "geometry_studio"
        self.canvas_overlay = None
        self.toolbar = None

    def run(self, overlay):
        """Eklentiye tıklandığında canvas overlay ve araç çubuğunu başlatır.

        *overlay*: Vizia'nın ana penceresi veya üst widget.
        Şekil canvas'ı overlay'in *içine* yerleştirilir;
        böylece kalem çizimleri canvas'ın arkasından geçer.
        Araç çubuğu ise her zaman üstte duran, sürüklenebilir paneldir.
        Panel, WindowDoesNotAcceptFocus bayrağı ile kalem modunu bozmaz.
        """
        if self.canvas_overlay is None or not self.canvas_overlay.isVisible():
            # Canvas overlay'i ana pencere üzerinde oluştur
            self.canvas_overlay = ShapeCanvasOverlay(overlay)
            self.canvas_overlay.setGeometry(overlay.rect())
            self.canvas_overlay.lower()  # Kalem katmanının arkasına gönder
            self.canvas_overlay.show()

            # Araç çubuğunu canvas'a bağla
            self.toolbar = GeometryToolbox(self.canvas_overlay)
            self._position_toolbar(overlay)
            self.toolbar.show()
        else:
            self.toolbar.activateWindow()
            self.toolbar.raise_()

    def _position_toolbar(self, overlay):
        """Araç çubuğunu overlay'in alt-ortasına konumlandırır."""
        if self.toolbar and overlay:
            tw = min(self.toolbar.sizeHint().width(), overlay.width() - 40)
            self.toolbar.setFixedWidth(tw)
            x = overlay.x() + (overlay.width() - tw) // 2
            y = overlay.y() + overlay.height() - self.toolbar.height() - 30
            self.toolbar.move(x, y)
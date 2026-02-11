import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor

# Aynı klasördeki modülleri bulsun
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from toolbox import GeometryToolbox, ShapeCanvasOverlay
except ImportError as e:
    print("HATA: Modüller bulunamadı. Lütfen 'toolbox.py' ve 'shapes.py' dosyalarının")
    print("bu dosya ile aynı klasörde olduğundan emin olun.")
    print(f"Detay: {e}")
    sys.exit(1)


def main():
    app = QApplication(sys.argv)

    # Tüm masaüstünü kaplayan şeffaf overlay (simülasyon penceresi yok)
    screen = app.primaryScreen().geometry()

    canvas = ShapeCanvasOverlay()
    canvas.setWindowFlags(
        Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
    )
    canvas.setAttribute(Qt.WA_TranslucentBackground, True)
    canvas.setGeometry(screen)
    
    canvas.show()

    # Araç çubuğunu canvas'a bağla
    toolbox = GeometryToolbox(canvas)
    tw = min(toolbox.sizeHint().width(), screen.width() - 40)
    toolbox.setFixedWidth(tw)
    x = screen.x() + (screen.width() - tw) // 2
    y = screen.y() + screen.height() - toolbox.height() - 60
    toolbox.move(x, y)
    toolbox.show()

    print("Vizia Geometri Stüdyosu başlatıldı ✓")
    print("  • Şekil butonuna tıklayın, masaüstünde sürükleyerek çizin")
    print("  • ➕ ile merkeze şekil ekleyin")
    print("  • ↩ Geri al  |  🗑 Sil  |  ⊘ Tümünü temizle")
    print("  • Paneli sürükleyerek taşıyın (sol üst tutamak)")
    print("  • Renk butonuna tıklayarak renk paleti açın")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
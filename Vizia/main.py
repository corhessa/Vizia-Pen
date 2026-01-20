import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from core import DrawingOverlay, ModernToolbar

if __name__ == "__main__":
    # Yüksek DPI ekranlar için ölçeklendirme
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Uygulama bileşenlerini oluştur
    overlay = DrawingOverlay()
    toolbar = ModernToolbar(overlay)
    
    # Bileşenleri birbirine bağla
    overlay.toolbar = toolbar
    
    # Araç çubuğunu göster ve uygulamayı başlat
    toolbar.show()
    sys.exit(app.exec_())
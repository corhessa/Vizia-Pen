import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.overlay import DrawingOverlay
from core.toolbar import ModernToolbar

if __name__ == "__main__":
    # Yüksek DPI ekranlar için ölçeklendirme
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Uygulama ikonunu assets klasöründen yükle
    base_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_path, "Assets", "VIZIA.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Uygulama bileşenlerini oluştur
    overlay = DrawingOverlay()
    toolbar = ModernToolbar(overlay)
    
    # Bileşenleri birbirine bağla
    overlay.toolbar = toolbar
    
    # Araç çubuğunu göster ve uygulamayı başlat
    toolbar.show()
    sys.exit(app.exec_())
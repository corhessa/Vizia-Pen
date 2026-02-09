import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.overlay import DrawingOverlay
from core.toolbar import ModernToolbar

def resource_path(relative_path):
    """ Dosya yollarını EXE uyumlu hale getirir """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Yüksek DPI ekranlar için ölçeklendirme (Bulanıklığı önler)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Uygulama ikonunu yükle
    icon_path = resource_path("Vizia/Assets/VIZIA.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 1. Uygulama bileşenlerini oluştur
    overlay = DrawingOverlay()
    toolbar = ModernToolbar(overlay)
    
    # 2. Bileşenleri birbirine bağla
    overlay.toolbar = toolbar
    
    
    # 4. Araç çubuğunu göster
    toolbar.show()

    # 5. Uygulama döngüsünü başlat ve çıkış kodunu yakala
    exit_code = app.exec_()
    
    sys.exit(exit_code)
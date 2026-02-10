import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# [EKLEME] Çalışma dizini sorunlarını önlemek için dizini main.py'nin olduğu yere sabitle
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.overlay import DrawingOverlay
from core.toolbar import ModernToolbar

def resource_path(relative_path):
    """ Dosya yollarını hem EXE hem de IDE için uyumlu hale getirir """
    try:
        base_path = sys._MEIPASS
    except Exception:
        # [DÜZELTME] os.path.abspath(".") yerine dosyanın kendi konumunu baz al
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # [DÜZELTME] Bazı sistemlerde DPI ölçeklendirmesi çakışmaya neden olabilir
    # Bu ayarların QApplication oluşturulmadan hemen önce yapılması kritiktir
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # [DÜZELTME] İkon yolu kontrolü
    # Assets klasörü Vizia içinde mi yoksa bir üstte mi kontrol et
    icon_path = resource_path("Assets/VIZIA.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # Alternatif yol denemesi
        icon_path = resource_path("Vizia/Assets/VIZIA.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    
    try:
        # 1. Uygulama bileşenlerini oluştur
        overlay = DrawingOverlay()
        toolbar = ModernToolbar(overlay)
        
        # 2. Bileşenleri birbirine bağla
        overlay.toolbar = toolbar
        
        # 4. Araç çubuğunu göster
        toolbar.show()
        
        print("Vizia Pen başlatıldı...") # Terminalden takip için
        
        # 5. Uygulama döngüsünü başlat
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Başlatma sırasında kritik hata oluştu: {e}")
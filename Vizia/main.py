import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.overlay import DrawingOverlay
from core.toolbar import ModernToolbar

# [FIX 10] DPI Ayarı: Programın en başında, QApplication oluşmadan önce yapılmalı.
try:
    if os.name == 'nt': # Sadece Windows için
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per-Monitor DPI Aware
except Exception:
    pass

def resource_path(relative_path):
    """ Dosya yollarını EXE ve Geliştirme Ortamı uyumlu hale getirir """
    try:
        # PyInstaller ile paketlenmişse
        base_path = sys._MEIPASS
    except Exception:
        # [FIX 3] Geliştirme ortamında (IDE/Terminal) çalışma dizini sorunu çözümü
        base_path = os.path.dirname(os.path.abspath(__file__))
        # main.py "Vizia" klasörü içindeyse, bir üst klasöre çıkmaya gerek yok
        # çünkü assets klasörü main.py ile aynı seviyedeki "Assets" içinde olabilir 
        # veya proje yapısına göre ayarlanmalı. 
        # Mevcut yapıda: Vizia/main.py ve Vizia/Assets var.
        
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Yüksek DPI ekranlar için ölçeklendirme
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Vizia Pen")
    
    # Uygulama ikonunu yükle
    # resource_path zaten Vizia klasörünü baz alıyorsa "Assets/VIZIA.ico" yeterli olabilir
    # Ancak proje yapısı karışık olduğu için güvenli yolu deniyoruz.
    icon_path = resource_path("Assets/VIZIA.ico")
    if not os.path.exists(icon_path):
        # Yedek deneme (Vizia klasörü altındaysa)
        icon_path = resource_path("Vizia/Assets/VIZIA.ico")
  
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
sys.exit(app.exec_())
import sys
import os
import traceback
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

# ✅ Global Hata Yakalayıcı (Crash Kalkanı)
# Beklenmedik bir hata oluştuğunda programın sessizce kapanmasını engeller.
def exception_hook(exctype, value, tb):
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print("Vizia Kritik Hata:\n", error_msg)
    
    # Kullanıcıya hatayı göster ama programı kapatma
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Beklenmedik bir hata oluştu!")
    msg.setInformativeText("Uygulama çalışmaya devam etmeye çalışacak.")
    msg.setDetailedText(error_msg)
    msg.setWindowTitle("Vizia Pen Hatası")
    msg.exec_()

sys.excepthook = exception_hook

# Yüksek DPI ve OpenGL ayarları
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Çalışma dizinini ayarla
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    from core.overlay import DrawingOverlay
    from core.toolbar import ModernToolbar

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    # İkon yükle
    icon_path = resource_path("Assets/VIZIA.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Ana pencereleri başlat
    overlay = DrawingOverlay()
    toolbar = ModernToolbar(overlay)

    overlay.toolbar = toolbar
    toolbar.show()

    print("Vizia Pen başlatıldı (Güvenli Mod)...")
    sys.exit(app.exec_())
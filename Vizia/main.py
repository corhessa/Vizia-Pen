import sys
import os

from PyQt5.QtCore import QCoreApplication, Qt

# ✅ TÜM attribute'lar önce
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# Opsiyonel ama WebEngine + overlay için stabil
# QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


if __name__ == "__main__":

    app = QApplication(sys.argv)   # ✅ SADECE BURADA

    # Çalışma dizini sabitle
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

    # ikon
    icon_path = resource_path("Assets/VIZIA.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    overlay = DrawingOverlay()
    toolbar = ModernToolbar(overlay)

    overlay.toolbar = toolbar
    toolbar.show()

    print("Vizia Pen başlatıldı...")

    sys.exit(app.exec_())

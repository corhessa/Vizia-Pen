"""
Ana uygulama - standalone ve plugin modları
"""
import sys
from PyQt5.QtWidgets import QApplication
from .ui.main_window import MainWindow


class ViziaEditApp:
    """Vizia Edit uygulaması (standalone + plugin)"""
    
    def __init__(self, overlay=None):
        """
        Args:
            overlay: Vizia-Pen overlay (plugin mod için)
        """
        self.overlay = overlay
        self.app = None
        self.main_window = None
        self.is_plugin_mode = overlay is not None
    
    def setup_application(self):
        """QApplication instance'ını oluşturur"""
        # Standalone mod için yeni QApplication
        if not self.is_plugin_mode:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
        else:
            # Plugin mod - mevcut QApplication'ı kullan
            self.app = QApplication.instance()
            if not self.app:
                self.app = QApplication(sys.argv)
    
    def show(self):
        """Uygulamayı gösterir"""
        self.setup_application()
        
        # Ana pencereyi oluştur
        self.main_window = MainWindow()
        
        # Plugin modda overlay'e entegre et (opsiyonel)
        if self.is_plugin_mode and self.overlay:
            # TODO: Overlay entegrasyonu
            pass
        
        # Pencereyi göster
        self.main_window.show()
        
        # Standalone modda event loop'u çalıştır
        if not self.is_plugin_mode:
            sys.exit(self.app.exec_())
    
    def close(self):
        """Uygulamayı kapatır"""
        if self.main_window:
            self.main_window.close()


def run_standalone():
    """Standalone mod çalıştırıcı"""
    app = ViziaEditApp()
    app.show()


if __name__ == "__main__":
    run_standalone()

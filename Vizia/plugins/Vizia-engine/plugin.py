import sys
import os
import traceback

# Bulunduğumuz klasörü sisteme tanıt
current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    sys.path.insert(0, current_folder)

# --- ENGINE IMPORT DENEMESİ ---
ViziaEngineItem = None
engine_error = None

try:
    # Import from engine package
    from engine.viewport import ViziaEngineItem
    print("✅ [ENGINE] Motor başarıyla yüklendi.")

except Exception as e:
    engine_error = str(e)
    print("❌ [ENGINE] Gerçek hata aşağıda:")
    traceback.print_exc()


class ViziaPlugin:
    def __init__(self):
        self.name = "Vizia Engine (3D Lab)"
        # İkonu "icons" klasöründe ara
        self.icon = "icons/game.png"
        self.id = "engine"
        self.window = None

    def run(self, overlay):
        # Eğer motor yüklenemediyse hata mesajı göster
        if ViziaEngineItem is None:
            print(f"🛑 HATA: Engine başlatılamıyor. Sebep: {engine_error}")
            if hasattr(overlay, 'show_toast'):
                overlay.show_toast("Motor Hatası! (Terminale bak)")
            return

        try:
            from PyQt5.QtWidgets import QApplication

            if self.window is None or not self.window.isVisible():
                self.window = ViziaEngineItem(overlay)
                self.window.show()

                # Ortala
                screen = QApplication.primaryScreen().geometry()
                x = (screen.width() - self.window.width()) // 2
                y = (screen.height() - self.window.height()) // 2
                self.window.move(x, y)
            else:
                self.window.raise_()
                self.window.activateWindow()

        except Exception as e:
            print(f"🛑 [ENGINE RUN ERROR]: {e}")

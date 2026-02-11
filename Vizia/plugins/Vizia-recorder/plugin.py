# plugins/Vizia-recorder/plugin.py
import sys
import os

# 1. Şu anki klasörü bul (Dedektiflik)
current_folder = os.path.dirname(os.path.abspath(__file__))

# 2. Bu klasörü Python'un kütüphane yoluna ekle (ZORLA)
if current_folder not in sys.path:
    sys.path.insert(0, current_folder)

# 3. Import Denemesi
RecorderController = None

try:
    # Dosya adını doğrudan çağırıyoruz (recorder_ui.py)
    import recorder_ui
    RecorderController = recorder_ui.RecorderController
    print("✅ [RECORDER] Modül başarıyla yüklendi.")
except ImportError as e:
    print(f"❌ [RECORDER] Import Hatası: {e}")
    # Dosya listesini yazdıralım ki hata nerede görelim
    print(f"   Baktığım yer: {current_folder}")
    print(f"   İçindeki dosyalar: {os.listdir(current_folder)}")
except AttributeError:
    print("❌ [RECORDER] Sınıf Hatası: recorder_ui.py var ama içinde 'RecorderController' yok!")
except Exception as e:
    print(f"❌ [RECORDER] Beklenmeyen Hata: {e}")

class ViziaPlugin:
    def __init__(self):
        self.name = "Ekran Kaydı"
        # İkon kontrolü
        if os.path.exists(os.path.join(current_folder, "icons", "record.png")):
             self.icon = "icons/record.png"
        else:
             self.icon = "record.png"
             
        self.id = "recorder"
        self.window = None

    def run(self, overlay):
        # Eğer modül yüklenemediyse programı ÇÖKERTME, sadece uyar
        if RecorderController is None:
            print("🛑 [RECORDER] HATA: RecorderController yüklenemediği için açılmıyor.")
            if hasattr(overlay, 'show_toast'):
                overlay.show_toast("HATA: Kayıt dosyaları bulunamadı!")
            return

        if self.window is None:
            self.window = RecorderController(overlay.settings, overlay)
        
        if not self.window.isVisible():
            self.window.show()
            try:
                from PyQt5.QtWidgets import QApplication
                screen = QApplication.primaryScreen().geometry()
                x = (screen.width() - self.window.width()) // 2
                y = (screen.height() - self.window.height()) // 2
                self.window.move(x, y)
            except:
                pass
            
            # Pencereyi plugin window manager'a kaydet
            if hasattr(overlay, 'plugin_windows'):
                sub_wins = []
                if hasattr(self.window, 'mini_panel'):
                    sub_wins.append(self.window.mini_panel)
                if hasattr(self.window, 'camera_widget'):
                    sub_wins.append(self.window.camera_widget)
                overlay.plugin_windows.register(self.window, sub_windows=sub_wins if sub_wins else None)
        else:
            self.window.raise_()
            self.window.activateWindow()
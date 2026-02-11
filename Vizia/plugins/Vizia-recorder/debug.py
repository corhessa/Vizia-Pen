import sys
import os
from PyQt5.QtWidgets import QApplication

# 1. KLASÖRÜN YERİNİ TESPİT ET VE SİSTEME TANIT
# Bu kısım, recorder_ui.py ve diğer dosyaların bulunmasını sağlar.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. ANA PROJEYİ TAKLİT EDEN (MOCK) YAPI ---
class MockOverlay:
    def __init__(self):
        # Settings simülasyonu için 'self' referansı veriyoruz
        self.settings = self
        self.drawing_mode = "pen"
        # Ayarları geçici olarak bu sözlükte tutacağız
        self.temp_settings = {
            "video_save_path": os.path.join(os.path.expanduser("~"), "Videos"),
            "fps": 24,
            "quality": "high"
        }
    
    # Ayar okuma metodu (self.settings.get çağrıldığında çalışır)
    def get(self, key): 
        val = self.temp_settings.get(key, "")
        print(f"[DEBUG GET]: {key} -> {val}")
        return val
    
    # Ayar yazma metodu (self.settings.set çağrıldığında çalışır)
    def set(self, key, value):
        self.temp_settings[key] = value
        print(f"[DEBUG SET]: {key} güncellendi -> {value}")
    
    # Ekrana mesaj basma simülasyonu
    def show_toast(self, msg): 
        print(f"*** [EKRAN MESAJI / TOAST]: {msg} ***")
    
    # Pencereyi öne getirme simülasyonu
    def bring_ui_to_front(self):
        print("[DEBUG]: Ana arayüz öne getirme tetiklendi.")

# --- 3. UYGULAMAYI BAŞLAT ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Sahte ana yapı objesini oluştur
    overlay = MockOverlay()
    
    print("--- Vizia Recorder Bağımsız Geliştirme Modu Başlatılıyor ---")
    
    try:
        # recorder_ui.py içindeki RecorderController sınıfını çağır
        from recorder_ui import RecorderController
        
        # Pencereyi oluştur ve göster
        window = RecorderController(overlay.settings, overlay)
        window.show()
        
        print("✅ Başarılı: Recorder penceresi açıldı.")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ KRİTİK HATA: Modül başlatılamadı!")
        print(f"Hata Mesajı: {e}")
        # Hatanın tam yerini görmek için traceback basalım
        import traceback
        traceback.print_exc()
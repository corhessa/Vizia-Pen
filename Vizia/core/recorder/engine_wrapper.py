# Vizia/core/recorder/engine_wrapper.py

import ctypes
import os
import sys

class CppEngineWrapper:
    def __init__(self):
        self.lib = None
        self.load_library()
        
    def load_library(self):
        try:
            # İşletim sistemine göre DLL yolunu bul
            # Bu dosya (engine_wrapper.py) -> core/recorder içinde
            # DLL dosyası -> core/cpp_engine/build içinde olacak
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Yolu: Vizia/core/recorder/../../core/cpp_engine/build/recorder.dll
            dll_path = os.path.join(current_dir, "..", "cpp_engine", "build", "recorder.dll")
            dll_path = os.path.normpath(dll_path)
            
            if not os.path.exists(dll_path):
                print(f"[UYARI] C++ DLL bulunamadı: {dll_path}")
                print("Simülasyon modunda çalışılacak. (Gerçek kayıt yapılmayacak)")
                return

            # DLL'i yükle
            self.lib = ctypes.CDLL(dll_path)
            
            # --- C++ Fonksiyonlarını Python'a Tanıt ---
            
            # Fonksiyon: void start_capture(const char* path, int fps)
            self.lib.start_capture.argtypes = [ctypes.c_char_p, ctypes.c_int]
            self.lib.start_capture.restype = None
            
            # Fonksiyon: void stop_capture()
            self.lib.stop_capture.argtypes = []
            self.lib.stop_capture.restype = None
            
            # Fonksiyon: void pause_capture(bool pause)
            self.lib.pause_capture.argtypes = [ctypes.c_bool]
            self.lib.pause_capture.restype = None
            
            print("Vizia C++ Engine Başarıyla Yüklendi.")
            
        except Exception as e:
            print(f"DLL Yükleme Hatası: {e}")
            self.lib = None

    def start(self, save_path, fps=60):
        """Kaydı başlatır."""
        if self.lib:
            # Python string'i C string'e (byte array) çevirmemiz lazım
            b_path = save_path.encode('utf-8')
            self.lib.start_capture(b_path, fps)
        else:
            print(f"[Simülasyon] Kayıt Başladı: {save_path} (FPS: {fps})")

    def stop(self):
        """Kaydı bitirir."""
        if self.lib:
            self.lib.stop_capture()
        else:
            print("[Simülasyon] Kayıt Durduruldu.")

    def pause(self, is_paused):
        """Kaydı duraklatır veya devam ettirir."""
        if self.lib:
            self.lib.pause_capture(is_paused)
        else:
            status = "DURAKLATILDI" if is_paused else "DEVAM EDİYOR"
            print(f"[Simülasyon] Kayıt Durumu: {status}")
import threading
import time
import os
import sys
import ctypes
import numpy as np
import cv2

# Windows DPI Ayarı (Ölçekleme sorununu çözen sihirli kod)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # PER_MONITOR_DPI_AWARE
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

class CppEngineWrapper:
    def __init__(self):
        self.is_recording = False
        self.stop_event = threading.Event()
        self.dll = None
        self.cap_obj = None
        self.mode = "PYTHON"
        self._load_cpp_engine()

    def _load_cpp_engine(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            cpp_dir = os.path.join(base_path, "..", "..", "core", "cpp_engine")
            build_dir = os.path.join(cpp_dir, "build")
            dll_path = os.path.join(build_dir, "recorder.dll")
            
            if dll_path and os.path.exists(dll_path):
                self.dll = ctypes.CDLL(dll_path)
                
                # init_engine artık w, h alıyor!
                self.dll.init_engine.argtypes = [ctypes.c_int, ctypes.c_int]
                self.dll.init_engine.restype = ctypes.c_void_p
                
                self.dll.grab_frame.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte)]
                self.dll.grab_frame.restype = ctypes.c_bool
                self.dll.release_engine.argtypes = [ctypes.c_void_p]
                
                print("[Vizia Engine] C++ Modu Hazır")
                self.mode = "CPP"
            else:
                self.mode = "PYTHON"
        except Exception as e:
            print(f"[Vizia Engine] Hata: {e}")
            self.mode = "PYTHON"

    def _record_loop(self, filename, fps):
        # 1. Gerçek fiziksel çözünürlüğü al
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        
        print(f"[REC] Algılanan Çözünürlük: {width}x{height}")

        filename = filename.replace(".mp4", ".avi")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        # 4 Kanal (BGRA) Buffer
        frame_size = width * height * 4
        c_buffer = (ctypes.c_ubyte * frame_size)()
        c_pointer = ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_ubyte))
        
        # 2. C++ Motorunu bu çözünürlükle başlat (Senkronizasyon)
        if self.mode == "CPP":
            self.cap_obj = self.dll.init_engine(width, height)
        
        frame_interval = 1.0 / fps
        
        while not self.stop_event.is_set():
            start_time = time.time()
            try:
                if self.mode == "CPP" and self.cap_obj:
                    if self.dll.grab_frame(self.cap_obj, c_pointer):
                        # Veriyi al
                        frame = np.ctypeslib.as_array(c_buffer).reshape(height, width, 4)
                        # BGRA -> BGR Dönüşümü
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        out.write(frame_bgr)
            except Exception:
                pass
            
            elapsed = time.time() - start_time
            time.sleep(max(0, frame_interval - elapsed))
            
        out.release()
        if self.mode == "CPP" and self.cap_obj:
            self.dll.release_engine(self.cap_obj)
        print("[REC] Kayıt Bitti.")

    def start(self, save_path, fps=30):
        if self.is_recording: return
        self.is_recording = True
        self.stop_event.clear()
        
        folder = os.path.dirname(save_path)
        if not os.path.exists(folder): os.makedirs(folder)

        self.thread = threading.Thread(target=self._record_loop, args=(save_path, fps))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_recording = False
        self.stop_event.set()
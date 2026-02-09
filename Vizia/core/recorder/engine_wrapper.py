import threading
import time
import os
import ctypes
import numpy as np
import cv2
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QRect

# Windows DPI Ayarı
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

class CppEngineWrapper(QObject):
    # Kamera görüntüsünü (varsa) UI'da göstermek için sinyal
    frame_captured = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.is_paused = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set() # Başlangıçta çalışır durumda
        
        self.dll = None
        self.cap_obj = None
        self.mode = "PYTHON"
        
        # Kamera Ayarları
        self.use_camera = False
        self.cam_cap = None
        self.cam_geometry = None # (x, y, w, h)
        
        self._load_cpp_engine()

    def _load_cpp_engine(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            cpp_dir = os.path.join(base_path, "..", "..", "core", "cpp_engine")
            build_dir = os.path.join(cpp_dir, "build")
            dll_path = os.path.join(build_dir, "recorder.dll")
            
            if dll_path and os.path.exists(dll_path):
                self.dll = ctypes.CDLL(dll_path)
                self.dll.init_engine.argtypes = [ctypes.c_int, ctypes.c_int]
                self.dll.init_engine.restype = ctypes.c_void_p
                self.dll.grab_frame.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte)]
                self.dll.grab_frame.restype = ctypes.c_bool
                self.dll.release_engine.argtypes = [ctypes.c_void_p]
                print("[Vizia Engine] C++ Modu Aktif")
                self.mode = "CPP"
            else:
                self.mode = "PYTHON"
        except Exception as e:
            print(f"[Vizia Engine] Hata: {e}")
            self.mode = "PYTHON"

    def update_camera_config(self, active, geometry_rect):
        """UI tarafından çağrılır: Kameranın durumu ve konumu"""
        self.use_camera = active
        # QRect'i (x, y, w, h) tuple'ına çevir
        if geometry_rect:
            self.cam_geometry = (geometry_rect.x(), geometry_rect.y(), geometry_rect.width(), geometry_rect.height())
        else:
            self.cam_geometry = None

    def _init_camera(self):
        if self.use_camera:
            # 0: Varsayılan Kamera
            self.cam_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            # Performans için düşük çözünürlük yeterli (köşede duracak)
            self.cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def _release_camera(self):
        if self.cam_cap:
            self.cam_cap.release()
            self.cam_cap = None

    def pause(self):
        self.is_paused = True
        self.pause_event.clear()
        
    def resume(self):
        self.is_paused = False
        self.pause_event.set()

    def _record_loop(self, filename, target_fps):
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        
        print(f"[REC] Başlatıldı: {width}x{height} @ {target_fps} FPS")

        # Dosya uzantısını AVI yap (OpenCV ile en uyumlu format)
        if not filename.endswith(".avi"):
            filename = os.path.splitext(filename)[0] + ".avi"
            
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, target_fps, (width, height))
        
        frame_size = width * height * 4
        c_buffer = (ctypes.c_ubyte * frame_size)()
        c_pointer = ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_ubyte))
        
        if self.mode == "CPP":
            self.cap_obj = self.dll.init_engine(width, height)
        
        self._init_camera()
        
        start_time = time.time()
        frames_written = 0
        
        # Ekran görüntüsü alamama durumu için boş frame
        last_valid_frame = np.zeros((height, width, 3), dtype=np.uint8)

        while not self.stop_event.is_set():
            # Duraklatıldıysa bekle
            if not self.pause_event.is_set():
                # Pause süresini start_time'a eklememiz lazım yoksa senkron kayar
                pause_start = time.time()
                self.pause_event.wait()
                start_time += (time.time() - pause_start)
            
            # 1. Ekran Görüntüsü Al
            current_frame = None
            if self.mode == "CPP" and self.cap_obj:
                if self.dll.grab_frame(self.cap_obj, c_pointer):
                    frame_raw = np.ctypeslib.as_array(c_buffer).reshape(height, width, 4)
                    current_frame = frame_raw[:, :, :3] # BGRA -> BGR
            else:
                # Python modu yedeği (mss vb. eklenebilir, şimdilik boş geçiyor)
                pass

            if current_frame is None:
                current_frame = last_valid_frame
            else:
                last_valid_frame = current_frame.copy()

            # 2. Kamera Görüntüsü Ekle (Picture-in-Picture)
            if self.use_camera and self.cam_cap and self.cam_cap.isOpened() and self.cam_geometry:
                ret, cam_frame = self.cam_cap.read()
                if ret:
                    # UI'da önizleme sinyali
                    rgb_preview = cv2.cvtColor(cam_frame, cv2.COLOR_BGR2RGB)
                    self.frame_captured.emit(rgb_preview)
                    
                    # Videoya montajla
                    cx, cy, cw, ch = self.cam_geometry
                    # Sınır kontrolü
                    if cx >= 0 and cy >= 0 and (cx + cw) <= width and (cy + ch) <= height:
                        try:
                            cam_resized = cv2.resize(cam_frame, (cw, ch))
                            current_frame[cy:cy+ch, cx:cx+cw] = cam_resized
                        except: pass

            # 3. Akıllı Senkronizasyon (Smart Sync)
            # Gerçekte ne kadar zaman geçti?
            elapsed_time = time.time() - start_time
            # Bu zamana göre kaç kare yazmış olmalıydık?
            expected_frames = int(elapsed_time * target_fps)
            # Yazmamız gereken fark
            frames_to_add = expected_frames - frames_written
            
            # Eğer bilgisayar yavaş kaldıysa kare tekrarı yap, hızlıysa bekleme zaten loop dönecek
            if frames_to_add > 0:
                for _ in range(frames_to_add):
                    out.write(current_frame)
                    frames_written += 1
            
            # CPU'yu rahatlat (çok küçük bir uyku)
            time.sleep(0.001)

        out.release()
        self._release_camera()
        
        if self.mode == "CPP" and self.cap_obj:
            self.dll.release_engine(self.cap_obj)
        print("[REC] Kayıt Bitti.")

    def start(self, save_path, fps=20):
        # 20 FPS ideal (Hem akıcı hem kasmayan)
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
        self.pause_event.set() # Pause'daysa çıksın
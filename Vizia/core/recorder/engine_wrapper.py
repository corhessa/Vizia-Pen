# Vizia/core/recorder/engine_wrapper.py

import threading
import time
import os
import ctypes
import numpy as np
import cv2
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex
from PyQt5.QtGui import QImage

# Fallback: mss (C++ çalışmazsa devreye girecek)
try:
    import mss
except ImportError:
    mss = None

class CameraThread(QThread):
    # Preview Image (QImage) ve Kayıt Frame'i (Raw BGR)
    frame_ready = pyqtSignal(QImage, np.ndarray)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.mutex = QMutex()

    def run(self):
        try:
            if os.name == 'nt':
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(0)
            
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)

            if not self.cap or not self.cap.isOpened():
                return

            # Performans ayarı (İsteğe bağlı, desteklenmezse yoksayar)
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            except: pass

            self.running = True
            while self.running:
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    try:
                        # 1. Kayıt için orijinal frame (BGR) kalsın
                        frame_bgr = frame.copy()

                        # 2. Arayüz (UI) için RGBA dönüşümü (Crash önleyici)
                        frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                        h, w, ch = frame_rgba.shape
                        bytes_per_line = ch * w
                        
                        qt_img = QImage(frame_rgba.data, w, h, bytes_per_line, QImage.Format_RGBA8888).copy()
                        
                        self.frame_ready.emit(qt_img, frame_bgr)
                    except: pass
                else:
                    time.sleep(0.1)
                
                time.sleep(0.03) # ~30 FPS
                
        except Exception as e:
            print(f"Kamera Kritik Hata: {e}")
        finally:
            if self.cap: self.cap.release()

    def stop(self):
        self.running = False
        self.wait()


class CppEngineWrapper(QObject):
    preview_signal = pyqtSignal(QImage)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set() 
        
        self.dll = None
        self.cap_obj = None
        self.mode = "PYTHON" # Varsayılan
        
        self.camera_thread = None
        self.cam_geometry = None 
        self.mutex_cam = QMutex()
        self.last_cam_frame_bgr = None 
        
        self._load_cpp_engine()

    def _load_cpp_engine(self):
        """ C++ DLL dosyasını yüklemeyi dener """
        try:
            # DLL yolunu bul
            base_path = os.path.dirname(os.path.abspath(__file__))
            # Vizia/core/recorder -> Vizia/core/cpp_engine/build/recorder.dll
            cpp_dir = os.path.join(base_path, "..", "cpp_engine")
            build_dir = os.path.join(cpp_dir, "build")
            dll_path = os.path.join(build_dir, "recorder.dll")
            
            if dll_path and os.path.exists(dll_path):
                self.dll = ctypes.CDLL(dll_path)
                
                # init_engine(int w, int h) -> CapContext*
                self.dll.init_engine.argtypes = [ctypes.c_int, ctypes.c_int]
                self.dll.init_engine.restype = ctypes.c_void_p
                
                # grab_frame(CapContext* ctx, uchar* buffer, size_t size) -> bool
                # YENİ: size_t bufferSize parametresi eklendi
                self.dll.grab_frame.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t]
                self.dll.grab_frame.restype = ctypes.c_bool
                
                # release_engine(CapContext* ctx) -> void
                self.dll.release_engine.argtypes = [ctypes.c_void_p]
                
                self.mode = "CPP"
                print(f"[INFO] C++ Motoru Yüklendi: {dll_path}")
            else:
                print("[WARN] DLL bulunamadı, Python modu (mss) kullanılacak.")
                self.mode = "PYTHON"
        except Exception as e:
            print(f"[ERROR] C++ Yükleme Hatası: {e}")
            self.mode = "PYTHON"

    def update_camera_config(self, active, geometry_rect):
        self.mutex_cam.lock()
        if geometry_rect:
            self.cam_geometry = (geometry_rect.x(), geometry_rect.y(), geometry_rect.width(), geometry_rect.height())
        else:
            self.cam_geometry = None
        self.mutex_cam.unlock()

        if active: self.start_camera_preview()
        else: self.stop_camera_preview()

    def start_camera_preview(self):
        if self.camera_thread is None or not self.camera_thread.isRunning():
            self.camera_thread = CameraThread()
            self.camera_thread.frame_ready.connect(self._handle_camera_data)
            self.camera_thread.start()

    def stop_camera_preview(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None

    def _handle_camera_data(self, qt_img, raw_frame_bgr):
        self.preview_signal.emit(qt_img)
        self.mutex_cam.lock()
        self.last_cam_frame_bgr = raw_frame_bgr
        self.mutex_cam.unlock()

    def pause(self):
        self.pause_event.clear()
        
    def resume(self):
        self.pause_event.set()

    def _record_loop(self, filename, target_fps):
        # Ekran Çözünürlüğü
        if os.name == 'nt':
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
        else:
            width, height = 1920, 1080 

        if not filename.endswith(".mp4"):
            filename = os.path.splitext(filename)[0] + ".mp4"
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, target_fps, (width, height))
        
        # --- MOTOR HAZIRLIĞI ---
        c_buffer = None
        c_pointer = None
        frame_size = width * height * 4 # BGRA
        
        # C++ Başlatma
        if self.mode == "CPP":
            try:
                c_buffer = (ctypes.c_ubyte * frame_size)()
                c_pointer = ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_ubyte))
                self.cap_obj = self.dll.init_engine(width, height)
                if not self.cap_obj:
                    print("[ERROR] C++ init başarısız, Python'a dönülüyor.")
                    self.mode = "PYTHON"
            except:
                self.mode = "PYTHON"
        
        # Python (MSS) Başlatma (Yedek veya Ana Mod)
        sct = None
        monitor = None
        if self.mode == "PYTHON" and mss:
            sct = mss.mss()
            if len(sct.monitors) > 1: monitor = sct.monitors[1]
            else: monitor = sct.monitors[0]

        start_time = time.time()
        frames_written = 0
        last_valid_frame = np.zeros((height, width, 3), dtype=np.uint8)

        print(f"[REC] Kayıt Başladı ({self.mode}): {filename}")

        while not self.stop_event.is_set():
            if not self.pause_event.is_set():
                pause_start = time.time()
                self.pause_event.wait()
                start_time += (time.time() - pause_start)
            
            current_frame = None
            
            # --- 1. GÖRÜNTÜ YAKALAMA ---
            if self.mode == "CPP" and self.cap_obj:
                # C++ Motoru (Güvenli Çağrı)
                if self.dll.grab_frame(self.cap_obj, c_pointer, ctypes.c_size_t(frame_size)):
                    frame_raw = np.ctypeslib.as_array(c_buffer).reshape(height, width, 4)
                    current_frame = frame_raw[:, :, :3] # Alpha kanalını at
                else:
                    # C++ hata verirse frame atla veya Python'a geç (burada atlıyoruz)
                    pass
            
            elif self.mode == "PYTHON" and sct:
                # Python Motoru (MSS)
                try:
                    img = sct.grab(monitor)
                    frame_np = np.array(img)
                    current_frame = cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)
                    if current_frame.shape[:2] != (height, width):
                         current_frame = cv2.resize(current_frame, (width, height))
                except: pass

            if current_frame is None: 
                current_frame = last_valid_frame.copy()
            else: 
                last_valid_frame = current_frame

            # --- 2. KAMERA OVERLAY ---
            self.mutex_cam.lock()
            cam_frame = self.last_cam_frame_bgr
            geo = self.cam_geometry
            self.mutex_cam.unlock()

            if cam_frame is not None and geo:
                cx, cy, cw, ch = geo
                y1, y2 = max(0, cy), min(height, cy + ch)
                x1, x2 = max(0, cx), min(width, cx + cw)
                
                if y2 > y1 and x2 > x1:
                    try:
                        target_w, target_h = x2 - x1, y2 - y1
                        cam_resized = cv2.resize(cam_frame, (target_w, target_h))
                        current_frame[y1:y2, x1:x2] = cam_resized
                    except: pass

            out.write(current_frame)
            
            # FPS Kontrolü
            elapsed_time = time.time() - start_time
            expected_frames = int(elapsed_time * target_fps)
            frames_to_add = expected_frames - frames_written
            
            if frames_to_add > 0:
                for _ in range(frames_to_add):
                    out.write(current_frame)
                    frames_written += 1
            
            time.sleep(0.001) # CPU Dostu

        out.release()
        if self.mode == "CPP" and self.cap_obj:
            self.dll.release_engine(self.cap_obj)
        if sct: sct.close()
        print("[REC] Kayıt Bitti.")
    
    def start(self, save_path, fps=24):
        if self.is_recording: return
        self.is_recording = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._record_loop, args=(save_path, fps))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_recording = False
        self.stop_event.set()
        self.pause_event.set()
        self.stop_camera_preview()
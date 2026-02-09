import threading
import time
import os
import ctypes
import numpy as np
import cv2
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

# --- GÜVENLİ KAMERA THREAD'İ ---
class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.mutex = QMutex()
        self.latest_frame = None

    def run(self):
        try:
            # KRİTİK DEĞİŞİKLİK: CAP_DSHOW'u kaldırdım.
            # DSHOW, bazı sürücülerde doğrudan CRASH verdirtiyor.
            # Varsayılan (Backend=0 veya Auto) en güvenli yoldur.
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap or not self.cap.isOpened():
                print("Kamera varsayılan modda açılamadı.")
                return

            # Çözünürlük ayarı (Hata verirse yoksay, programı çökertme)
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            except: pass

            self.running = True
            while self.running:
                # Güvenli okuma
                try:
                    ret, frame = self.cap.read()
                    if ret and frame is not None and frame.size > 0:
                        self.mutex.lock()
                        self.latest_frame = frame.copy()
                        self.mutex.unlock()
                        self.frame_ready.emit(frame)
                    else:
                        time.sleep(0.1)
                except:
                    # Okuma hatası olursa döngüyü kırma, tekrar dene
                    pass
                
                time.sleep(0.033) # ~30 FPS
                
        except Exception as e:
            print(f"Kamera Thread Hatası: {e}")
        finally:
            if self.cap:
                self.cap.release()

    def stop(self):
        self.running = False
        self.wait()

    def get_frame(self):
        self.mutex.lock()
        try:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None
        finally:
            self.mutex.unlock()


class CppEngineWrapper(QObject):
    preview_signal = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.is_paused = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set() 
        
        self.dll = None
        self.cap_obj = None
        self.mode = "PYTHON"
        
        self.camera_thread = None
        self.cam_geometry = None 
        
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
                self.mode = "CPP"
            else:
                self.mode = "PYTHON"
        except Exception:
            self.mode = "PYTHON"

    def update_camera_config(self, active, geometry_rect):
        if geometry_rect:
            self.cam_geometry = (geometry_rect.x(), geometry_rect.y(), geometry_rect.width(), geometry_rect.height())
        else:
            self.cam_geometry = None

        if active:
            self.start_camera_preview()
        else:
            self.stop_camera_preview()

    def start_camera_preview(self):
        if self.camera_thread is None or not self.camera_thread.isRunning():
            self.camera_thread = CameraThread()
            self.camera_thread.frame_ready.connect(self._handle_camera_frame)
            self.camera_thread.start()

    def stop_camera_preview(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None

    def _handle_camera_frame(self, frame_bgr):
        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            self.preview_signal.emit(rgb)
        except: pass

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
        
        if not filename.endswith(".mp4"):
            filename = os.path.splitext(filename)[0] + ".mp4"
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, target_fps, (width, height))
        
        frame_size = width * height * 4
        c_buffer = (ctypes.c_ubyte * frame_size)()
        c_pointer = ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_ubyte))
        
        if self.mode == "CPP":
            self.cap_obj = self.dll.init_engine(width, height)
        
        start_time = time.time()
        frames_written = 0
        last_valid_frame = np.zeros((height, width, 3), dtype=np.uint8)

        while not self.stop_event.is_set():
            if not self.pause_event.is_set():
                pause_start = time.time()
                self.pause_event.wait()
                start_time += (time.time() - pause_start)
            
            current_frame = None
            if self.mode == "CPP" and self.cap_obj:
                if self.dll.grab_frame(self.cap_obj, c_pointer):
                    frame_raw = np.ctypeslib.as_array(c_buffer).reshape(height, width, 4)
                    current_frame = frame_raw[:, :, :3] 
            
            if current_frame is None: current_frame = last_valid_frame
            else: last_valid_frame = current_frame.copy()

            if self.camera_thread and self.cam_geometry:
                cam_frame = self.camera_thread.get_frame()
                if cam_frame is not None:
                    cx, cy, cw, ch = self.cam_geometry
                    if cx >= 0 and cy >= 0 and (cx + cw) <= width and (cy + ch) <= height:
                        try:
                            cam_resized = cv2.resize(cam_frame, (cw, ch))
                            current_frame[cy:cy+ch, cx:cx+cw] = cam_resized
                        except: pass

            out.write(current_frame)
            
            elapsed_time = time.time() - start_time
            expected_frames = int(elapsed_time * target_fps)
            frames_to_add = expected_frames - frames_written
            
            if frames_to_add > 0:
                for _ in range(frames_to_add):
                    out.write(current_frame)
                    frames_written += 1
            
            time.sleep(0.001)

        out.release()
        if self.mode == "CPP" and self.cap_obj:
            self.dll.release_engine(self.cap_obj)
        print("[REC] Kayıt Bitti.")

    def start(self, save_path, fps=24):
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
        self.pause_event.set()
        self.stop_camera_preview()
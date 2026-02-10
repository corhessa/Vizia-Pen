# Vizia/core/recorder/engine_wrapper.py

import threading
import time
import os
import ctypes
import numpy as np
import cv2
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex
from PyQt5.QtGui import QImage

# Fallback: mss
try:
    import mss
except ImportError:
    mss = None

class CameraThread(QThread):
    # ARTIK NUMPY DEĞİL, DOĞRUDAN QIMAGE GÖNDERİYORUZ (DAHA GÜVENLİ)
    frame_ready = pyqtSignal(QImage, np.ndarray) # (Preview Image, Raw Recording Frame)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.mutex = QMutex()

    def run(self):
        try:
            # Windows için en güvenli backend CAP_DSHOW'dur.
            # Eğer yine açılmazsa cv2.CAP_MSMF denebilir ama DSHOW genelde çökmez.
            if os.name == 'nt':
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(0)
            
            # Kamera açılmazsa 2. deneme (backend belirtmeden)
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)

            if not self.cap or not self.cap.isOpened():
                print("Kamera donanımı bulunamadı.")
                return

            # Çözünürlüğü zorlamayalım, varsayılan neyse o gelsin (Stabilite için)
            self.running = True
            
            while self.running:
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    try:
                        # --- KRİTİK ÇÖZÜM: RGBA (32-bit) DÖNÜŞÜMÜ ---
                        # RGB888 (24-bit) hizalama sorunu yaratabilir ve çökertebilir.
                        # RGBA8888 (32-bit) her zaman 4-byte hizalıdır. ASLA ÇÖKMEZ.
                        frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                        h, w, ch = frame_rgba.shape
                        bytes_per_line = ch * w
                        
                        # QImage'i burada oluşturup kopyalıyoruz.
                        # UI thread'ine "saf" bir PyQt nesnesi gidiyor.
                        qt_img = QImage(frame_rgba.data, w, h, bytes_per_line, QImage.Format_RGBA8888).copy()
                        
                        # Preview için QImage, Kayıt için orijinal frame (BGR) gönder
                        self.frame_ready.emit(qt_img, frame)
                        
                    except Exception as e:
                        print(f"Dönüştürme Hatası: {e}")
                else:
                    time.sleep(0.1)
                
                time.sleep(0.03) # ~30 FPS
                
        except Exception as e:
            print(f"Kamera Kritik Hata: {e}")
        finally:
            if self.cap:
                self.cap.release()

    def stop(self):
        self.running = False
        self.wait()


class CppEngineWrapper(QObject):
    preview_signal = pyqtSignal(QImage) # Sinyal artık QImage taşıyor
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set() 
        
        self.mode = "PYTHON" # C++ DLL'ini kapattık, crash riskini sıfırladık.
        
        self.camera_thread = None
        self.cam_geometry = None 
        self.mutex_cam = QMutex()
        
        # Son gelen kamera karesini kayıt için sakla
        self.last_cam_frame_bgr = None 

    def update_camera_config(self, active, geometry_rect):
        self.mutex_cam.lock()
        if geometry_rect:
            self.cam_geometry = (geometry_rect.x(), geometry_rect.y(), geometry_rect.width(), geometry_rect.height())
        else:
            self.cam_geometry = None
        self.mutex_cam.unlock()

        if active:
            self.start_camera_preview()
        else:
            self.stop_camera_preview()

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
        # 1. Preview sinyalini UI'a gönder
        self.preview_signal.emit(qt_img)
        
        # 2. Kayıt için ham veriyi sakla
        self.mutex_cam.lock()
        self.last_cam_frame_bgr = raw_frame_bgr
        self.mutex_cam.unlock()

    def pause(self):
        self.pause_event.clear()
        
    def resume(self):
        self.pause_event.set()

    def _record_loop(self, filename, target_fps):
        # Ekran boyutlarını al
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
        
        # MSS (Screen Capture) Hazırlığı
        sct = None
        monitor = None
        if mss:
            sct = mss.mss()
            # Genellikle monitors[1] ana ekrandır.
            if len(sct.monitors) > 1:
                monitor = sct.monitors[1]
            else:
                monitor = sct.monitors[0]

        start_time = time.time()
        frames_written = 0
        last_valid_frame = np.zeros((height, width, 3), dtype=np.uint8)

        print(f"[REC] Kayıt Başladı: {filename}")

        while not self.stop_event.is_set():
            if not self.pause_event.is_set():
                pause_start = time.time()
                self.pause_event.wait()
                start_time += (time.time() - pause_start)
            
            current_frame = None
            
            # --- EKRAN GÖRÜNTÜSÜ AL ---
            if sct:
                try:
                    img = sct.grab(monitor)
                    frame_np = np.array(img)
                    # MSS BGRA döndürür, BGR'a çevir
                    current_frame = cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)
                    
                    # Boyut uyuşmazlığı varsa resize et
                    if current_frame.shape[0] != height or current_frame.shape[1] != width:
                         current_frame = cv2.resize(current_frame, (width, height))
                except Exception as e:
                    print(f"Screen Grab Error: {e}")

            if current_frame is None: 
                current_frame = last_valid_frame.copy()
            else: 
                last_valid_frame = current_frame

            # --- KAMERA OVERLAY ---
            self.mutex_cam.lock()
            cam_frame = self.last_cam_frame_bgr
            geo = self.cam_geometry
            self.mutex_cam.unlock()

            if cam_frame is not None and geo:
                cx, cy, cw, ch = geo
                
                # Taşma Kontrolleri
                y1 = max(0, cy)
                y2 = min(height, cy + ch)
                x1 = max(0, cx)
                x2 = min(width, cx + cw)
                
                if y2 > y1 and x2 > x1:
                    try:
                        target_w = x2 - x1
                        target_h = y2 - y1
                        
                        # Kamerayı o boyuta getir
                        cam_resized = cv2.resize(cam_frame, (target_w, target_h))
                        
                        # Ana kareye yapıştır
                        current_frame[y1:y2, x1:x2] = cam_resized
                    except: 
                        pass

            out.write(current_frame)
            
            # FPS Sabitleme
            elapsed_time = time.time() - start_time
            expected_frames = int(elapsed_time * target_fps)
            frames_to_add = expected_frames - frames_written
            
            if frames_to_add > 0:
                for _ in range(frames_to_add):
                    out.write(current_frame)
                    frames_written += 1
            
            # CPU'yu yakmamak için minik uyku
            time.sleep(0.002)

        out.release()
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
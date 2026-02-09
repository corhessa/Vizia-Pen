# Vizia/core/recorder/recorder_ui.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QComboBox, QFrame, QApplication, QFileDialog, QGraphicsDropShadowEffect, QListView)
from PyQt5.QtCore import Qt, QTimer, QDate, QTime, QPoint
from PyQt5.QtGui import QColor
import os
import sys
import datetime

# Motoru yükle
try:
    from core.recorder.camera_widget import ResizableCameraWidget
    from core.recorder.engine_wrapper import CppEngineWrapper
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from core.recorder.camera_widget import ResizableCameraWidget
    from core.recorder.engine_wrapper import CppEngineWrapper

# --- MİNİ KONTROL PANELİ (Kayıt Sırasında Çıkan) ---
class MiniControlPanel(QWidget):
    def __init__(self, parent_controller):
        super().__init__()
        self.controller = parent_controller
        # Madde 1: Her zaman en üstte ve kalemden etkilenmemesi için Tool/StaysOnTop
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(260, 60)
        
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 260, 60)
        self.container.setStyleSheet("""
            QFrame { background-color: #1c1c1e; border: 1px solid #333; border-radius: 30px; }
            QLabel { color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 14px; }
        """)
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,150))
        self.container.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(20, 5, 20, 5)
        
        # Kırmızı Nokta (Yanıp Sönen)
        self.dot = QLabel("●"); self.dot.setStyleSheet("color: red; font-size: 14px;")
        layout.addWidget(self.dot)
        
        # Süre
        self.lbl_time = QLabel("00:00:00")
        layout.addWidget(self.lbl_time)
        
        layout.addStretch()
        
        # Duraklat Butonu
        self.btn_pause = QPushButton("||")
        self.btn_pause.setFixedSize(32, 32)
        self.btn_pause.setCheckable(True)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setStyleSheet("""
            QPushButton { background: #333; color: white; border-radius: 16px; font-weight: bold; border: 1px solid #444; }
            QPushButton:checked { background: #faad14; color: black; border: none; } 
            QPushButton:hover { background: #444; }
        """)
        self.btn_pause.clicked.connect(self.toggle_pause)
        layout.addWidget(self.btn_pause)
        
        # Bitir Butonu
        self.btn_stop = QPushButton("■")
        self.btn_stop.setFixedSize(32, 32)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setStyleSheet("""
            QPushButton { background: #ff3b30; color: white; border-radius: 16px; font-weight: bold; font-size: 16px; border: none; }
            QPushButton:hover { background: #ff453a; }
        """)
        self.btn_stop.clicked.connect(self.stop_recording)
        layout.addWidget(self.btn_stop)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0
        self.blink_state = True
        
    def start_timer(self):
        self.elapsed_seconds = 0
        self.timer.start(1000)
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Ekranın sağ altına koy
        geo = QApplication.primaryScreen().geometry()
        self.move(geo.width() - 290, geo.height() - 130)

    def update_timer(self):
        self.elapsed_seconds += 1
        t = QTime(0,0,0).addSecs(self.elapsed_seconds)
        self.lbl_time.setText(t.toString("HH:mm:ss"))
        
        self.blink_state = not self.blink_state
        self.dot.setStyleSheet(f"color: {'red' if self.blink_state else '#555'}; font-size: 14px;")

    def toggle_pause(self, checked):
        if checked:
            self.controller.engine.pause()
            self.timer.stop()
            self.dot.setStyleSheet("color: orange;")
            self.lbl_time.setStyleSheet("color: orange;")
        else:
            self.controller.engine.resume()
            self.timer.start(1000)
            self.lbl_time.setStyleSheet("color: white;")

    def stop_recording(self):
        self.timer.stop()
        self.controller.stop_rec()
        self.close()

    # Sürükleme Mantığı (Madde 1: Kalemden etkilenmeden sürükleme)
    def mousePressEvent(self, e): 
        if e.button() == Qt.LeftButton: 
            self.old_pos = e.globalPos()
            self.raise_() # Tıklanınca en öne gel
    def mouseMoveEvent(self, e): 
        if hasattr(self, 'old_pos'): 
            delta = e.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = e.globalPos()

# --- ANA ARAYÜZ ---
class RecorderController(QWidget):
    def __init__(self, settings_manager, overlay_ref=None):
        super().__init__()
        self.settings = settings_manager
        self.overlay = overlay_ref 
        self.is_recording = False
        
        self.camera_widget = ResizableCameraWidget()
        self.engine = CppEngineWrapper()
        
        # Madde 2: Kamera görüntüsünü widget'a bağla (Canlı Önizleme)
        self.engine.frame_captured.connect(self.camera_widget.update_frame)
        
        self.mini_panel = MiniControlPanel(self)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 560) 
        
        self.initUI()
        
    def initUI(self):
        self.container = QFrame(self)
        self.container.setGeometry(15, 15, 420, 530)
        
        # Madde 4: Modern QComboBox Tasarımı
        self.container.setStyleSheet("""
            QFrame#Main { background: #121212; border: 1px solid #2a2a2a; border-radius: 24px; }
            QLabel { color: #f0f0f0; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel#H { color: #888; font-size: 11px; font-weight: bold; letter-spacing: 1px; margin-top: 15px; }
            
            QComboBox { 
                background-color: #1e1e20; 
                border: 1px solid #333; 
                border-radius: 12px; 
                padding: 10px; 
                color: white; 
                font-size: 13px;
            }
            QComboBox:hover { border-color: #555; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { 
                image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #888; margin-right: 10px; 
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e20;
                color: white;
                selection-background-color: #007aff;
                selection-color: white;
                border: 1px solid #333;
                border-radius: 5px;
                outline: none;
            }
            
            QPushButton#Path { background: #1e1e20; border: 1px solid #333; border-radius: 12px; }
            QPushButton#Path:hover { border-color: #007aff; }
        """)
        self.container.setObjectName("Main")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50); shadow.setColor(QColor(0,0,0,200)); shadow.setYOffset(10)
        self.container.setGraphicsEffect(shadow)
        
        l = QVBoxLayout(self.container); l.setContentsMargins(30, 30, 30, 30); l.setSpacing(8)
        
        # Başlık
        h = QHBoxLayout()
        ttl = QLabel("Kayıt Stüdyosu"); ttl.setStyleSheet("font-size: 24px; font-weight: 800; color: white;")
        cls = QPushButton("✕"); cls.setFixedSize(30,30); cls.clicked.connect(self.close_panel)
        cls.setStyleSheet("background: transparent; color: #666; font-size: 16px; border: none; font-weight: bold;")
        h.addWidget(ttl); h.addStretch(); h.addWidget(cls)
        l.addLayout(h); l.addSpacing(10)
        
        # Ayarlar
        l.addWidget(QLabel("SES KAYNAĞI", objectName="H"))
        self.c_mic = QComboBox(); self.c_mic.setView(QListView()) # CSS için gerekli
        self.c_mic.addItems(["Sadece Sistem Sesi", "Sistem Sesi + Mikrofon", "Sessiz"])
        l.addWidget(self.c_mic)
        
        l.addWidget(QLabel("KAMERA", objectName="H"))
        self.c_cam = QComboBox(); self.c_cam.setView(QListView())
        self.c_cam.addItems(["Kamera Kapalı", "Webcam Aktif"])
        self.c_cam.currentIndexChanged.connect(self.cam_toggle)
        l.addWidget(self.c_cam)
        
        l.addWidget(QLabel("DOSYA KONUMU", objectName="H"))
        ph = QHBoxLayout()
        self.lbl_p = QLabel("..."); self.lbl_p.setStyleSheet("color: #888;")
        btn_p = QPushButton("📂"); btn_p.setFixedSize(40,40); btn_p.setObjectName("Path"); btn_p.clicked.connect(self.ch_path)
        ph.addWidget(self.lbl_p, 1); ph.addWidget(btn_p)
        l.addLayout(ph); self.upd_path()
        
        l.addStretch()
        
        # Başlat
        self.btn_rec = QPushButton("KAYDI BAŞLAT")
        self.btn_rec.setFixedHeight(60)
        self.btn_rec.setCursor(Qt.PointingHandCursor)
        self.btn_rec.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b30, stop:1 #ff2d55);
                color: white; font-size: 16px; font-weight: bold; border-radius: 30px; border: none; 
            }
            QPushButton:hover { background: #ff453a; margin-top: -2px; }
            QPushButton:pressed { margin-top: 2px; }
        """)
        self.btn_rec.clicked.connect(self.toggle_rec)
        l.addWidget(self.btn_rec)
        
        self.mode_lbl = QLabel(f"Motor: {self.engine.mode}")
        self.mode_lbl.setAlignment(Qt.AlignCenter); self.mode_lbl.setStyleSheet("color: #444; font-size: 10px; margin-top:5px;")
        l.addWidget(self.mode_lbl)

    def upd_path(self):
        p = self.settings.get("video_save_path")
        self.lbl_p.setText(f"...{p[-30:]}" if p and len(p)>30 else (p or "Seçilmedi"))

    def ch_path(self):
        d = QFileDialog.getExistingDirectory(self, "Seç", self.settings.get("video_save_path"))
        if d: self.settings.set("video_save_path", d); self.upd_path()

    def cam_toggle(self, i):
        active = (i == 1)
        if active:
            self.camera_widget.show()
            self.camera_widget.raise_()
            geo = QApplication.primaryScreen().geometry()
            self.camera_widget.move(geo.width()-350, geo.height()-280)
        else: 
            self.camera_widget.hide()
        
        self.engine.update_camera_config(active, self.camera_widget.geometry())

    def toggle_rec(self):
        if not self.is_recording:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_dir = self.settings.get("video_save_path") or os.path.join(os.path.expanduser("~"), "Videos")
            if not os.path.exists(base_dir): os.makedirs(base_dir)
            
            fn = os.path.join(base_dir, f"Vizia_{timestamp}.avi")
            
            self.engine.update_camera_config(self.c_cam.currentIndex()==1, self.camera_widget.geometry())
            
            self.is_recording = True
            self.hide() 
            self.mini_panel.start_timer()
            
            if self.overlay: self.overlay.show_toast("🔴 Kayıt Başladı")
            self.engine.start(fn, 20) 
            
            self.btn_rec.setText("KAYDI DURDUR")
            self.btn_rec.setStyleSheet("background: #333; color: white; border-radius: 30px; font-weight: bold;")
        else:
            self.stop_rec()

    def stop_rec(self):
        self.is_recording = False
        self.engine.stop()
        self.mini_panel.hide()
        self.show()
        self.btn_rec.setText("KAYDI BAŞLAT")
        self.btn_rec.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b30, stop:1 #ff2d55); color: white; border-radius: 30px; font-weight: bold;")
        if self.overlay: self.overlay.show_toast("Video Kaydedildi ✅")

    def close_panel(self):
        self.hide()
        if not self.is_recording:
            self.camera_widget.close()

    def showEvent(self, e):
        self.mode_lbl.setText(f"Engine: {self.engine.mode}")
        self.raise_(); self.activateWindow()

    def mousePressEvent(self, e): 
        if e.button()==Qt.LeftButton: self.old=e.globalPos()
    def mouseMoveEvent(self, e): 
        if hasattr(self,'old'): self.move(self.pos()+e.globalPos()-self.old); self.old=e.globalPos()
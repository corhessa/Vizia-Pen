# Vizia/core/recorder/recorder_ui.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QComboBox, QFrame, QApplication, QFileDialog, QDialog, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QDate, QPoint
from PyQt5.QtGui import QColor, QFont, QIcon
import os
import sys

# Motoru yükle
try:
    from core.recorder.camera_widget import ResizableCameraWidget
    from core.recorder.engine_wrapper import CppEngineWrapper
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from core.recorder.camera_widget import ResizableCameraWidget
    from core.recorder.engine_wrapper import CppEngineWrapper

# --- ŞIK ONAY PENCERESİ ---
class ModernConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(400, 220)
        
        layout = QVBoxLayout(self)
        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: #1a1a1c; border: 1px solid #333; border-radius: 18px; }
            QLabel { font-family: 'Segoe UI'; }
        """)
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(40); shadow.setColor(QColor(0,0,0,150))
        container.setGraphicsEffect(shadow)
        
        inner = QVBoxLayout(container); inner.setContentsMargins(30, 30, 30, 30)
        
        t = QLabel("Kaydı Başlat"); t.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        m = QLabel("Ekran kaydı başlatılacak ve bu pencere gizlenecek.\nDuraklatmak için tekrar araç çubuğunu kullanabilirsiniz."); 
        m.setStyleSheet("font-size: 13px; color: #aaa; margin-top: 5px;")
        m.setWordWrap(True)
        
        btns = QHBoxLayout(); btns.setSpacing(15); btns.addStretch()
        
        b_cancel = QPushButton("İptal"); b_cancel.setCursor(Qt.PointingHandCursor)
        b_cancel.setStyleSheet("background: transparent; color: #888; border: none; font-weight: bold;")
        b_cancel.clicked.connect(self.reject)
        
        b_ok = QPushButton("KAYDI BAŞLAT"); b_ok.setCursor(Qt.PointingHandCursor)
        b_ok.setFixedSize(140, 40)
        b_ok.setStyleSheet("background: #007aff; color: white; border-radius: 20px; font-weight: bold; border: none;")
        b_ok.clicked.connect(self.accept)
        
        btns.addWidget(b_cancel); btns.addWidget(b_ok)
        inner.addWidget(t); inner.addWidget(m); inner.addStretch(); inner.addLayout(btns)
        layout.addWidget(container)

    def mousePressEvent(self, e): 
        if e.button() == Qt.LeftButton: self.old = e.globalPos()
    def mouseMoveEvent(self, e): 
        if hasattr(self, 'old'): delta = e.globalPos() - self.old; self.move(self.pos() + delta); self.old = e.globalPos()

# --- ANA ARAYÜZ ---
class RecorderController(QWidget):
    def __init__(self, settings_manager, overlay_ref=None):
        super().__init__()
        self.settings = settings_manager
        self.overlay = overlay_ref 
        self.is_recording = False
        
        self.camera_widget = ResizableCameraWidget()
        self.engine = CppEngineWrapper()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 550) # Geniş Arayüz
        
        self.initUI()
        
    def initUI(self):
        self.container = QFrame(self)
        self.container.setGeometry(15, 15, 420, 520)
        self.container.setStyleSheet("""
            QFrame#Main { background: #121212; border: 1px solid #2a2a2a; border-radius: 24px; }
            QLabel { color: #f0f0f0; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel#H { color: #666; font-size: 11px; font-weight: bold; letter-spacing: 1px; margin-top: 15px; }
            QComboBox { background: #1e1e20; border: 1px solid #333; padding: 10px; border-radius: 12px; color: white; }
            QComboBox::drop-down { border: none; }
            QPushButton#Path { background: #1e1e20; border: 1px solid #333; border-radius: 12px; }
            QPushButton#Path:hover { border-color: #007aff; }
        """)
        self.container.setObjectName("Main")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50); shadow.setColor(QColor(0,0,0,200)); shadow.setYOffset(10)
        self.container.setGraphicsEffect(shadow)
        
        l = QVBoxLayout(self.container); l.setContentsMargins(30, 30, 30, 30); l.setSpacing(10)
        
        # Başlık
        h = QHBoxLayout()
        ttl = QLabel("Kayıt Stüdyosu"); ttl.setStyleSheet("font-size: 24px; font-weight: 800; color: white;")
        cls = QPushButton("✕"); cls.setFixedSize(30,30); cls.clicked.connect(self.close_panel)
        cls.setStyleSheet("background: transparent; color: #666; font-size: 16px; border: none; font-weight: bold;")
        h.addWidget(ttl); h.addStretch(); h.addWidget(cls)
        l.addLayout(h); l.addSpacing(10)
        
        # Ayarlar
        l.addWidget(QLabel("MİKROFON", objectName="H"))
        self.c_mic = QComboBox(); self.c_mic.addItems(["Sistem Sesi + Mikrofon", "Sessiz"])
        l.addWidget(self.c_mic)
        
        l.addWidget(QLabel("KAMERA", objectName="H"))
        self.c_cam = QComboBox(); self.c_cam.addItems(["Kamera Kapalı", "Webcam Aktif"])
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
        
        # Mod Göstergesi
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
        if i==0: self.camera_widget.hide(); self.camera_widget.set_camera_active(False)
        else: 
            self.camera_widget.show(); self.camera_widget.set_camera_active(True)
            geo = QApplication.primaryScreen().geometry()
            self.camera_widget.move(geo.width()-350, geo.height()-280)

    def toggle_rec(self):
        if not self.is_recording:
            if ModernConfirmDialog(self).exec_():
                self.is_recording = True
                fn = os.path.join(self.settings.get("video_save_path"), f"Vizia_{int(QDate.currentDate().toJulianDay())}.mp4")
                self.hide()
                if self.overlay: self.overlay.show_toast("🔴 Kayıt Başladı")
                self.engine.start(fn, 60)
                self.btn_rec.setText("KAYDI DURDUR")
                self.btn_rec.setStyleSheet("background: #333; color: white; border-radius: 30px; font-weight: bold;")
        else:
            self.stop_rec()

    def stop_rec(self):
        self.is_recording = False
        self.engine.stop()
        self.btn_rec.setText("KAYDI BAŞLAT")
        self.btn_rec.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b30, stop:1 #ff2d55); color: white; border-radius: 30px; font-weight: bold;")
        if self.overlay: self.overlay.show_toast("Video Kaydedildi ✅")

    def close_panel(self):
        self.hide() # Kayıt devam ediyorsa sadece gizle
        self.camera_widget.close()

    def showEvent(self, e):
        self.mode_lbl.setText(f"Engine: {self.engine.mode}") # Modu güncelle
        self.raise_(); self.activateWindow()

    def mousePressEvent(self, e): 
        if e.button()==Qt.LeftButton: self.old=e.globalPos()
    def mouseMoveEvent(self, e): 
        if hasattr(self,'old'): self.move(self.pos()+e.globalPos()-self.old); self.old=e.globalPos()
# Vizia/core/recorder/recorder_ui.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QComboBox, QFrame, QApplication, QFileDialog, QDialog, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QColor

import os
import sys

# Relative import hatası almamak için güvenli yöntem
try:
    from core.recorder.camera_widget import ResizableCameraWidget
    from core.recorder.engine_wrapper import CppEngineWrapper
except ImportError:
    # Eğer doğrudan çalıştırılırsa
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from core.recorder.camera_widget import ResizableCameraWidget
    from core.recorder.engine_wrapper import CppEngineWrapper

# --- MODERN ONAY PENCERESİ (Çökme Sorununu Çözer) ---
class ModernConfirmDialog(QDialog):
    def __init__(self, parent=None, title="Onay", message="İşlemi onaylıyor musunuz?"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(350, 200)
        
        layout = QVBoxLayout(self)
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame { background-color: #1c1c1e; border: 1px solid #3a3a3c; border-radius: 15px; }
            QLabel { color: white; font-family: 'Segoe UI'; }
        """)
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,100))
        self.container.setGraphicsEffect(shadow)
        
        inner_layout = QVBoxLayout(self.container)
        inner_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title); lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #007aff;")
        lbl_msg = QLabel(message); lbl_msg.setStyleSheet("font-size: 14px; color: #ccc;")
        lbl_msg.setWordWrap(True)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.setStyleSheet("background-color: transparent; color: #888; border: none; font-weight: bold;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_ok = QPushButton("Başlat")
        btn_ok.setFixedSize(100, 35)
        btn_ok.setStyleSheet("background-color: #34c759; color: white; border-radius: 8px; font-weight: bold;")
        btn_ok.clicked.connect(self.accept)
        
        btn_layout.addStretch(); btn_layout.addWidget(btn_cancel); btn_layout.addWidget(btn_ok)
        
        inner_layout.addWidget(lbl_title); inner_layout.addSpacing(10); inner_layout.addWidget(lbl_msg); inner_layout.addStretch(); inner_layout.addLayout(btn_layout)
        layout.addWidget(self.container)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos') and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

# --- ANA KONTROLCÜ ---
class RecorderController(QWidget):
    def __init__(self, settings_manager, overlay_ref=None):
        super().__init__()
        self.settings = settings_manager
        self.overlay = overlay_ref # Overlay referansı (kilitleme için)
        self.is_recording = False
        self.is_paused = False
        
        # Bileşenler
        self.camera_widget = ResizableCameraWidget()
        self.engine = CppEngineWrapper()
        
        # Pencere Ayarları
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 520) # Daha geniş ve ferah
        
        # Başlarken Overlay'i Kilitle
        if self.overlay: self.overlay.set_input_locked(True)
        
        self.initUI()
        
    def initUI(self):
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 420, 520)
        self.container.setStyleSheet("""
            QFrame#MainFrame { 
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1c1c1e, stop:1 #121212);
                border: 1px solid #3a3a3c; 
                border-radius: 20px; 
            }
            QLabel { color: white; font-size: 14px; font-family: 'Segoe UI', sans-serif; background: transparent; border: none; }
            QComboBox { 
                background-color: #2c2c2e; color: white; 
                border: 1px solid #3a3a3c; border-radius: 8px; padding: 10px; font-size: 13px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox:hover { border-color: #007aff; }
            QPushButton#PathBtn { background-color: #3a3a3c; border-radius: 8px; border: none; }
            QPushButton#PathBtn:hover { background-color: #4a4a4c; }
        """)
        self.container.setObjectName("MainFrame")
        
        # Gölge Efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25); shadow.setColor(QColor(0,0,0,150)); shadow.setYOffset(5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 1. HEADER
        header = QHBoxLayout()
        title = QLabel("Ekran Kaydı")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: white; letter-spacing: 0.5px;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close_panel)
        btn_close.setStyleSheet("background: transparent; color: #888; font-size: 16px; font-weight: bold; border: none;")
        
        header.addWidget(title); header.addStretch(); header.addWidget(btn_close)
        layout.addLayout(header)
        
        # 2. AYARLAR
        # Mikrofon
        layout.addWidget(QLabel("SES KAYNAĞI"))
        self.combo_mic = QComboBox()
        self.combo_mic.addItems(["Sistem Sesi + Mikrofon (Varsayılan)", "Sadece Mikrofon", "Sessiz"])
        layout.addWidget(self.combo_mic)
        
        # Kamera
        layout.addWidget(QLabel("KAMERA"))
        self.combo_cam = QComboBox()
        # İki seçenek yerine daha mantıklı dummy seçenekler
        self.combo_cam.addItems(["Kamera Kapalı", "Entegre Webcam (Varsayılan)"])
        self.combo_cam.currentIndexChanged.connect(self.toggle_camera_preview)
        layout.addWidget(self.combo_cam)
        
        # Kayıt Yeri
        layout.addWidget(QLabel("KAYIT KLASÖRÜ"))
        path_layout = QHBoxLayout()
        self.lbl_path = QLabel("...")
        self.lbl_path.setStyleSheet("font-size: 12px; color: #888; background: #222; padding: 10px; border-radius: 8px; border: 1px solid #333;")
        btn_path = QPushButton("📂")
        btn_path.setObjectName("PathBtn")
        btn_path.setFixedSize(40, 40)
        btn_path.clicked.connect(self.change_path)
        path_layout.addWidget(self.lbl_path, 1)
        path_layout.addWidget(btn_path)
        layout.addLayout(path_layout)
        self.update_path_label()

        layout.addStretch()

        # 3. AKSİYON BUTONLARI
        # Kayıt Başlat Butonu (Kocaman)
        self.btn_start = QPushButton("KAYDI BAŞLAT")
        self.btn_start.setFixedHeight(60)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff3b30, stop:1 #ff2d55);
                color: white; font-size: 16px; font-weight: bold; border-radius: 30px; border: none;
            }
            QPushButton:hover { background: #ff453a; }
            QPushButton:pressed { background: #d22f2f; margin-top: 2px; }
        """)
        self.btn_start.clicked.connect(self.start_recording)
        layout.addWidget(self.btn_start)

    def update_path_label(self):
        path = self.settings.get("video_save_path")
        if path:
            short_path = f"...{path[-35:]}" if len(path) > 35 else path
            self.lbl_path.setText(short_path)
        else:
            self.lbl_path.setText("Seçilmedi")

    def change_path(self):
        d = QFileDialog.getExistingDirectory(self, "Kayıt Klasörü Seç", self.settings.get("video_save_path"))
        if d:
            self.settings.set("video_save_path", d)
            self.update_path_label()

    def toggle_camera_preview(self, index):
        if index == 0:
            self.camera_widget.hide()
            self.camera_widget.set_camera_active(False)
        else:
            self.camera_widget.show()
            self.camera_widget.set_camera_active(True)
            # Sağ alt köşe varsayılan konum
            screen = QApplication.primaryScreen().geometry()
            self.camera_widget.move(screen.width() - 340, screen.height() - 260)

    def generate_filename(self):
        import time
        folder = self.settings.get("video_save_path")
        name = f"Vizia_Kayit_{int(time.time())}.mp4"
        return os.path.join(folder, name)

    def start_recording(self):
        # Özel Onay Penceresi Kullan (Çökmeyi Önler)
        dlg = ModernConfirmDialog(self, "Kayıt Başlatılıyor", "Mikrofon ve ekran kaydı başlayacak.\nArayüz gizlenecek ve çizim modu aktifleşecek.")
        if dlg.exec_():
            self.is_recording = True
            filename = self.generate_filename()
            
            # 1. Pencereyi Gizle (Kullanıcı İsteği)
            self.hide()
            
            # 2. Overlay Kilidini Aç (Kullanıcı İsteği)
            if self.overlay: 
                self.overlay.set_input_locked(False)
                self.overlay.show_toast("🔴 Kayıt Başladı! (Simülasyon)")
            
            # 3. Motoru Başlat
            self.engine.start(filename, fps=60)
            
            # Not: Gerçek durdurma işlemi için tray icon veya toolbar butonu gerekir.
            # Şimdilik "Durdurmak için F10" gibi bir mantık kurabiliriz 
            # veya Toolbar'a bir "Stop" butonu ekleyebiliriz.

    def close_panel(self):
        if self.is_recording:
            self.engine.stop()
        
        self.camera_widget.close()
        # Paneli kapatınca kilidi açmayı unutma
        if self.overlay: self.overlay.set_input_locked(False)
        self.close()

    # Sürükleme Mantığı
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos') and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
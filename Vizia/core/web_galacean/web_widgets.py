# core/web_galacean/web_widgets.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizeGrip
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
except ImportError:
    raise ImportError("PyQtWebEngine is required. Install it with: pip install PyQtWebEngine")

from .web_engine import ViziaEngineAssets

class ViziaEngineItem(QWidget):
    request_close = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.SubWindow) 
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Ana Düzen
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- 1. BAŞLIK ÇUBUĞU ---
        self.control_frame = QFrame()
        self.control_frame.setFixedHeight(32)
        self.control_frame.setStyleSheet("""
            QFrame { 
                background-color: #1c1c1e; 
                border-top-left-radius: 10px; 
                border-top-right-radius: 10px; 
                border-bottom: 1px solid #3a3a3c;
            }
        """)
        
        self.control_layout = QHBoxLayout(self.control_frame)
        self.control_layout.setContentsMargins(15, 0, 10, 0)
        
        self.lbl_title = QLabel("VIZIA STUDIO PRO")
        self.lbl_title.setStyleSheet("color: #0a84ff; font-weight: 900; font-size: 11px; letter-spacing: 1px; border:none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton { background-color: #ff3b30; color: white; border-radius: 10px; font-weight: bold; border: none; font-size: 10px; }
            QPushButton:hover { background-color: #ff453a; }
        """)
        self.btn_close.clicked.connect(self.close)
        
        self.control_layout.addWidget(self.lbl_title)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.btn_close)
        
        self.layout.addWidget(self.control_frame)

        # --- 2. WEB TARAYICI VE AYARLAR ---
        self.browser = QWebEngineView()
        self.browser.setStyleSheet("background-color: #1c1c1e;")
        
        # !!! İŞTE SİHİRLİ KODLAR BURADA !!!
        settings = self.browser.settings()
        # 1. Yerel dosyaların diğer yerel dosyaları okumasına izin ver
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        # 2. Yerel dosyaların internete erişmesine izin ver (Gerekirse)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # 3. JavaScript'i aç
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        # 4. Yerel depolamayı aç
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        # 5. WebGL Hızlandırması
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        
        # HTML Dosyasını Yükle
        url = ViziaEngineAssets.get_engine_url()
        print(f"DEBUG: Vizia Engine Yükleniyor... URL: {url.toString()}")
        self.browser.setUrl(url)
        
        self.layout.addWidget(self.browser)

        # --- 3. PENCERE HAREKETİ ---
        self.grip = QSizeGrip(self)
        self.resize(1000, 600)
        self.is_moving = False
        self.drag_start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.control_frame.geometry().contains(event.pos()):
                self.is_moving = True
                self.drag_start_pos = event.pos()
            self.raise_() 
    
    def mouseMoveEvent(self, event):
        if self.is_moving:
            delta = event.pos() - self.drag_start_pos
            self.move(self.pos() + delta)
    
    def mouseReleaseEvent(self, event):
        self.is_moving = False

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.grip.width(), rect.bottom() - self.grip.height())
        super().resizeEvent(event)
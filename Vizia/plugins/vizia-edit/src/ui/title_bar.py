"""
Custom title bar widget (frameless window için)
"""
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QApplication)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
from .styles import get_title_bar_stylesheet


class TitleBar(QWidget):
    """Özel title bar widget'ı (Vizia branding ile)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.drag_position = QPoint()
        
        self.setObjectName("titleBar")
        self.setFixedHeight(40)
        self.setup_ui()
        self.setStyleSheet(get_title_bar_stylesheet())
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)
        
        # Logo / İkon (opsiyonel)
        # logo_label = QLabel()
        # logo_label.setPixmap(QPixmap("icon.png").scaled(24, 24, Qt.KeepAspectRatio))
        # layout.addWidget(logo_label)
        
        # Başlık
        self.title_label = QLabel("Vizia Edit - Video Düzenleyici")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Window control butonları
        # Minimize
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("windowButton")
        self.minimize_btn.clicked.connect(self.minimize_window)
        self.minimize_btn.setToolTip("Küçült")
        layout.addWidget(self.minimize_btn)
        
        # Maximize/Restore
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("windowButton")
        self.maximize_btn.clicked.connect(self.maximize_restore_window)
        self.maximize_btn.setToolTip("Ekranı Kapla")
        layout.addWidget(self.maximize_btn)
        
        # Close
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.close_window)
        self.close_btn.setToolTip("Kapat")
        layout.addWidget(self.close_btn)
    
    def set_title(self, title: str):
        """Başlığı ayarlar"""
        self.title_label.setText(title)
    
    def minimize_window(self):
        """Pencereyi küçültür"""
        if self.parent_window:
            self.parent_window.showMinimized()
    
    def maximize_restore_window(self):
        """Pencereyi maksimize eder veya restore eder"""
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
                self.maximize_btn.setText("□")
            else:
                self.parent_window.showMaximized()
                self.maximize_btn.setText("❐")
    
    def close_window(self):
        """Pencereyi kapatır"""
        if self.parent_window:
            self.parent_window.close()
    
    def mousePressEvent(self, event):
        """Mouse basma eventi"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Mouse hareket eventi (sürükleme)"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            if self.parent_window.isMaximized():
                # Maximize durumdan çık
                self.parent_window.showNormal()
                self.maximize_btn.setText("□")
                # Mouse pozisyonunu ayarla
                self.drag_position = QPoint(self.parent_window.width() // 2, 20)
            
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Mouse bırakma eventi"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """Çift tıklama eventi (maximize/restore)"""
        if event.button() == Qt.LeftButton:
            self.maximize_restore_window()
            event.accept()

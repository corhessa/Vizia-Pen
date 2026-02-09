# Vizia/core/recorder/camera_widget.py

from PyQt5.QtWidgets import QWidget, QLabel, QSizeGrip, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ResizableCameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 6. İSTEK: Webcam her daim çizgilerin üzerinde dursun (Z-Order)
        # Tool ve StaysOnTopHint kombinasyonu en üstte tutar
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setMinimumSize(160, 120)
        self.resize(320, 240)
        
        # Kamera Görüntüsü İçin Alan
        # Not: Gerçek görüntü Engine tarafından videoya basılıyor, burası sadece "yer tutucu" ve "vizör"
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Vizia Cam\n(Çerçeve)")
        self.video_label.setStyleSheet("""
            QLabel { 
                color: #007aff; 
                background-color: rgba(0, 0, 0, 200); 
                border-radius: 10px; 
                border: 2px solid #007aff; 
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_label)
        
        self.old_pos = None
        
        # Sağ alt köşe boyutlandırma
        self.grip = QSizeGrip(self)
        self.grip.setStyleSheet("background-color: transparent;")
        self.grip.resize(20, 20)

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - 20, rect.bottom() - 20)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.raise_() # Tıklayınca en üste al

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    # Çizim yapılırken arkada kalmaması için zorla öne getir
    def paintEvent(self, event):
        self.raise_()
        super().paintEvent(event)
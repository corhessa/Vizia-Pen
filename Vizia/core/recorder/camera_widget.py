# Vizia/core/recorder/camera_widget.py

from PyQt5.QtWidgets import QWidget, QLabel, QSizeGrip, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor, QPainter, QPen

class ResizableCameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Çerçevesiz, her zaman üstte ve şeffaf arkaplan
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setMinimumSize(160, 120)
        self.resize(320, 240)
        
        # Kamera Görüntüsü İçin Alan (Siyah Ekran)
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Kamera Bekleniyor...")
        self.video_label.setStyleSheet("""
            QLabel { 
                color: #666; 
                background-color: #101010; 
                border-radius: 10px; 
                border: 2px solid #333; 
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_label)
        
        # Sürükleme için değişkenler
        self.old_pos = None
        
        # Sağ alt köşe boyutlandırma tutamacı
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

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def set_camera_active(self, active):
        if active:
            self.video_label.setText("Vizia C++ Engine\n[Kamera Yayını]")
            self.video_label.setStyleSheet("""
                QLabel { 
                    color: #007aff; 
                    background-color: #000; 
                    border-radius: 10px; 
                    border: 2px solid #007aff; 
                }
            """)
        else:
            self.video_label.setText("Kamera Kapalı")
            self.video_label.setStyleSheet("""
                QLabel { 
                    color: #666; 
                    background-color: #101010; 
                    border-radius: 10px; 
                    border: 2px solid #333; 
                }
            """)
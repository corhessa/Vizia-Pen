# Vizia/plugins/vizia-recorder/camera_widget.py

from PyQt5.QtWidgets import QWidget, QSizeGrip
# [FIX] QRectF eklendi (Float Rectangle)
from PyQt5.QtCore import Qt, QRect, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor, QPen, QPainterPath

class ResizableCameraWidget(QWidget):
    geometry_changed = pyqtSignal(QRect)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setMinimumSize(160, 120)
        self.resize(320, 240)
        
        self.current_pixmap = None
        self.old_pos = None
        
        self.grip = QSizeGrip(self)
        self.grip.setStyleSheet("background-color: transparent;")
        self.grip.resize(20, 20)
        
        self.placeholder_color = QColor(20, 20, 20, 240)
        self.border_color = QColor(0, 122, 255) 

    def update_frame(self, qt_img):
        if qt_img is None: return
        try:
            self.current_pixmap = QPixmap.fromImage(qt_img)
            self.update() 
        except Exception as e:
            print(f"Paint Error: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        
        # [FIX] QRect -> QRectF olarak değiştirildi.
        # PyQt5 path çizimlerinde float koordinat ister.
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 15, 15)
        
        painter.setClipPath(path)
        
        painter.fillPath(path, self.placeholder_color)
        
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled = self.current_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            
        painter.setClipping(False)
        pen = QPen(self.border_color, 4) 
        painter.strokePath(path, pen)
        
        self.raise_()

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - 20, rect.bottom() - 20)
        self.geometry_changed.emit(self.geometry())
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.raise_()
            self.activateWindow()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            self.geometry_changed.emit(self.geometry())

    def mouseReleaseEvent(self, event):
        self.geometry_changed.emit(self.geometry())
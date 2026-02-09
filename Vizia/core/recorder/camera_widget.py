# Vizia/core/recorder/camera_widget.py

from PyQt5.QtWidgets import QWidget, QSizeGrip
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor, QPen

class ResizableCameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Madde 1: Her zaman en üstte, kalem çiziminin altında kalmaz
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setMinimumSize(160, 120)
        self.resize(320, 240)
        
        self.current_pixmap = None
        self.old_pos = None
        
        # Sağ alt köşe boyutlandırma tutamacı
        self.grip = QSizeGrip(self)
        self.grip.setStyleSheet("background-color: transparent;")
        self.grip.resize(20, 20)
        
        # Bekleme Ekranı İçin Stil
        self.placeholder_color = QColor(20, 20, 20, 240)
        self.border_color = QColor(0, 122, 255) # Vizia Mavisi

    def update_frame(self, cv_img):
        """Madde 2: Gelen kareyi arayüzde göster"""
        if cv_img is None: return
        try:
            h, w, ch = cv_img.shape
            bytes_per_line = ch * w
            # OpenCV (NumPy) -> Qt Image dönüşümü
            qt_img = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.current_pixmap = QPixmap.fromImage(qt_img)
            self.update() # paintEvent'i tetikle
        except Exception:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arkaplan
        painter.setBrush(self.placeholder_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        # Madde 3: Görüntü Çerçeveye Tam Otursun (Kayma Olmasın)
        if self.current_pixmap and not self.current_pixmap.isNull():
            # En boy oranını koruyarak widget'ı DOLDURACAK şekilde ölçekle (Crop mantığı)
            scaled = self.current_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            # Görüntüyü merkeze hizala
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            
            # Köşeleri yuvarlatmak için Clip Path kullan
            path = self.rect()
            painter.setClipRect(self.rect()) # Basit clip, yuvarlak için QPainterPath gerekebilir ama performans için Rect yeterli
            painter.drawPixmap(x, y, scaled)
            
        # Çerçeve (Border)
        painter.setClipping(False)
        pen = QPen(self.border_color, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 15, 15)
        
        # Madde 1: Çizim yaparken arkada kalmaması için zorla öne getir
        self.raise_()

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - 20, rect.bottom() - 20)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.raise_() # Tıklayınca öne al

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
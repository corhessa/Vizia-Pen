from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QApplication
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup

class ModernNotification(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel(message)
        self.label.setStyleSheet("background-color: rgba(20, 20, 20, 245); color: #ffffff; border: 2px solid #007aff; border-radius: 20px; padding: 12px 35px; font-size: 15px; font-weight: 700;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.adjustSize()
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
        # Ekranın ortasına konumlandırma (Güvenli kontrol)
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.geometry()
            self.target_y = int(screen_geo.height() * 0.12)
            self.target_x = (screen_geo.width() - self.width()) // 2
            self.move(self.target_x, self.target_y)
        else:
            self.target_y = 100
            self.target_x = 100
            
    def show_animated(self):
        self.show(); self.raise_()
        self.anim_group = QParallelAnimationGroup()
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_in.setDuration(400); fade_in.setStartValue(0.0); fade_in.setEndValue(1.0)
        slide_in = QPropertyAnimation(self, b"pos")
        slide_in.setDuration(500); slide_in.setStartValue(QPoint(self.target_x, self.target_y + 30)); slide_in.setEndValue(QPoint(self.target_x, self.target_y)); slide_in.setEasingCurve(QEasingCurve.OutExpo)
        self.anim_group.addAnimation(fade_in); self.anim_group.addAnimation(slide_in)
        self.anim_group.start(); QTimer.singleShot(2500, self._start_fade_out)
        
    def _start_fade_out(self):
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(600); self.fade_out.setStartValue(1.0); self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.close); self.fade_out.start()
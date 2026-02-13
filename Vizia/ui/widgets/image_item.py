from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSizeGrip, QFrame, QSizePolicy, QMenu)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect

class ViziaImageItem(QWidget):
    request_close = pyqtSignal(QWidget)
    request_stamp = pyqtSignal()
    
    def __init__(self, image_path, creation_mode, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.creation_mode = creation_mode
        self.setWindowFlags(Qt.SubWindow)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_Hover)
        self.setStyleSheet("background: transparent;")
        
        self.setCursor(Qt.ArrowCursor)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.control_frame = QFrame()
        self.control_frame.setFixedHeight(32)
        self.control_frame.setStyleSheet("""
            QFrame { background-color: #1c1c1e; border-top-left-radius: 10px; border-top-right-radius: 10px; border: 1px solid #3a3a3c; }
        """)
        self.control_layout = QHBoxLayout(self.control_frame)
        self.control_layout.setContentsMargins(5, 0, 5, 0)
        self.control_layout.setSpacing(5)
        
        def create_btn(text, tip, func, bg="#2c2c2e"):
            btn = QPushButton(text)
            btn.setFixedSize(24, 24)
            btn.setToolTip(tip)
            btn.clicked.connect(func)
            btn.setStyleSheet(f"QPushButton {{ background:{bg}; color:white; border-radius:4px; font-weight:bold; }} QPushButton:hover {{ background:#3a3a40; }}")
            return btn

        self.control_layout.addWidget(create_btn("📌", "Sabitle", self.request_stamp.emit, "#007aff"))
        self.control_layout.addStretch()
        self.control_layout.addWidget(create_btn("✕", "Kapat", self.close, "#ff3b30"))
        
        self.layout.addWidget(self.control_frame)
        self.control_frame.hide()
        
        self.image_container = QLabel()
        self.original_pixmap = QPixmap(image_path)
        self.image_container.setPixmap(self.original_pixmap)
        self.image_container.setScaledContents(True)
        self.image_container.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        self.layout.addWidget(self.image_container)
        
        self.grip = QSizeGrip(self)
        self.grip.setCursor(Qt.SizeFDiagCursor)
        self.grip.setStyleSheet("""
            background-color: rgba(255, 255, 255, 180); 
            border-top-left-radius: 8px;
            border-bottom-right-radius: 8px;
            width: 16px;
            height: 16px;
        """)
        self.grip.hide() 
        
        self.old_pos = None
        self.is_resizing = False
        self.is_moving = False
        self.drag_start_pos = QPoint()
        self.resize_start_geo = QRect()
        
        w, h = self.original_pixmap.width(), self.original_pixmap.height()
        if w > 400: h = int(h * (400/w)); w = 400
        self.resize(w, h + 32)
        self.show()

    def contextMenuEvent(self, event):
        # KRİTİK DÜZELTME: Parent kaldırıldı (bağımsız pencere), her zaman en üstte kalması sağlandı
        menu = QMenu()
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowStaysOnTopHint | Qt.Popup) 
        menu.setStyleSheet("""
            QMenu { background-color: #2c2c2e; color: white; border: 1px solid #48484a; border-radius: 8px; padding: 5px; font-family: 'Segoe UI'; font-size: 13px; }
            QMenu::item { padding: 6px 25px; border-radius: 4px; }
            QMenu::item:selected { background-color: #007aff; }
            QMenu::separator { height: 1px; background-color: #48484a; margin: 4px 10px; }
        """)
        a_front = menu.addAction("Öne Getir")
        a_back = menu.addAction("Geriye Gönder")
        menu.addSeparator()
        a_dup = menu.addAction("Çoğalt")
        a_del = menu.addAction("Sil")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == a_front: self.raise_()
        elif action == a_back: self.lower()
        elif action == a_del: self.close()
        elif action == a_dup:
            parent_overlay = self.parentWidget()
            if parent_overlay:
                new_img = ViziaImageItem(self.image_path, self.creation_mode, parent_overlay)
                new_img.resize(self.size())
                new_img.move(self.x() + 20, self.y() + 20)
                new_img.request_close.connect(lambda w: [parent_overlay.active_layer.remove_widget_item(w), w.deleteLater()])
                new_img.request_stamp.connect(lambda: parent_overlay.stamp_image(new_img))
                parent_overlay.active_layer.add_widget_item(new_img, 'image')

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.grip.width(), rect.bottom() - self.grip.height())
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        event.accept()
        if event.button() == Qt.LeftButton:
            if self.grip.isVisible() and self.grip.geometry().contains(event.pos()):
                self.is_resizing = True
                self.drag_start_pos = event.globalPos()
                self.resize_start_geo = self.geometry()
            else:
                self.is_moving = True
                self.drag_start_pos = event.pos()
                self.raise_()
                self.setCursor(Qt.SizeAllCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        event.accept()
        if self.is_resizing:
            delta = event.globalPos() - self.drag_start_pos
            new_w = max(50, self.resize_start_geo.width() + delta.x())
            new_h = max(50, self.resize_start_geo.height() + delta.y())
            self.resize(new_w, new_h)
        elif self.is_moving:
            delta = event.pos() - self.drag_start_pos
            self.move(self.pos() + delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        self.is_moving = False
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
        
    def enterEvent(self, event):
        self.control_frame.show()
        self.grip.show() 
        self.image_container.setStyleSheet("border: 1px solid #007aff;")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.control_frame.hide()
        self.grip.hide()
        self.image_container.setStyleSheet("border: none;")
        self.unsetCursor()
        super().leaveEvent(event)

    def closeEvent(self, event):
        self.request_close.emit(self)
        super().closeEvent(event)
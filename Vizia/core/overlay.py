import sys
import os

def resource_path(relative_path):
    """ Dosya yollarını EXE uyumlu hale getirir """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QVBoxLayout, 
                             QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QPainter, QPixmap, QPainterPath, QColor, QPen)
from PyQt5.QtCore import (Qt, QPoint, QTimer, QStandardPaths)

from ui.ui_components import ModernNotification
from ui.text_widgets import ViziaTextItem 

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 520)
        self.old_pos = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) 

        # --- BEYAZ KART (Ana Taşıyıcı) ---
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 20px;
                border: 1px solid #f0f0f0;
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI', sans-serif;
                border: none;
            }
        """)
        
        # Kartın Gölgesi
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)

        # İçerik Düzeni
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(30, 45, 30, 45)
        content_layout.setSpacing(15)

        # 1. LOGO ALANI
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = resource_path("Vizia/Assets/VIZIA.png") 
        if not os.path.exists(logo_path):
            logo_path = os.path.join(base_path, "Assets", "VIZIA.ico")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Logoyu biraz büyüttük ve netleştirdik
            scaled_pixmap = pixmap.scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("V")
            logo_label.setStyleSheet("font-size: 80px; font-weight: bold; color: #000;")
        content_layout.addWidget(logo_label, 0, Qt.AlignHCenter)

        # 2. BAŞLIK
        title = QLabel("VIZIA PEN")
        title.setStyleSheet("font-size: 28px; font-weight: 900; letter-spacing: 0.5px; color: #111;")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)
        
        content_layout.addStretch()

        # 3. AÇIKLAMA METNİ
        aciklama_metni = """
        <p style='line-height: 160%; font-size: 14px; color: #444;'>
        Vizia Pen, ekran üzerinde <b>özgürce</b> çizim yapmanızı ve <b>fikirlerinizi</b> 
        anında görselleştirmenizi sağlayan <b>profesyonel</b> bir araçtır.
        </p>
        <br>
        <p style='color: #999; font-size: 12px;'>
        Geliştirici: <b>Corhessa</b> &nbsp;|&nbsp; v1.0
        </p>
        """
        info_label = QLabel(aciklama_metni)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setTextFormat(Qt.RichText)
        content_layout.addWidget(info_label)

        content_layout.addSpacing(25)

        # 4. YENİLENMİŞ PREMİUM 'KAPAT' BUTONU
        btn_ok = QPushButton("Kapat")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFixedSize(160, 44) 
        
        # Tasarım: Hafif Gradient + Modern Font + Tam Yuvarlak Köşeler
        btn_ok.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007aff, stop:1 #005bb5);
                color: #ffffff;
                border: none;
                border-radius: 22px;
                font-family: 'Segoe UI';
                font-weight: 700;
                font-size: 14px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0088ff, stop:1 #0066cc);
            }
            QPushButton:pressed {
                background-color: #004494;
                padding-top: 2px; /* Basma hissi */
            }
        """)
        
        
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(15)
        btn_shadow.setColor(QColor(0, 122, 255, 80)) # Mavi gölge
        btn_shadow.setOffset(0, 5)
        btn_ok.setGraphicsEffect(btn_shadow)
        
        content_layout.addWidget(btn_ok, 0, Qt.AlignHCenter)

    # Pencere Sürükleme
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    def mouseReleaseEvent(self, event): self.old_pos = None


class DrawingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.canvas = QPixmap(QApplication.primaryScreen().size())
        self.canvas.fill(Qt.transparent)
        self.drawing_mode = "pen"
        self.whiteboard_mode = False
        self.desktop_history, self.board_history = [], []
        self.current_stroke_path = QPainterPath()
        self.last_point = QPoint()
        self.current_color = QColor(255, 45, 85)
        self.brush_size = 4
        self.drawing = False
        self.toolbar = None
        self.toast = None
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace: self.undo()
        elif event.key() == Qt.Key_Q: QApplication.quit()
        elif event.key() == Qt.Key_S: self.take_screenshot()
        elif event.key() == Qt.Key_D: self.clear_all()
        elif event.key() == Qt.Key_V:
            if self.toolbar: self.toolbar.toggle_move_mode()
        elif event.key() == Qt.Key_C:
            if self.toolbar: self.toolbar.select_color()
        elif event.key() == Qt.Key_Space:
            if self.toolbar: self.toolbar.toggle_board()

    def force_focus(self):
        self.activateWindow(); self.raise_(); self.setFocus()

    def redraw_canvas(self):
        self.canvas.fill(Qt.transparent)
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        
        active_hist = self.board_history if self.whiteboard_mode else self.desktop_history
        
        for item in active_hist:
            if isinstance(item, dict) and item.get('type') == 'path':
                if item['mode'] == 'eraser' and not self.whiteboard_mode:
                    painter.setCompositionMode(QPainter.CompositionMode_Clear)
                    pen_color = Qt.transparent
                else:
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    pen_color = Qt.white if item['mode'] == 'eraser' else item['color']
                painter.setPen(QPen(pen_color, item['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(item['path'])
        painter.end()
        
        all_items = self.board_history + self.desktop_history
        for item in all_items:
            if isinstance(item, dict) and item.get('type') == 'text':
                try:
                    widget = item['obj']
                    should_be_visible = (widget.creation_mode == self.whiteboard_mode)
                    widget.setVisible(should_be_visible)
                except RuntimeError:
                    pass 
                    
        self.update()

    def undo(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        if target:
            last = target.pop()
            if isinstance(last, dict) and last.get('type') == 'text': last['obj'].close()
            self.redraw_canvas()

    def clear_all(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in target[:]:
            if isinstance(item, dict) and item.get('type') == 'text': item['obj'].close()
        target.clear(); self.canvas.fill(Qt.transparent); self.update()
        self.redraw_canvas() 

    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        QTimer.singleShot(400, self._perform_capture)

    def _perform_capture(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pics = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        path = os.path.join(pics, f"Vizia_{timestamp}.png")
        if screenshot.save(path): self.show_toast("Başarıyla Kaydedildi !")
        if self.toolbar: self.toolbar.show()
        self.force_focus()

    def show_toast(self, message):
        self.toast = ModernNotification(message, self)
        self.toast.show_animated()

    def remove_text_item(self, text_item):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        for i in range(len(target) - 1, -1, -1):
            item = target[i]
            if isinstance(item, dict) and item.get('obj') == text_item:
                target.pop(i)
                break
        text_item.deleteLater()
        self.update()

    def add_text(self):
        txt = ViziaTextItem(self, self.whiteboard_mode, self.current_color)
        start_x, start_y = 100, 100
        if self.toolbar:
            target_x = self.toolbar.x() + self.toolbar.width() + 20
            target_y = self.toolbar.y()
            screen_width = QApplication.primaryScreen().size().width()
            if target_x + 200 > screen_width: target_x = self.toolbar.x() - 220
            start_x, start_y = target_x, target_y
        txt.move(start_x, start_y)
        txt.delete_requested.connect(self.remove_text_item)
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        target.append({'type': 'text', 'obj': txt})

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.whiteboard_mode: painter.fillRect(self.rect(), Qt.white)
        else: painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        painter.drawPixmap(0, 0, self.canvas)

    def mousePressEvent(self, event):
        if self.drawing_mode != "move": self.force_focus()
        if self.drawing_mode in ["pen", "eraser"] and event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.current_stroke_path = QPainterPath()
            self.current_stroke_path.moveTo(self.last_point)

    def mouseMoveEvent(self, event):
        if not self.drawing: return
        current_pos = event.pos()
        mid_point = (self.last_point + current_pos) / 2
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.drawing_mode == 'eraser' and not self.whiteboard_mode:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            pen_color = Qt.transparent
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen_color = Qt.white if self.drawing_mode == 'eraser' else self.current_color
        painter.setPen(QPen(pen_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path_segment = QPainterPath()
        path_segment.moveTo(self.last_point)
        path_segment.quadTo(self.last_point, mid_point)
        path_segment.lineTo(current_pos)
        painter.drawPath(path_segment); painter.end()
        self.current_stroke_path.quadTo(self.last_point, mid_point)
        self.current_stroke_path.lineTo(current_pos)
        self.last_point = current_pos; self.update()

    def mouseReleaseEvent(self, event):
        if self.drawing:
            item = {'type': 'path', 'path': QPainterPath(self.current_stroke_path), 
                    'color': QColor(self.current_color), 'width': self.brush_size, 'mode': self.drawing_mode}
            target = self.board_history if self.whiteboard_mode else self.desktop_history
            target.append(item)
        self.drawing = False; self.update()
import os
import datetime
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath, QColor, QFont, QCursor, QPen
from PyQt5.QtCore import Qt, QPoint, QTimer, QStandardPaths

from ui_components import ModernNotification, ModernColorPicker
from text_widgets import ViziaTextItem 

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vizia - Hakkında")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog { background-color: #1c1c1e; border: 2px solid #3a3a3c; border-radius: 20px; }
            QLabel { color: white; font-family: 'Segoe UI'; }
        """)
        
        layout = QVBoxLayout(self)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: #ff3b30; color: white; border-radius: 15px; font-weight: bold;")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, 0, Qt.AlignRight)

        title = QLabel("VIZIA PROJECT")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.image_label = QLabel("Görsel Buraya Gelecek")
        self.image_label.setFixedSize(300, 150)
        self.image_label.setStyleSheet("background: #2c2c2e; border-radius: 10px; color: #555;")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label, 0, Qt.AlignCenter)

        vision_text = QLabel("Vizyonun ve projenin detaylarını\nburada anlatabilirsin.")
        vision_text.setWordWrap(True)
        vision_text.setAlignment(Qt.AlignCenter)
        vision_text.setStyleSheet("color: #ebebeb; font-size: 14px; margin: 20px;")
        layout.addWidget(vision_text)
        layout.addStretch()

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

    def undo(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        if target:
            last = target.pop()
            if isinstance(last, dict) and last.get('type') == 'text': last['obj'].close()
            self.redraw_canvas(); self.update()

    def clear_all(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in target[:]:
            if isinstance(item, dict) and item.get('type') == 'text': item['obj'].close()
        target.clear(); self.canvas.fill(Qt.transparent); self.update()

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

    # --- YENİ EKLENEN FONKSİYON: GÜVENLİ SİLME ---
    def remove_text_item(self, text_item):
        """Metin kutusunu güvenli bir şekilde geçmişten siler."""
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        
        # Listeyi tersten tarayıp bu objeyi bul ve listeden çıkar
        # (Tersten taramak silme işlemlerinde daha güvenlidir)
        for i in range(len(target) - 1, -1, -1):
            item = target[i]
            if isinstance(item, dict) and item.get('obj') == text_item:
                target.pop(i)
                break
        
        # Listeden çıktıktan sonra widget'ı güvenle yok et
        text_item.deleteLater()
        self.update()

    def add_text(self):
        txt = ViziaTextItem(self, self.whiteboard_mode, self.current_color)
        
        # --- KONUM HESAPLAMA (Toolbar'ın yanına) ---
        start_x, start_y = 100, 100 # Varsayılan (Toolbar yoksa)
        
        if self.toolbar:
            # Toolbar'ın sağına koymaya çalış (Toolbar X + Genişlik + 20px boşluk)
            target_x = self.toolbar.x() + self.toolbar.width() + 20
            target_y = self.toolbar.y()
            
            # Eğer sağ tarafta ekran bittiyse, soluna koy
            screen_width = QApplication.primaryScreen().size().width()
            if target_x + 200 > screen_width:
                target_x = self.toolbar.x() - 220
                
            start_x, start_y = target_x, target_y

        txt.move(start_x, start_y)
        
        # Güvenli silme sinyalini bağla (CRASH FIX)
        txt.delete_requested.connect(self.remove_text_item)
        
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        target.append({'type': 'text', 'obj': txt})

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.whiteboard_mode: painter.fillRect(self.rect(), Qt.white)
        else: painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        painter.drawPixmap(0, 0, self.canvas)
        for item in self.board_history + self.desktop_history:
            if isinstance(item, dict) and item.get('type') == 'text':
                # Sadece objesi hala yaşayanları çiz (Ekstra güvenlik)
                try:
                    if item['obj'].isVisible():
                        is_visible = item['obj'].creation_mode == self.whiteboard_mode
                        item['obj'].setVisible(is_visible)
                except RuntimeError:
                    # Obje silinmişse pas geç
                    continue

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
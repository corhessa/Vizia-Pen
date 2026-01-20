import os
import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QSlider, QLabel, QFrame, QApplication, QDialog, QHBoxLayout)
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPixmap, QPainterPath, QFont
from PyQt5.QtCore import Qt, QPoint, QTimer, QStandardPaths
from ui_components import ModernNotification, ModernColorPicker
from text_widgets import StandaloneText

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
        
        # Kapatma butonu
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: #ff3b30; color: white; border-radius: 15px; font-weight: bold;")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, 0, Qt.AlignRight)

        # Başlık ve Görsel Alanı
        title = QLabel("VIZIA PROJECT")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # İlerde görsel ekleyeceğin alan
        self.image_label = QLabel("Görsel Buraya Gelecek")
        self.image_label.setFixedSize(300, 150)
        self.image_label.setStyleSheet("background: #2c2c2e; border-radius: 10px; color: #555;")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label, 0, Qt.AlignCenter)

        # Vizyon Metni
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

    def add_text(self):
        txt = StandaloneText(self, self.whiteboard_mode, self.current_color)
        pos = QCursor.pos(); txt.move(pos.x() - 150, pos.y() - 50)
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        target.append({'type': 'text', 'obj': txt})

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.whiteboard_mode: painter.fillRect(self.rect(), Qt.white)
        else: painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        painter.drawPixmap(0, 0, self.canvas)
        for item in self.board_history + self.desktop_history:
            if isinstance(item, dict) and item.get('type') == 'text':
                is_visible = item['obj'].creation_mode == self.whiteboard_mode
                item['obj'].setVisible(is_visible)

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

class ModernToolbar(QWidget):
    def __init__(self, overlay):
        super().__init__(overlay)
        self.overlay = overlay; self.old_pos = None
        self.custom_colors = ["#2c2c2e"] * 10 
        self.custom_color_index = 0
        self.last_active_tool = "pen"
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedWidth(75); self.setFixedHeight(620) # Boyutu yeni butonlar için artırdım
        self.setStyleSheet("""
            QWidget { background-color: #1c1c1e; border-radius: 20px; border: 1.5px solid #3a3a3c; }
            QPushButton { background-color: #2c2c2e; color: white; border: none; border-radius: 10px; font-size: 18px; min-width: 38px; min-height: 38px; }
            QPushButton:hover { background-color: #3a3a40; border: 1px solid #007aff; }
            QLabel { color: white; background: transparent; border: none; font-size: 10px; font-weight: 800; }
            QSlider::groove:horizontal { border: none; height: 4px; background: #2c2c2e; border-radius: 2px; }
            QSlider::handle:horizontal { background: #007aff; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
        """)
        layout = QVBoxLayout(self); layout.setContentsMargins(10, 12, 10, 10); layout.setSpacing(5) 

        # Logo Alanı
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, "Assets", "VIZIA.ico")
        logo_label = QLabel()
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("VIZIA")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("margin-top: 5px; margin-bottom: 10px;") # Aralığı açtım
        layout.addWidget(logo_label)

        # Butonlar
        self.btn_draw = self.create_btn("🖋", lambda: self.safe_change("pen", self.btn_draw))
        layout.addWidget(self.btn_draw, 0, Qt.AlignCenter)
        self.btn_eraser = self.create_btn("🧼", lambda: self.safe_change("eraser", self.btn_eraser))
        layout.addWidget(self.btn_eraser, 0, Qt.AlignCenter)
        layout.addWidget(self.create_btn("T", self.overlay.add_text), 0, Qt.AlignCenter)
        self.btn_board = self.create_btn("📋", self.toggle_board)
        self.btn_board.setStyleSheet("background-color: #ff3b30;"); layout.addWidget(self.btn_board, 0, Qt.AlignCenter)
        self.btn_move = self.create_btn("🖱", lambda: self.safe_change("move", self.btn_move))
        layout.addWidget(self.btn_move, 0, Qt.AlignCenter)
        
        line = QFrame(); line.setFixedHeight(1); line.setStyleSheet("background-color: #3a3a3c; margin: 4px 0;"); layout.addWidget(line)
        
        layout.addWidget(self.create_btn("↺", self.overlay.undo), 0, Qt.AlignCenter)
        btn_clear = self.create_btn("🗑️", self.overlay.clear_all); btn_clear.setStyleSheet("font-size: 20px;"); layout.addWidget(btn_clear, 0, Qt.AlignCenter)
        self.btn_shot = self.create_btn("📸", self.overlay.take_screenshot)
        self.btn_shot.setStyleSheet("background-color: #5856d6;"); layout.addWidget(self.btn_shot, 0, Qt.AlignCenter)
        self.btn_color = self.create_btn("⬤", self.select_color)
        self.btn_color.setStyleSheet(f"color: {self.overlay.current_color.name()}; font-size: 20px;"); layout.addWidget(self.btn_color, 0, Qt.AlignCenter)
        
        # Boyut Slider Alanı
        lbl_size = QLabel("BOYUT"); lbl_size.setAlignment(Qt.AlignCenter); lbl_size.setStyleSheet("font-size: 9px; font-weight: 900; margin-top: 5px;"); layout.addWidget(lbl_size)
        slider = QSlider(Qt.Horizontal); slider.setRange(2, 100); slider.setValue(4); slider.setFixedWidth(52)
        slider.valueChanged.connect(self.update_brush_size); layout.addWidget(slider, 0, Qt.AlignCenter)
        self.lbl_percent = QLabel("4%"); self.lbl_percent.setAlignment(Qt.AlignCenter); self.lbl_percent.setStyleSheet("font-size: 11px; color: #007aff; font-weight: 900;"); layout.addWidget(self.lbl_percent)
        
        layout.addStretch() # Üst kısmı yukarı itmek için boşluk

        # Alt Bölüm: Ayarlar, Hakkında ve Kapat
        layout.addWidget(self.create_btn("⚙️", lambda: print("Ayarlar tıklandı")), 0, Qt.AlignCenter)
        layout.addWidget(self.create_btn("ℹ️", self.show_about), 0, Qt.AlignCenter)
        
        btn_close = self.create_btn("✕", QApplication.quit)
        btn_close.setStyleSheet("background-color: #ff3b30; color: white;")
        layout.addWidget(btn_close, 0, Qt.AlignCenter)
        
        self.safe_change("pen", self.btn_draw)

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def select_color(self):
        picker = ModernColorPicker(self.overlay.current_color, self.custom_colors, self.overlay)
        if picker.exec_():
            color = picker.selected_color; self.overlay.current_color = color
            self.btn_color.setStyleSheet(f"color: {color.name()}; font-size: 20px;")
        QTimer.singleShot(10, self.overlay.force_focus)

    def update_brush_size(self, val): self.overlay.brush_size = val; self.lbl_percent.setText(f"{val}%")
    def create_btn(self, text, slot): btn = QPushButton(text); btn.clicked.connect(slot); btn.setFocusPolicy(Qt.NoFocus); return btn
    def toggle_board(self):
        self.overlay.whiteboard_mode = not self.overlay.whiteboard_mode
        self.btn_board.setStyleSheet("background-color: #4cd964;" if self.overlay.whiteboard_mode else "background-color: #ff3b30;")
        self.overlay.redraw_canvas(); self.overlay.update(); QTimer.singleShot(10, self.overlay.force_focus)
    
    def toggle_move_mode(self):
        if self.overlay.drawing_mode != "move":
            self.last_active_tool = self.overlay.drawing_mode
            self.safe_change("move", self.btn_move)
        else:
            target_btn = self.btn_draw if self.last_active_tool == "pen" else self.btn_eraser
            self.safe_change(self.last_active_tool, target_btn)

    def safe_change(self, mode, button):
        self.overlay.drawing_mode = mode
        for b in [self.btn_draw, self.btn_move, self.btn_eraser]: b.setStyleSheet("background-color: #2c2c2e;")
        button.setStyleSheet("background-color: #007aff; border: 1px solid white;")
        self.overlay.setWindowFlag(Qt.WindowTransparentForInput, mode == "move")
        self.overlay.show(); QTimer.singleShot(10, self.overlay.force_focus)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPos()
import sys
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QSlider, 
                             QLabel, QFrame, QTextEdit, QSizeGrip, QDialog, 
                             QGridLayout, QFileDialog, QGraphicsOpacityEffect)
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QFont, QLinearGradient, QBrush, QPixmap, QPainterPath
from PyQt5.QtCore import Qt, QPoint, QObject, QEvent, QTimer, QPropertyAnimation, QEasingCurve, QRect, QStandardPaths, QParallelAnimationGroup, pyqtSignal

# --- MODERN BİLDİRİM (TOAST ANIMATION) ---
class ModernNotification(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.label = QLabel(message)
        self.label.setStyleSheet("""
            background-color: rgba(20, 20, 20, 245);
            color: #ffffff;
            border: 2px solid #007aff;
            border-radius: 20px;
            padding: 12px 35px;
            font-size: 15px;
            font-weight: 700;
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.adjustSize()
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
        screen_geo = QApplication.primaryScreen().geometry()
        self.target_y = int(screen_geo.height() * 0.12)
        self.target_x = (screen_geo.width() - self.width()) // 2
        self.move(self.target_x, self.target_y)

    def show_animated(self):
        self.show()
        self.raise_()
        
        self.anim_group = QParallelAnimationGroup()
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_in.setDuration(400); fade_in.setStartValue(0.0); fade_in.setEndValue(1.0)
        
        slide_in = QPropertyAnimation(self, b"pos")
        slide_in.setDuration(500); slide_in.setStartValue(QPoint(self.target_x, self.target_y + 30))
        slide_in.setEndValue(QPoint(self.target_x, self.target_y))
        slide_in.setEasingCurve(QEasingCurve.OutExpo)
        
        self.anim_group.addAnimation(fade_in); self.anim_group.addAnimation(slide_in)
        self.anim_group.start()
        QTimer.singleShot(2500, self._start_fade_out)

    def _start_fade_out(self):
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(600); self.fade_out.setStartValue(1.0); self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.close); self.fade_out.start()

# --- MODERN RENK SEÇİCİ ---
class ModernColorPicker(QDialog):
    def __init__(self, initial_color, persistent_colors, parent_widget):
        super().__init__(parent_widget)
        self.selected_color = initial_color
        self.persistent_colors = persistent_colors
        self.parent_context = parent_widget 
        
        self.hue = initial_color.hue() if initial_color.hue() != -1 else 0
        self.sat = initial_color.saturation()
        self.val = initial_color.value()
        self.custom_chips = []
        
        self.setWindowTitle("🖋 Renk Seç")
        self.setFixedSize(520, 360)
        self.setStyleSheet("""
            QDialog { background-color: #1c1c1e; color: white; }
            QLabel { color: #ebebeb; font-size: 12px; font-weight: bold; }
            QPushButton#ActionBtn { 
                background-color: #2c2c2e; border: 1px solid #3a3a3c; 
                border-radius: 6px; padding: 8px; color: white; font-size: 11px;
            }
            QPushButton#ActionBtn:hover { background-color: #3a3a40; border: 1px solid #007aff; }
            QPushButton#ToolBtn { 
                background-color: #2c2c2e; border: 1.5px solid #3a3a3c; border-radius: 6px; font-size: 16px; 
            }
            QPushButton#ToolBtn:hover { background-color: #ff3b30; border-color: white; }
        """)
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Temel Renkler"))
        basic_grid = QGridLayout()
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffffff", "#000000", "#808080", "#ffa500"]
        for i, c in enumerate(colors):
            btn = self.create_color_chip(c)
            basic_grid.addWidget(btn, i // 5, i % 5)
        left_panel.addLayout(basic_grid)
        
        line = QFrame(); line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3a3a3c; margin: 10px 0;"); left_panel.addWidget(line)
        
        left_panel.addWidget(QLabel("Özel Renkler"))
        self.custom_grid = QGridLayout()
        for i in range(10):
            color_hex = self.persistent_colors[i]
            chip = self.create_color_chip(color_hex, empty=(color_hex == "#2c2c2e"))
            self.custom_chips.append(chip)
            self.custom_grid.addWidget(chip, i // 5, i % 5)
        left_panel.addLayout(self.custom_grid)
        
        left_panel.addStretch()
        
        bottom_left_btns = QHBoxLayout()
        self.add_btn = QPushButton("Palete Ekle"); self.add_btn.setObjectName("ActionBtn")
        self.add_btn.clicked.connect(self.add_to_custom)
        
        self.trash_btn = QPushButton("🗑️")
        self.trash_btn.setFixedSize(35, 35); self.trash_btn.setObjectName("ToolBtn")
        self.trash_btn.clicked.connect(self.reset_custom)
        
        bottom_left_btns.addWidget(self.add_btn); bottom_left_btns.addWidget(self.trash_btn)
        left_panel.addLayout(bottom_left_btns); main_layout.addLayout(left_panel)
        
        right_panel = QVBoxLayout()
        self.sv_map = SVMapWidget(self.hue, self.sat, self.val)
        self.sv_map.colorChanged.connect(self.update_sv); right_panel.addWidget(self.sv_map)
        
        self.hue_slider = QSlider(Qt.Horizontal); self.hue_slider.setRange(0, 359); self.hue_slider.setValue(self.hue)
        self.hue_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 12px; border-radius: 6px; background: qlineargradient(x1:0, x2:1, stop:0 red, stop:0.17 yellow, stop:0.33 green, stop:0.5 cyan, stop:0.67 blue, stop:0.83 magenta, stop:1 red); }
            QSlider::handle:horizontal { background: white; border: 2px solid black; width: 14px; margin: -2px 0; border-radius: 7px; }
        """)
        self.hue_slider.valueChanged.connect(self.update_hue); right_panel.addWidget(self.hue_slider)
        
        self.preview_bar = QFrame(); self.preview_bar.setFixedHeight(35); self.update_preview()
        right_panel.addWidget(self.preview_bar)
        
        btn_box = QHBoxLayout(); btn_box.addStretch()
        ok_btn = QPushButton("Tamam"); ok_btn.setObjectName("ActionBtn"); ok_btn.clicked.connect(self.accept)
        btn_box.addWidget(ok_btn); right_panel.addLayout(btn_box)
        main_layout.addLayout(right_panel)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            self.accept()
        else:
            super().keyPressEvent(event)

    def create_color_chip(self, color_hex, empty=False):
        btn = QPushButton(); btn.setFixedSize(28, 28); btn.setCursor(Qt.PointingHandCursor)
        border = "#3a3a3c" if empty else "#007aff"
        btn.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px; border: 1.5px solid {border};")
        if not empty: btn.clicked.connect(lambda: self.set_direct_color(QColor(color_hex)))
        return btn

    def get_toolbar(self):
        if isinstance(self.parent_context, StandaloneText):
            return self.parent_context.owner.toolbar
        return self.parent_context.toolbar if hasattr(self.parent_context, 'toolbar') else self.parent_context

    def add_to_custom(self):
        toolbar = self.get_toolbar()
        if toolbar:
            idx = toolbar.custom_color_index
            color_hex = self.selected_color.name()
            self.persistent_colors[idx] = color_hex
            chip = self.custom_chips[idx]
            chip.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px; border: 1.5px solid #007aff;")
            try: chip.clicked.disconnect()
            except: pass
            chip.clicked.connect(lambda _, c=color_hex: self.set_direct_color(QColor(c)))
            toolbar.custom_color_index = (idx + 1) % 10

    def reset_custom(self):
        toolbar = self.get_toolbar()
        for i in range(10):
            self.persistent_colors[i] = "#2c2c2e"
            chip = self.custom_chips[i]
            chip.setStyleSheet("background-color: #2c2c2e; border-radius: 4px; border: 1.5px solid #3a3a3c;")
            try: chip.clicked.disconnect()
            except: pass
        if toolbar: toolbar.custom_color_index = 0

    def set_direct_color(self, color):
        self.selected_color = color; self.hue = color.hue() if color.hue() != -1 else 0
        self.sat = color.saturation(); self.val = color.value()
        self.hue_slider.setValue(self.hue); self.sv_map.update_hsv(self.hue, self.sat, self.val)
        self.update_preview()

    def update_hue(self, val): self.hue = val; self.sv_map.update_hsv(self.hue, self.sat, self.val); self.update_selected_color()
    def update_sv(self, s, v): self.sat = s; self.val = v; self.update_selected_color()
    def update_selected_color(self): self.selected_color = QColor.fromHsv(self.hue, self.sat, self.val); self.update_preview()
    def update_preview(self): self.preview_bar.setStyleSheet(f"background-color: {self.selected_color.name()}; border: 2.5px solid #ffffff; border-radius: 8px;")

class SVMapWidget(QWidget):
    colorChanged = pyqtSignal(int, int)
    def __init__(self, h, s, v):
        super().__init__(); self.h, self.s, self.v = h, s, v; self.setFixedSize(240, 160)
    def update_hsv(self, h, s, v): self.h, self.s, self.v = h, s, v; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        base_color = QColor.fromHsv(self.h, 255, 255)
        grad_s = QLinearGradient(0, 0, self.width(), 0); grad_s.setColorAt(0, Qt.white); grad_s.setColorAt(1, base_color)
        p.fillRect(self.rect(), QBrush(grad_s))
        grad_v = QLinearGradient(0, 0, 0, self.height()); grad_v.setColorAt(0, Qt.transparent); grad_v.setColorAt(1, Qt.black)
        p.fillRect(self.rect(), QBrush(grad_v))
        p.setPen(QPen(Qt.white if self.v < 128 else Qt.black, 2))
        x = int((self.s / 255) * self.width()); y = int((1 - self.v / 255) * self.height())
        p.drawEllipse(QPoint(x, y), 6, 6)
    def mousePressEvent(self, event): self.handle_mouse(event)
    def mouseMoveEvent(self, event): self.handle_mouse(event)
    def handle_mouse(self, event):
        x = max(0, min(event.x(), self.width())); y = max(0, min(event.y(), self.height()))
        self.s = int((x / self.width()) * 255); self.v = int((1 - y / self.height()) * 255)
        self.colorChanged.emit(self.s, self.v); self.update()

# --- STANDALONE MODERN TEXT BOX ---
class TextEventFilter(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.parent_widget.edit.isReadOnly():
                self.parent_widget.set_active_mode(True)
                return True
        return False

class StandaloneText(QWidget):
    def __init__(self, owner, creation_mode, initial_color):
        super().__init__()
        self.owner = owner
        self.creation_mode = creation_mode
        self.text_color = initial_color
        self.old_pos = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 100)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.container = QFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.edit = QTextEdit()
        self.edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.edit.setPlaceholderText("Yazmaya başlayın...")
        self.filter = TextEventFilter(self)
        self.edit.installEventFilter(self.filter)
        self.container_layout.addWidget(self.edit)
        
        self.layout.addWidget(self.container)
        
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(35)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(2, 5, 2, 5); self.side_layout.setSpacing(8)
        
        self.btn_palette = QPushButton("🎨")
        self.btn_palette.setFixedSize(28, 28)
        self.btn_palette.setStyleSheet("background: #2c2c2e; border-radius: 14px; border: 1px solid #3a3a3c; font-size: 14px;")
        self.btn_palette.clicked.connect(self.open_text_color_picker)
        self.side_layout.addWidget(self.btn_palette)
        
        self.btn_ok = QPushButton("✓")
        self.btn_ok.setFixedSize(28, 28)
        self.btn_ok.setStyleSheet("background: #007aff; color: white; border-radius: 14px; font-weight: bold;")
        self.btn_ok.clicked.connect(lambda: self.set_active_mode(False))
        self.side_layout.addWidget(self.btn_ok)
        
        self.layout.addWidget(self.side_panel)
        self.size_grip = QSizeGrip(self)
        self.layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        
        self.set_active_mode(True)
        self.show()

    def open_text_color_picker(self):
        picker = ModernColorPicker(self.text_color, self.owner.toolbar.custom_colors, self)
        if picker.exec_():
            self.text_color = picker.selected_color
            self.update_appearance()
        QTimer.singleShot(10, self.owner.force_focus)

    def update_appearance(self):
        f_size = max(14, self.height() // 3.5)
        if self.edit.isReadOnly():
            self.container.setStyleSheet("background: transparent; border: none;")
            self.edit.setStyleSheet(f"""
                color: {self.text_color.name()}; background: transparent; border: none; 
                font-size: {f_size}px; font-weight: 700; font-family: 'Segoe UI', sans-serif;
            """)
            self.side_panel.hide(); self.size_grip.hide()
        else:
            self.container.setStyleSheet("""
                background: rgba(255, 255, 255, 248); border: 2.5px solid #007aff; border-radius: 14px;
            """)
            self.edit.setStyleSheet(f"""
                color: black; background: transparent; border: none; 
                font-size: {f_size - 4}px; font-family: 'Segoe UI', sans-serif;
            """)
            self.side_panel.show(); self.size_grip.show()

    def set_active_mode(self, active):
        self.edit.setReadOnly(not active)
        if not active: self.owner.force_focus()
        self.update_appearance()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.edit.isReadOnly(): self.set_active_mode(True)
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos and not self.edit.isReadOnly():
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPos()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_appearance()

# --- ANA ÇİZİM VE ARAÇ ÇUBUĞU ---
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

    # --- KISAYOL TUŞLARI ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            self.undo()
        elif event.key() == Qt.Key_Q:
            QApplication.quit()
        elif event.key() == Qt.Key_S:
            self.take_screenshot()
        elif event.key() == Qt.Key_D:
            self.clear_all()
        elif event.key() == Qt.Key_V:
            if self.toolbar:
                self.toolbar.toggle_move_mode()
        elif event.key() == Qt.Key_C:
            if self.toolbar:
                self.toolbar.select_color()
        elif event.key() == Qt.Key_Space:
            if self.toolbar:
                self.toolbar.toggle_board()

    def force_focus(self):
        self.activateWindow(); self.raise_(); self.setFocus()

    def redraw_canvas(self):
        self.canvas.fill(Qt.transparent)
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        
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
            self.redraw_canvas()
            self.update()

    def clear_all(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in target[:]:
            if isinstance(item, dict) and item.get('type') == 'text': item['obj'].close()
        target.clear()
        self.canvas.fill(Qt.transparent)
        self.update()

    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        QTimer.singleShot(400, self._perform_capture)

    def _perform_capture(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pics = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        path = os.path.join(pics, f"Vizia_{timestamp}.png")
        if screenshot.save(path): 
            self.show_toast("Başarıyla Kaydedildi !")
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
        if self.whiteboard_mode:
            painter.fillRect(self.rect(), Qt.white)
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
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
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        
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
        
        painter.drawPath(path_segment)
        painter.end()
        
        self.current_stroke_path.quadTo(self.last_point, mid_point)
        self.current_stroke_path.lineTo(current_pos)
        
        self.last_point = current_pos
        self.update()

    def mouseReleaseEvent(self, event):
        if self.drawing:
            item = {
                'type': 'path', 
                'path': QPainterPath(self.current_stroke_path), 
                'color': QColor(self.current_color), 
                'width': self.brush_size, 
                'mode': self.drawing_mode
            }
            target = self.board_history if self.whiteboard_mode else self.desktop_history
            target.append(item)
        self.drawing = False
        self.update()

class ModernToolbar(QWidget):
    def __init__(self, overlay):
        super().__init__(overlay)
        self.overlay = overlay; self.old_pos = None
        self.custom_colors = ["#2c2c2e"] * 10 
        self.custom_color_index = 0
        self.last_active_tool = "pen" # Hafıza mekanizması
        self.initUI()
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedWidth(75); self.setFixedHeight(560) 
        self.setStyleSheet("""
            QWidget { background-color: #1c1c1e; border-radius: 20px; border: 1.5px solid #3a3a3c; }
            QPushButton { background-color: #2c2c2e; color: white; border: none; border-radius: 10px; font-size: 18px; min-width: 38px; min-height: 38px; }
            QPushButton:hover { background-color: #3a3a40; border: 1px solid #007aff; }
            QLabel { color: white; background: transparent; border: none; font-size: 10px; font-weight: 800; }
            QSlider::groove:horizontal { border: none; height: 4px; background: #2c2c2e; border-radius: 2px; }
            QSlider::handle:horizontal { background: #007aff; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
        """)
        layout = QVBoxLayout(self); layout.setContentsMargins(10, 12, 10, 10); layout.setSpacing(5) 
        vizia = QLabel("VIZIA"); vizia.setAlignment(Qt.AlignCenter); layout.addWidget(vizia)
        pen = QLabel("PEN"); pen.setAlignment(Qt.AlignCenter); pen.setStyleSheet("margin-top: -6px; margin-bottom: 5px;"); layout.addWidget(pen)
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
        lbl_size = QLabel("BOYUT"); lbl_size.setAlignment(Qt.AlignCenter); lbl_size.setStyleSheet("font-size: 9px; font-weight: 900; margin-top: 5px;"); layout.addWidget(lbl_size)
        slider = QSlider(Qt.Horizontal); slider.setRange(2, 100); slider.setValue(4); slider.setFixedWidth(52)
        slider.valueChanged.connect(self.update_brush_size); layout.addWidget(slider, 0, Qt.AlignCenter)
        self.lbl_percent = QLabel("4%"); self.lbl_percent.setAlignment(Qt.AlignCenter); self.lbl_percent.setStyleSheet("font-size: 11px; color: #007aff; font-weight: 900;"); layout.addWidget(self.lbl_percent)
        layout.addStretch(); layout.addWidget(self.create_btn("✕", QApplication.quit), 0, Qt.AlignCenter)
        self.safe_change("pen", self.btn_draw)

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
        self.overlay.redraw_canvas()
        self.overlay.update(); QTimer.singleShot(10, self.overlay.force_focus)
    
    def toggle_move_mode(self):
        """V tuşu için özel akıllı geçiş"""
        if self.overlay.drawing_mode != "move":
            # Hafızaya al ve mouse moduna geç
            self.last_active_tool = self.overlay.drawing_mode
            self.safe_change("move", self.btn_move)
        else:
            # Hafızadaki eski araca dön
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

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv); overlay = DrawingOverlay(); toolbar = ModernToolbar(overlay)
    overlay.toolbar = toolbar; toolbar.show(); sys.exit(app.exec_())
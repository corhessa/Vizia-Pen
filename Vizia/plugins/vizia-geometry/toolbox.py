# plugins/vizia-geometry/toolbox.py
import json
import os
import sys
from collections import deque
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QSlider, QFrame, QMenu,
    QGraphicsDropShadowEffect, QGridLayout,
    QApplication, QMessageBox
)
from PyQt5.QtCore import (
    Qt, QSize, QPointF, QRectF, pyqtSignal, QPoint, QMimeData,
)
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPen, QCursor, QPixmap,
    QIcon, QPainterPath, QDrag,
)

# Shapes modülünü yükle
try:
    from shapes import CanvasShape, draw_shape_path
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from shapes import CanvasShape, draw_shape_path

# [GÜVENLİ İMPORT] Ana projenin 'ui' klasörüne erişim sağla
vizia_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if vizia_root not in sys.path:
    sys.path.insert(0, vizia_root)

try:
    from ui.widgets.color_picker import ModernColorPicker
except ImportError:
    ModernColorPicker = None

# ---------------------------------------------------------------------------
# GLOBAL ASSET YOLU BULUCU
# ---------------------------------------------------------------------------
def get_asset_path(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    path = os.path.abspath(os.path.join(base_dir, "../../Assets", filename))
    if os.path.exists(path): return path
    if hasattr(sys, "_MEIPASS"):
        path = os.path.join(sys._MEIPASS, "Assets", filename)
        if os.path.exists(path): return path
    return None

# ---------------------------------------------------------------------------
# Şekil İkonu Oluşturucu
# ---------------------------------------------------------------------------
def _shape_icon(shape_type, size=28, color=None):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    fill_color = color if color else QColor(0, 170, 255, 200)
    painter.setBrush(fill_color)
    painter.setPen(QPen(QColor(220, 220, 220), 1.5))
    rect = QRectF(3, 3, size - 6, size - 6)
    draw_shape_path(painter, shape_type, rect)
    painter.end()
    return QIcon(pixmap)

# ---------------------------------------------------------------------------
# Sürükle-Bırak Butonu
# ---------------------------------------------------------------------------
class DraggableShapeButton(QPushButton):
    def __init__(self, shape_type, tooltip, parent=None):
        super().__init__(parent)
        self.shape_type = shape_type
        self.setIcon(_shape_icon(shape_type))
        self.setIconSize(QSize(24, 24))
        self.setToolTip(tooltip)
        self.setCheckable(True)
        self.setFixedSize(44, 44)
        self._drag_start = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self._drag_start is not None and (event.pos() - self._drag_start).manhattanLength() > 10):
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"shape:{self.shape_type}")
            drag.setMimeData(mime)
            
            pixmap = QPixmap(48, 48); pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap); painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(0, 170, 255, 150))
            painter.setPen(QPen(QColor(220, 220, 220), 1.5))
            draw_shape_path(painter, self.shape_type, QRectF(4, 4, 40, 40))
            painter.end()
            drag.setPixmap(pixmap)
            drag.exec_(Qt.CopyAction)
            
            self._drag_start = None
            self.setChecked(False) 
            return
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._drag_start = None
        super().mouseReleaseEvent(event)

# ---------------------------------------------------------------------------
# [GERİ EKLENDİ] Canvas Overlay (Çizim Katmanı)
# ---------------------------------------------------------------------------
class ShapeCanvasOverlay(QWidget):
    shape_selected = pyqtSignal(object)
    shape_deselected = pyqtSignal()
    shapes_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shapes = []
        self._active_shape = None
        self._mode = "select"
        self._draw_type = None
        self._draw_start = None
        self._draw_rect = None
        self._current_color = QColor(0, 255, 255, 150)
        self._current_stroke_width = 3
        self._current_filled = True
        self._undo_stack = deque(maxlen=50)

        # Şeffaflık ve Mouse Ayarları
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

    def set_mode(self, mode, draw_type=None):
        self._mode = mode
        self._draw_type = draw_type
        self.setCursor(Qt.CrossCursor if mode == "draw" else Qt.ArrowCursor)

    def set_color(self, color): self._current_color = QColor(color)
    def set_stroke_width(self, w): self._current_stroke_width = w
    def set_filled(self, filled): self._current_filled = filled

    def _push_undo(self):
        snap = [s.snapshot() for s in self.shapes]
        self._undo_stack.append(snap)

    def undo(self):
        if not self._undo_stack: return
        snap = self._undo_stack.pop()
        self.shapes.clear()
        self._active_shape = None
        for s_data in snap:
            shape = CanvasShape(
                s_data["shape_type"], s_data["color"],
                s_data["rect"].x(), s_data["rect"].y(),
                s_data["rect"].width(), s_data["rect"].height(),
            )
            shape.border_color = s_data["border_color"]
            shape.stroke_width = s_data["stroke_width"]
            shape.rotation = s_data.get("rotation", 0.0)
            shape.filled = s_data.get("filled", True)
            shape.text = s_data.get("text", "")
            shape.is_flipped = s_data.get("is_flipped", False) 
            self.shapes.append(shape)
        self.shape_deselected.emit()
        self.shapes_changed.emit()
        self.update()

    def add_shape(self, shape):
        self._push_undo()
        self.shapes.append(shape)
        self._select(shape)
        self.shapes_changed.emit()
        self.update()

    def remove_shape(self, shape):
        self._push_undo()
        if shape in self.shapes: self.shapes.remove(shape)
        if self._active_shape is shape:
            self._active_shape = None
            self.shape_deselected.emit()
        self.shapes_changed.emit()
        self.update()

    def clear_shapes(self):
        if not self.shapes: return
        self._push_undo()
        self.shapes.clear()
        self._active_shape = None
        self.shape_deselected.emit()
        self.shapes_changed.emit()
        self.update()

    def active_shape(self): return self._active_shape

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("shape:"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        if text.startswith("shape:"):
            shape_type = text.split(":", 1)[1]
            pos = QPointF(event.pos())
            shape = CanvasShape(shape_type, self._current_color, pos.x()-80, pos.y()-80, 160, 160)
            shape.stroke_width = self._current_stroke_width
            shape.filled = self._current_filled
            self.add_shape(shape)
            event.acceptProposedAction()

    def paintEvent(self, event):
        painter = QPainter(self)
        for shape in self.shapes: shape.paint(painter)
        
        if self._mode == "draw" and self._draw_start and self._draw_rect:
            r = self._draw_rect
            preview_color = QColor(self._current_color); preview_color.setAlpha(80)
            painter.setBrush(preview_color)
            painter.setPen(QPen(QColor(0, 170, 255, 200), 2, Qt.DashLine))
            inner = r.adjusted(2, 2, -2, -2)
            if self._draw_type and inner.width() > 5:
                # Önizleme sırasında da çizgi yönünü hesapla
                flags = {}
                if self._draw_type == "line":
                    cur = self.mapFromGlobal(QCursor.pos())
                    dx = cur.x() - self._draw_start.x()
                    dy = cur.y() - self._draw_start.y()
                    if (dx * dy) < 0: flags["flipped"] = True

                draw_shape_path(painter, self._draw_type, inner, flags)
            else:
                painter.drawRect(r)
        painter.end()

    def mousePressEvent(self, event):
        pos = QPointF(event.pos())
        
        if self._mode == "draw" and event.button() == Qt.LeftButton:
            self._draw_start = pos
            self._draw_rect = QRectF(pos, pos)
            return

        if event.button() == Qt.LeftButton:
            if self._active_shape and self._active_shape.selected:
                handle = self._active_shape.handle_at(event.pos()) 
                if handle is not None:
                    self._push_undo()
                    self._active_shape.start_resize(handle, event.pos())
                    return

            for shape in reversed(self.shapes):
                if shape.contains(event.pos()):
                    self._push_undo()
                    self._select(shape)
                    shape.start_move(event.pos())
                    return

            self._deselect()
            return

        if event.button() == Qt.RightButton:
            for shape in reversed(self.shapes):
                if shape.contains(event.pos()):
                    self._show_context_menu(shape, event.globalPos())
                    return

    def mouseMoveEvent(self, event):
        pos = QPointF(event.pos())
        if self._mode == "draw" and self._draw_start:
            self._draw_rect = QRectF(self._draw_start, pos).normalized()
            self.update()
            return

        if self._active_shape:
            if self._active_shape._resize_handle is not None or self._active_shape._rotating:
                self._active_shape.do_resize(event.pos())
                self.update()
                return
            if self._active_shape._drag_offset is not None:
                self._active_shape.do_move(event.pos())
                self.update()
                return

        cursor_set = False
        for shape in reversed(self.shapes):
            if shape.selected:
                h = shape.handle_at(event.pos())
                if h == "rotate": self.setCursor(Qt.CrossCursor); cursor_set=True; break
                if h is not None: self.setCursor(Qt.SizeFDiagCursor); cursor_set=True; break
            if shape.contains(event.pos()) and self._mode == "select":
                self.setCursor(Qt.OpenHandCursor); cursor_set=True; break
        
        if not cursor_set and self._mode == "select":
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if self._mode == "draw" and self._draw_start and self._draw_rect:
            r = self._draw_rect.normalized()
            if r.width() > 10:
                shape = CanvasShape(self._draw_type, self._current_color, r.x(), r.y(), r.width(), r.height())
                shape.stroke_width = self._current_stroke_width; shape.filled = self._current_filled
                
                # Çapraz Çizgi Mantığı
                if self._draw_type == "line":
                    dx = event.pos().x() - self._draw_start.x()
                    dy = event.pos().y() - self._draw_start.y()
                    if (dx * dy) < 0:
                        shape.is_flipped = True
                
                self.add_shape(shape)
            self._draw_start = None; self._draw_rect = None
            self.update()
            return

        if self._active_shape:
            self._active_shape.end_move()
            self._active_shape.end_resize()
        self.shapes_changed.emit()
        self.update()

    def _select(self, shape):
        if self._active_shape and self._active_shape is not shape:
            self._active_shape.selected = False
        shape.selected = True
        self._active_shape = shape
        self.shape_selected.emit(shape)
        self.update()

    def _deselect(self):
        if self._active_shape:
            self._active_shape.selected = False
            self._active_shape = None
        self.shape_deselected.emit()
        self.update()

    def _show_context_menu(self, shape, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu {background:#2b2b2b; color:#eee; border:1px solid #555; padding:4px;} QMenu::item:selected {background:#00aaff;}")
        act_del = menu.addAction("Sil")
        if menu.exec_(global_pos) == act_del: self.remove_shape(shape)


# ---------------------------------------------------------------------------
# Stil Tanımları (CSS)
# ---------------------------------------------------------------------------
_TOOLBAR_STYLE = """
/* Ana Çerçeve Stili */
QFrame#ContentFrame {
    background-color: #1c1c1e; 
    border: 1.5px solid #3a3a3c;
    border-radius: 12px;
}

QPushButton, QToolButton {
    background-color: #2c2c2e;
    border: 1px solid #3a3a3c;
    border-radius: 8px;
    padding: 4px;
    color: #ddd;
    font-weight: bold;
    font-size: 11px;
}
QPushButton:hover, QToolButton:hover { background-color: #3a3a40; border-color: #007aff; }
QPushButton:pressed, QToolButton:pressed { background-color: #007aff; color: white; }
QPushButton:checked, QToolButton:checked { background-color: #007aff; color: white; border-color: white; }

QLabel { color: #8e8e93; font-size: 11px; font-weight: bold; background: transparent; }

/* SLIDER (Flat Style - Parlama Yok) */
QSlider::groove:horizontal { 
    background: #3a3a3c; 
    height: 4px; 
    border-radius: 2px; 
}

QSlider::sub-page:horizontal {
    background: #555555; 
    border-radius: 2px;
}

QSlider::handle:horizontal { 
    background: #b0b0b0; 
    border: none; 
    width: 12px; 
    height: 12px; 
    margin: -4px 0; 
    border-radius: 6px; 
}

QSlider::handle:horizontal:hover {
    background: #ffffff; 
}

QFrame#Separator { background-color: #48484a; max-width: 1px; margin: 4px 2px; border:none; }
"""

class GeometryToolbox(QWidget):
    def __init__(self, canvas_overlay, main_overlay):
        super().__init__()
        self.canvas = canvas_overlay
        self.main_overlay = main_overlay 
        self.current_color = QColor(0, 255, 255, 150)
        self._shape_buttons = {}
        self._drag_pos = None

        # [HATA DÜZELTME] Color Picker'ın çökmemesi için gerekli değişken
        self.custom_color_index = 0 

        self.setObjectName("GeometryToolbar")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TranslucentBackground) # Arka plan şeffaf

        self._init_ui()
        
        # Gölge Efekti
        shadow = QGraphicsDropShadowEffect(self.content_frame)
        shadow.setBlurRadius(24); shadow.setOffset(0, 4); shadow.setColor(QColor(0,0,0,120))
        self.content_frame.setGraphicsEffect(shadow)
        
        if self.canvas:
            self.canvas.shape_selected.connect(self._on_shape_selected)

    def _init_ui(self):
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)

        # İçerik Çerçevesi (Koyu Tonlu Arka Plan)
        self.content_frame = QFrame()
        self.content_frame.setObjectName("ContentFrame")
        self.content_frame.setStyleSheet(_TOOLBAR_STYLE)
        window_layout.addWidget(self.content_frame)

        main = QVBoxLayout(self.content_frame)
        main.setContentsMargins(10, 6, 10, 6)
        main.setSpacing(4)
        
        # --- ÜST SATIR ---
        top = QHBoxLayout(); top.setSpacing(3)
        drag = QLabel("☰"); drag.setFixedWidth(18); drag.setAlignment(Qt.AlignCenter)
        top.addWidget(drag); top.addWidget(self._sep())

        shapes = [("rect","Kare"), ("circle","Daire"), ("triangle","Üçgen"), ("star","Yıldız"), ("arrow","Ok"), ("note","Not"), ("line","Çizgi")]
        for k, t in shapes:
            btn = DraggableShapeButton(k, t) 
            btn.clicked.connect(lambda c, x=k: self._on_shape_btn(x, c))
            top.addWidget(btn); self._shape_buttons[k] = btn
        
        main.addLayout(top)
        
        # --- ALT SATIR ---
        bot = QHBoxLayout(); bot.setSpacing(3)
        
        # Renk Butonu
        self.btn_color = QPushButton(); self.btn_color.setFixedSize(32, 32)
        self._update_color_button()
        self.btn_color.clicked.connect(self._toggle_color_popup)
        bot.addWidget(self.btn_color)

        # Dolgu Butonu
        self.btn_fill = QPushButton("◼"); self.btn_fill.setFixedSize(32, 32)
        self.btn_fill.setCheckable(True); self.btn_fill.setChecked(True)
        self.btn_fill.toggled.connect(lambda c: self.canvas.set_filled(c) if self.canvas else None)
        bot.addWidget(self.btn_fill)
        bot.addWidget(self._sep())

        # Kalınlık
        for w, l in [(1,"İnce"), (3,"Orta"), (6,"Kalın")]:
            b = QPushButton(l); b.setFixedSize(45, 28)
            b.setCheckable(True); b.setFont(QFont("Arial", 9))
            if w==3: b.setChecked(True)
            b.clicked.connect(lambda c, x=w: self._on_stroke_width(x))
            setattr(self, f"_stroke_btn_{w}", b)
            bot.addWidget(b)
        
        bot.addWidget(self._sep())

        # Döndür
        lbl_rot = QLabel("Döndür:"); lbl_rot.setStyleSheet("margin-right: 2px;")
        bot.addWidget(lbl_rot)

        sl = QSlider(Qt.Horizontal); sl.setRange(0, 360); sl.setFixedWidth(70)
        sl.valueChanged.connect(self._on_rot); self.slider_rot = sl
        bot.addWidget(sl)

        bot.addWidget(self._sep())

        # Geri Al / Sil
        undo_path = get_asset_path("undo.png")
        btn_undo = QPushButton(); btn_undo.setFixedSize(32, 32)
        if undo_path: btn_undo.setIcon(QIcon(undo_path)); btn_undo.setIconSize(QSize(20,20))
        else: btn_undo.setText("↩")
        btn_undo.clicked.connect(lambda: self.canvas.undo() if self.canvas else None)
        bot.addWidget(btn_undo)

        bin_path = get_asset_path("bin.png")
        btn_clear = QPushButton(); btn_clear.setFixedSize(32, 32)
        if bin_path: btn_clear.setIcon(QIcon(bin_path)); btn_clear.setIconSize(QSize(20,20))
        else: btn_clear.setText("🗑")
        btn_clear.clicked.connect(lambda: self.canvas.clear_shapes() if self.canvas else None)
        bot.addWidget(btn_clear)

        main.addLayout(bot)

    def _sep(self): f=QFrame(); f.setFrameShape(QFrame.VLine); f.setObjectName("Separator"); return f

    # Panel Taşıma
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.LeftButton: self.move(e.globalPos() - self._drag_pos)

    # İşlevler
    def _on_shape_btn(self, k, c):
        for key, b in self._shape_buttons.items(): 
            if key != k: b.setChecked(False)
        if c and self.canvas: self.canvas.set_mode("draw", k)
        elif self.canvas: self.canvas.set_mode("select")

    def _toggle_color_popup(self):
        if not self.main_overlay: return
        if not ModernColorPicker: 
            QMessageBox.warning(self, "Hata", "Renk seçici yüklenemedi. (Import Error)")
            return

        # Settings'den kayıtlı renkleri al
        custom_colors = self.main_overlay.settings.get("custom_colors")
        
        picker = ModernColorPicker(self.current_color, custom_colors, self.main_overlay.settings, self)
        if picker.exec_():
            color = picker.selected_color
            self._on_color_picked(color)
            
    def _on_color_picked(self, c):
        self.current_color = c
        self._update_color_button()
        if self.canvas:
            self.canvas.set_color(c)
            if self.canvas.active_shape(): 
                self.canvas.active_shape().color = c
                self.canvas.update()

    def _update_color_button(self):
        self.btn_color.setStyleSheet(f"background-color:{self.current_color.name()}; border:2px solid #888; border-radius:8px;")
        
    def update_color_btn_style(self):
        # ColorPicker bunu çağırabilir
        self._update_color_button()

    def _on_stroke_width(self, w):
        for x in [1,3,6]: getattr(self, f"_stroke_btn_{x}").setChecked(x==w)
        if self.canvas:
            self.canvas.set_stroke_width(w)
            if self.canvas.active_shape():
                self.canvas.active_shape().stroke_width = w
                self.canvas.update()

    def _on_rot(self, v):
        if self.canvas and self.canvas.active_shape():
            self.canvas.active_shape().rotation = float(v)
            self.canvas.update()

    def _on_shape_selected(self, shape):
        self.slider_rot.blockSignals(True)
        self.slider_rot.setValue(int(shape.rotation) % 360)
        self.slider_rot.blockSignals(False)
        self.btn_fill.setChecked(shape.filled)
        self._on_stroke_width(shape.stroke_width)
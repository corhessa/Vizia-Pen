# plugins/vizia-geometry/toolbox.py
import json
import os
from collections import deque
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QSlider, QFrame, QMenu,
    QGraphicsDropShadowEffect, QSizePolicy, QGridLayout,
    QApplication,
)
from PyQt5.QtCore import (
    Qt, QSize, QPointF, QRectF, pyqtSignal, QPoint, QMimeData,
)
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPen, QCursor, QPixmap,
    QIcon, QPainterPath, QDrag,
)

from shapes import CanvasShape, draw_shape_path

# ---------------------------------------------------------------------------
# Sabit renk paleti (Vizia Pen uyumlu)
# ---------------------------------------------------------------------------
_DEFAULT_PALETTE = [
    "#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF",
    "#FFFF00", "#FF00FF", "#00FFFF", "#FF8800", "#8800FF",
    "#FF4444", "#44FF44", "#4444FF", "#FFAA00", "#00AAFF",
    "#AA00FF",
]

_PALETTE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "custom_palette.json")


def _load_custom_palette():
    """Vizia Pen ayarlarından kaydedilen özel renk paletini yükle."""
    try:
        with open(_PALETTE_FILE, "r") as f:
            data = json.load(f)
            return [c for c in data if isinstance(c, str)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_custom_palette(colors):
    try:
        with open(_PALETTE_FILE, "w") as f:
            json.dump(colors, f)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Şekil önizleme ikonu oluşturucu
# ---------------------------------------------------------------------------
def _shape_icon(shape_type, size=28, color=None):
    """Verilen şekil tipi için QIcon oluşturur."""
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
# Vizia tarzı renk seçici (inline, Windows dialog yerine)
# ---------------------------------------------------------------------------
class ViziaColorPicker(QWidget):
    """Vizia Pen uyumlu modern renk seçici – satır paleti + HSV slider."""

    color_picked = pyqtSignal(QColor)

    _STYLE = """
    QWidget#ViziaColorPicker {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #353535, stop:1 #2a2a2a);
        border: 1px solid #444;
        border-radius: 12px;
    }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ViziaColorPicker")
        self.custom_colors = _load_custom_palette()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setStyleSheet(self._STYLE)
        self._init_ui()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        lbl = QLabel("Renkler")
        lbl.setStyleSheet("color: #ccc; font-weight: bold; font-size: 11px; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        # Varsayılan renkler
        grid = QGridLayout()
        grid.setSpacing(3)
        for i, hex_color in enumerate(_DEFAULT_PALETTE):
            btn = self._color_btn(hex_color)
            grid.addWidget(btn, i // 8, i % 8)
        layout.addLayout(grid)

        # Özel renkler
        if self.custom_colors:
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet("background-color: #555;")
            layout.addWidget(sep)

            lbl2 = QLabel("Kayıtlı Renkler")
            lbl2.setStyleSheet("color: #999; font-size: 10px; background: transparent;")
            lbl2.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl2)

            grid2 = QGridLayout()
            grid2.setSpacing(3)
            for i, hex_color in enumerate(self.custom_colors[:16]):
                btn = self._color_btn(hex_color)
                grid2.addWidget(btn, i // 8, i % 8)
            layout.addLayout(grid2)

        # HSV Slider alanı
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background-color: #555;")
        layout.addWidget(sep2)

        # Ton (Hue)
        hue_lbl = QLabel("Ton")
        hue_lbl.setStyleSheet("color: #aaa; font-size: 10px; background: transparent;")
        layout.addWidget(hue_lbl)
        self._hue_slider = QSlider(Qt.Horizontal)
        self._hue_slider.setRange(0, 359)
        self._hue_slider.setValue(180)
        self._hue_slider.setFixedHeight(18)
        self._hue_slider.setStyleSheet(
            "QSlider::groove:horizontal { height: 10px; border-radius: 5px;"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #ff0000, stop:0.17 #ffff00, stop:0.33 #00ff00,"
            " stop:0.5 #00ffff, stop:0.67 #0000ff, stop:0.83 #ff00ff, stop:1 #ff0000); }"
            "QSlider::handle:horizontal { background: #fff; width: 14px; margin: -2px 0; border-radius: 7px;"
            " border: 2px solid #888; }"
        )
        self._hue_slider.valueChanged.connect(self._on_hsv_changed)
        layout.addWidget(self._hue_slider)

        # Doygunluk
        sat_lbl = QLabel("Doygunluk")
        sat_lbl.setStyleSheet("color: #aaa; font-size: 10px; background: transparent;")
        layout.addWidget(sat_lbl)
        self._sat_slider = QSlider(Qt.Horizontal)
        self._sat_slider.setRange(0, 255)
        self._sat_slider.setValue(255)
        self._sat_slider.setFixedHeight(18)
        self._sat_slider.setStyleSheet(
            "QSlider::groove:horizontal { height: 10px; border-radius: 5px;"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #808080, stop:1 #00aaff); }"
            "QSlider::handle:horizontal { background: #fff; width: 14px; margin: -2px 0; border-radius: 7px;"
            " border: 2px solid #888; }"
        )
        self._sat_slider.valueChanged.connect(self._on_hsv_changed)
        layout.addWidget(self._sat_slider)

        # Parlaklık
        val_lbl = QLabel("Parlaklık")
        val_lbl.setStyleSheet("color: #aaa; font-size: 10px; background: transparent;")
        layout.addWidget(val_lbl)
        self._val_slider = QSlider(Qt.Horizontal)
        self._val_slider.setRange(0, 255)
        self._val_slider.setValue(255)
        self._val_slider.setFixedHeight(18)
        self._val_slider.setStyleSheet(
            "QSlider::groove:horizontal { height: 10px; border-radius: 5px;"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #000000, stop:1 #ffffff); }"
            "QSlider::handle:horizontal { background: #fff; width: 14px; margin: -2px 0; border-radius: 7px;"
            " border: 2px solid #888; }"
        )
        self._val_slider.valueChanged.connect(self._on_hsv_changed)
        layout.addWidget(self._val_slider)

        # Önizleme + uygula + kaydet
        bottom_row = QHBoxLayout()
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(36, 36)
        self._preview_label.setStyleSheet(
            "background-color: #00aaff; border: 2px solid #666; border-radius: 6px;"
        )
        bottom_row.addWidget(self._preview_label)

        btn_apply = QPushButton("Uygula")
        btn_apply.setFixedHeight(30)
        btn_apply.setStyleSheet(
            "QPushButton { background: #00aaff; color: #fff; border: none;"
            " border-radius: 6px; font-weight: bold; font-size: 11px; padding: 4px 12px; }"
            "QPushButton:hover { background: #0099ee; }"
        )
        btn_apply.clicked.connect(self._apply_color)
        bottom_row.addWidget(btn_apply)

        btn_save = QPushButton("Kaydet")
        btn_save.setFixedHeight(30)
        btn_save.setToolTip("Rengi özel palete kaydet")
        btn_save.setStyleSheet(
            "QPushButton { background: #3c3c3c; color: #aaa; border: 1px solid #666;"
            " border-radius: 6px; font-size: 10px; padding: 4px 10px; }"
            "QPushButton:hover { border-color: #00aaff; color: #fff; }"
        )
        btn_save.clicked.connect(self._save_color)
        bottom_row.addWidget(btn_save)
        layout.addLayout(bottom_row)

        self._on_hsv_changed()

    def _color_btn(self, hex_color):
        btn = QPushButton()
        btn.setFixedSize(26, 26)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {hex_color}; border: 2px solid #555;"
            f" border-radius: 4px; min-height: 0; min-width: 0; padding: 0; }}"
            f"QPushButton:hover {{ border-color: #fff; }}"
        )
        btn.setToolTip(hex_color)
        btn.clicked.connect(lambda: self.color_picked.emit(QColor(hex_color)))
        return btn

    def _current_color(self):
        return QColor.fromHsv(
            self._hue_slider.value(),
            self._sat_slider.value(),
            self._val_slider.value(),
        )

    def _on_hsv_changed(self):
        c = self._current_color()
        self._preview_label.setStyleSheet(
            f"background-color: {c.name()}; border: 2px solid #666; border-radius: 6px;"
        )

    def _apply_color(self):
        self.color_picked.emit(self._current_color())

    def _save_color(self):
        c = self._current_color()
        hex_val = c.name()
        if hex_val not in self.custom_colors:
            self.custom_colors.append(hex_val)
            _save_custom_palette(self.custom_colors)


# ---------------------------------------------------------------------------
# Sürükle-bırak şekil butonu
# ---------------------------------------------------------------------------
class DraggableShapeButton(QPushButton):
    """Şekil butonu – tıkla veya sürükle-bırak ile canvas'a ekle."""

    shape_dropped = pyqtSignal(str, QPointF)

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
        if (self._drag_start is not None
                and (event.pos() - self._drag_start).manhattanLength() > 10):
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"shape:{self.shape_type}")
            drag.setMimeData(mime)

            pixmap = QPixmap(48, 48)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
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
# Şekil canvas overlay'i
# ---------------------------------------------------------------------------
class ShapeCanvasOverlay(QWidget):
    """Şekillerin çizildiği şeffaf overlay katmanı."""

    shape_selected = pyqtSignal(object)
    shape_deselected = pyqtSignal()
    shapes_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shapes: list[CanvasShape] = []
        self._active_shape = None
        self._mode = "select"
        self._draw_type = None
        self._draw_start = None
        self._draw_rect = None
        self._current_color = QColor(0, 255, 255, 150)
        self._current_stroke_width = 3
        self._current_filled = True
        self._undo_stack = deque(maxlen=50)
        self._needs_undo_push = False

        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

    # ---------- public API ----------
    def set_mode(self, mode, draw_type=None):
        self._mode = mode
        self._draw_type = draw_type
        if mode == "draw":
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_color(self, color):
        self._current_color = QColor(color)

    def set_stroke_width(self, w):
        self._current_stroke_width = w

    def set_filled(self, filled):
        self._current_filled = filled

    def _push_undo(self):
        snap = []
        for s in self.shapes:
            snap.append(s.snapshot())
        self._undo_stack.append(snap)

    def undo(self):
        if not self._undo_stack:
            return
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
        if shape in self.shapes:
            self.shapes.remove(shape)
        if self._active_shape is shape:
            self._active_shape = None
            self.shape_deselected.emit()
        self.shapes_changed.emit()
        self.update()

    def clear_shapes(self):
        if not self.shapes:
            return
        self._push_undo()
        self.shapes.clear()
        self._active_shape = None
        self.shape_deselected.emit()
        self.shapes_changed.emit()
        self.update()

    def active_shape(self):
        return self._active_shape

    # ---------- sürükle-bırak ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("shape:"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        if text.startswith("shape:"):
            shape_type = text.split(":", 1)[1]
            pos = QPointF(event.pos())
            shape = CanvasShape(
                shape_type, self._current_color,
                pos.x() - 80, pos.y() - 80, 160, 160,
            )
            shape.stroke_width = self._current_stroke_width
            shape.filled = self._current_filled
            self.add_shape(shape)
            event.acceptProposedAction()

    # ---------- çizim ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        for shape in self.shapes:
            shape.paint(painter)
        if self._mode == "draw" and self._draw_start and self._draw_rect:
            r = self._draw_rect
            preview_color = QColor(self._current_color)
            preview_color.setAlpha(80)
            painter.setBrush(preview_color)
            painter.setPen(QPen(QColor(0, 170, 255, 200), 2, Qt.DashLine))
            inner = r.adjusted(2, 2, -2, -2)
            if self._draw_type and inner.width() > 5 and inner.height() > 5:
                draw_shape_path(painter, self._draw_type, inner)
            else:
                painter.drawRect(r)
        painter.end()

    # ---------- mouse ----------
    def mousePressEvent(self, event):
        pos = QPointF(event.pos())

        if self._mode == "draw" and event.button() == Qt.LeftButton:
            self._draw_start = pos
            self._draw_rect = QRectF(pos, pos)
            return

        if event.button() == Qt.LeftButton:
            if self._active_shape and self._active_shape.selected:
                handle = self._active_shape.handle_at(pos)
                if handle is not None:
                    self._push_undo()
                    self._needs_undo_push = False
                    self._active_shape.start_resize(handle, pos)
                    return

            for shape in reversed(self.shapes):
                if shape.contains(pos):
                    self._push_undo()
                    self._needs_undo_push = False
                    self._select(shape)
                    shape.start_move(pos)
                    return

            # Boş yere tıklama → seçimi kaldır
            self._deselect()
            event.ignore()
            return

        if event.button() == Qt.RightButton:
            for shape in reversed(self.shapes):
                if shape.contains(pos):
                    self._show_context_menu(shape, event.globalPos())
                    return
            event.ignore()
            return

        event.ignore()

    def mouseMoveEvent(self, event):
        pos = QPointF(event.pos())

        if self._mode == "draw" and self._draw_start:
            self._draw_rect = QRectF(self._draw_start, pos).normalized()
            self.update()
            return

        if self._active_shape:
            if (self._active_shape._resize_handle is not None
                    or self._active_shape._rotating):
                self._active_shape.do_resize(pos)
                self.update()
                return
            if self._active_shape._drag_offset is not None:
                self._active_shape.do_move(pos)
                self.update()
                return

        for shape in reversed(self.shapes):
            if shape.selected:
                h = shape.handle_at(pos)
                if h == "rotate":
                    self.setCursor(Qt.CrossCursor)
                    return
                if h is not None:
                    self.setCursor(Qt.SizeFDiagCursor)
                    return
            if shape.contains(pos):
                if self._mode == "select":
                    self.setCursor(Qt.OpenHandCursor)
                return
        if self._mode == "select":
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if self._mode == "draw" and self._draw_start and self._draw_rect:
            r = self._draw_rect.normalized()
            if r.width() > 10 and r.height() > 10:
                shape = CanvasShape(
                    self._draw_type, self._current_color,
                    r.x(), r.y(), r.width(), r.height(),
                )
                shape.stroke_width = self._current_stroke_width
                shape.filled = self._current_filled
                self.add_shape(shape)
            self._draw_start = None
            self._draw_rect = None
            self.update()
            return

        if self._active_shape:
            self._active_shape.end_move()
            self._active_shape.end_resize()
        self.shapes_changed.emit()
        self.update()

    # ---------- yardımcılar ----------
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
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b; color: #eee;
                border: 1px solid #555; border-radius: 6px; padding: 4px;
            }
            QMenu::item:selected { background-color: #00aaff; }
        """)
        act_front = menu.addAction("⬆ Öne Getir")
        act_back = menu.addAction("⬇ Arkaya Gönder")
        menu.addSeparator()
        act_del = menu.addAction("❌ Sil")
        action = menu.exec_(global_pos)
        if action == act_del:
            self.remove_shape(shape)
        elif action == act_front:
            if shape in self.shapes:
                self._push_undo()
                self.shapes.remove(shape)
                self.shapes.append(shape)
                self.shapes_changed.emit()
                self.update()
        elif action == act_back:
            if shape in self.shapes:
                self._push_undo()
                self.shapes.remove(shape)
                self.shapes.insert(0, shape)
                self.shapes_changed.emit()
                self.update()


# ---------------------------------------------------------------------------
# Modern yatay araç paneli – sürüklenebilir, iki satırlı
# ---------------------------------------------------------------------------
_TOOLBAR_STYLE = """
QWidget#GeometryToolbar {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #353535, stop:1 #2a2a2a
    );
    border: 1px solid #444;
    border-radius: 12px;
}
QPushButton, QToolButton {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 4px 8px;
    color: #ddd;
    font-weight: bold;
    font-size: 11px;
    min-height: 0;
}
QPushButton:hover, QToolButton:hover {
    background-color: #505050;
    border-color: #00aaff;
}
QPushButton:pressed, QToolButton:pressed {
    background-color: #00aaff;
    color: #fff;
}
QPushButton:checked, QToolButton:checked {
    background-color: #00aaff;
    color: #fff;
    border-color: #0088cc;
}
QLabel {
    color: #aaa;
    font-size: 10px;
    background: transparent;
}
QLabel#SectionLabel {
    color: #ccc;
    font-size: 10px;
    font-weight: bold;
}
QSlider::groove:horizontal {
    border: 1px solid #555;
    height: 6px;
    background: #3e3e3e;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #00aaff;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QFrame#Separator {
    background-color: #555;
    max-width: 1px;
    margin: 4px 2px;
}
"""


class GeometryToolbox(QWidget):
    """Modern, yatay geometri araç çubuğu – sürüklenebilir, iki satırlı.

    Üst satır: Şekil butonları + hızlı ekle
    Alt satır: Özellikler (renk, kenarlık, dolgu, döndürme, saydamlık, geri al, temizle)
    """

    def __init__(self, canvas_overlay: ShapeCanvasOverlay = None):
        super().__init__()
        self.canvas = canvas_overlay
        self.current_color = QColor(0, 255, 255, 150)
        self._shape_buttons: dict[str, DraggableShapeButton] = {}
        self._draw_mode_active = False
        self._drag_pos = None
        self._color_popup = None
        self._init_ui()

        if self.canvas:
            self.canvas.shape_selected.connect(self._on_shape_selected)
            self.canvas.shape_deselected.connect(self._on_shape_deselected)

    def _init_ui(self):
        self.setObjectName("GeometryToolbar")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setStyleSheet(_TOOLBAR_STYLE)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(4)

        # ============ ÜST SATIR: Şekiller ============
        top_row = QHBoxLayout()
        top_row.setSpacing(3)

        # Sürükleme tutamağı
        drag_handle = QLabel("☰")
        drag_handle.setFixedWidth(18)
        drag_handle.setAlignment(Qt.AlignCenter)
        drag_handle.setStyleSheet("color: #777; font-size: 14px; background: transparent;")
        drag_handle.setToolTip("Paneli taşımak için sürükle")
        top_row.addWidget(drag_handle)
        top_row.addWidget(self._sep())

        # Şekil butonları (sürükle-bırak destekli)
        shapes_info = [
            ("rect", "Dikdörtgen – tıkla veya sürükle"),
            ("circle", "Daire – tıkla veya sürükle"),
            ("triangle", "Üçgen – tıkla veya sürükle"),
            ("star", "Yıldız – tıkla veya sürükle"),
            ("arrow", "Ok – akış diyagramı için"),
            ("note", "Not Kutusu – metin notu"),
            ("grid", "Izgara – tıkla veya sürükle"),
            ("line", "Çizgi – tıkla veya sürükle"),
        ]
        for key, tooltip in shapes_info:
            btn = DraggableShapeButton(key, tooltip)
            btn.setFixedSize(38, 38)
            btn.setIconSize(QSize(22, 22))
            btn.clicked.connect(lambda checked, k=key: self._on_shape_btn(k, checked))
            top_row.addWidget(btn)
            self._shape_buttons[key] = btn

        top_row.addWidget(self._sep())

        # Hızlı ekle
        btn_quick = QPushButton("➕")
        btn_quick.setToolTip("Merkeze şekil ekle")
        btn_quick.setFixedSize(38, 38)
        btn_quick.clicked.connect(self._quick_add)
        top_row.addWidget(btn_quick)

        main_layout.addLayout(top_row)

        # ============ ALT SATIR: Özellikler ============
        bot_row = QHBoxLayout()
        bot_row.setSpacing(3)

        # Renk
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(32, 32)
        self.btn_color.setToolTip("Renk seç")
        self._update_color_button()
        self.btn_color.clicked.connect(self._toggle_color_popup)
        bot_row.addWidget(self.btn_color)

        # Dolgu açma/kapama
        self.btn_fill = QPushButton("◼")
        self.btn_fill.setFixedSize(32, 32)
        self.btn_fill.setCheckable(True)
        self.btn_fill.setChecked(True)
        self.btn_fill.setToolTip("Dolgu aç/kapat")
        self.btn_fill.toggled.connect(self._on_fill_toggled)
        bot_row.addWidget(self.btn_fill)

        bot_row.addWidget(self._sep())

        # Kenarlık kalınlığı
        stroke_lbl = QLabel("Kenarlık")
        stroke_lbl.setObjectName("SectionLabel")
        bot_row.addWidget(stroke_lbl)

        for width, label, tip in [(1, "İnce", "İnce kenarlık"), (3, "Orta", "Orta kenarlık"), (6, "Kalın", "Kalın kenarlık")]:
            btn = QPushButton(label)
            btn.setFixedSize(42, 28)
            btn.setCheckable(True)
            btn.setToolTip(tip)
            if width == 3:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, w=width: self._on_stroke_width(w))
            bot_row.addWidget(btn)
            setattr(self, f"_stroke_btn_{width}", btn)

        bot_row.addWidget(self._sep())

        # Döndürme
        rot_lbl = QLabel("Döndür")
        rot_lbl.setObjectName("SectionLabel")
        bot_row.addWidget(rot_lbl)
        self.slider_rotation = QSlider(Qt.Horizontal)
        self.slider_rotation.setRange(0, 360)
        self.slider_rotation.setValue(0)
        self.slider_rotation.setFixedWidth(70)
        self.slider_rotation.setToolTip("Şekli döndür (0°–360°)")
        self.slider_rotation.valueChanged.connect(self._on_rotation_changed)
        bot_row.addWidget(self.slider_rotation)

        self._rotation_label = QLabel("0°")
        self._rotation_label.setFixedWidth(28)
        bot_row.addWidget(self._rotation_label)

        bot_row.addWidget(self._sep())

        # Saydamlık
        opac_lbl = QLabel("Saydamlık")
        opac_lbl.setObjectName("SectionLabel")
        bot_row.addWidget(opac_lbl)
        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setRange(20, 255)
        self.slider_opacity.setValue(150)
        self.slider_opacity.setFixedWidth(60)
        self.slider_opacity.setToolTip("Renk saydamlığı")
        self.slider_opacity.valueChanged.connect(self._update_opacity)
        bot_row.addWidget(self.slider_opacity)

        bot_row.addWidget(self._sep())

        # Geri al
        btn_undo = QPushButton("↩")
        btn_undo.setToolTip("Geri al")
        btn_undo.setFixedSize(32, 32)
        btn_undo.clicked.connect(self._undo)
        bot_row.addWidget(btn_undo)

        # Tümünü temizle
        btn_clear = QPushButton("⊘")
        btn_clear.setFixedSize(32, 32)
        btn_clear.setToolTip("Tümünü temizle")
        btn_clear.setStyleSheet(
            "QPushButton { background-color: #552222; border: 1px solid #773333; "
            "border-radius: 8px; color: #ddd; font-size: 16px; min-height: 0; }"
            "QPushButton:hover { background-color: #773333; border-color: #ff4444; }"
        )
        btn_clear.clicked.connect(self._clear_all)
        bot_row.addWidget(btn_clear)

        main_layout.addLayout(bot_row)
        self.setLayout(main_layout)

    @staticmethod
    def _sep():
        f = QFrame()
        f.setObjectName("Separator")
        f.setFrameShape(QFrame.VLine)
        return f

    # ---- sürükleme (panel taşıma) ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ---- slot'lar ----
    def _on_shape_btn(self, shape_key, checked):
        for key, btn in self._shape_buttons.items():
            if key != shape_key:
                btn.setChecked(False)

        if checked:
            self._draw_mode_active = True
            if self.canvas:
                self.canvas.set_color(self.current_color)
                self.canvas.set_stroke_width(self._get_current_stroke_width())
                self.canvas.set_filled(self.btn_fill.isChecked())
                self.canvas.set_mode("draw", shape_key)
        else:
            self._draw_mode_active = False
            if self.canvas:
                self.canvas.set_mode("select")

    def _quick_add(self):
        shape_type = "rect"
        for key, btn in self._shape_buttons.items():
            if btn.isChecked():
                shape_type = key
                break

        if self.canvas:
            cx = self.canvas.width() / 2 - 80
            cy = self.canvas.height() / 2 - 80
            shape = CanvasShape(shape_type, self.current_color, cx, cy, 160, 160)
            shape.stroke_width = self._get_current_stroke_width()
            shape.filled = self.btn_fill.isChecked()
            self.canvas.add_shape(shape)
            self._deactivate_draw()

    def _toggle_color_popup(self):
        if self._color_popup and self._color_popup.isVisible():
            self._color_popup.close()
            self._color_popup = None
            return

        popup = ViziaColorPicker()
        popup.color_picked.connect(self._on_palette_color)
        popup.adjustSize()

        btn_global = self.btn_color.mapToGlobal(QPoint(0, 0))
        popup.move(
            btn_global.x() - popup.width() // 2 + self.btn_color.width() // 2,
            btn_global.y() - popup.height() - 8,
        )
        popup.show()
        self._color_popup = popup

    def _on_palette_color(self, color):
        alpha = self.slider_opacity.value()
        color.setAlpha(alpha)
        self.current_color = color
        self._update_color_button()
        if self.canvas:
            self.canvas.set_color(color)
            active = self.canvas.active_shape()
            if active:
                active.color = QColor(color)
                self.canvas.update()
        if self._color_popup:
            self._color_popup.close()
            self._color_popup = None

    def _update_color_button(self):
        c = self.current_color
        self.btn_color.setStyleSheet(
            f"QPushButton {{ background-color: {c.name()}; border: 2px solid #888;"
            f" border-radius: 8px; min-height: 0; }}"
            f"QPushButton:hover {{ border-color: #fff; }}"
        )

    def _on_fill_toggled(self, checked):
        self.btn_fill.setText("◼" if checked else "◻")
        if self.canvas:
            self.canvas.set_filled(checked)
            active = self.canvas.active_shape()
            if active:
                active.filled = checked
                self.canvas.update()

    def _on_stroke_width(self, width):
        for w in (1, 3, 6):
            btn = getattr(self, f"_stroke_btn_{w}", None)
            if btn:
                btn.setChecked(w == width)
        if self.canvas:
            self.canvas.set_stroke_width(width)
            active = self.canvas.active_shape()
            if active:
                active.stroke_width = width
                self.canvas.update()

    def _get_current_stroke_width(self):
        for w in (1, 3, 6):
            btn = getattr(self, f"_stroke_btn_{w}", None)
            if btn and btn.isChecked():
                return w
        return 3

    def _on_rotation_changed(self, value):
        self._rotation_label.setText(f"{value}°")
        if self.canvas:
            active = self.canvas.active_shape()
            if active:
                active.rotation = float(value)
                self.canvas.update()

    def _update_opacity(self, value):
        self.current_color.setAlpha(value)
        if self.canvas:
            self.canvas.set_color(self.current_color)
            active = self.canvas.active_shape()
            if active:
                active.color.setAlpha(value)
                self.canvas.update()

    def _undo(self):
        if self.canvas:
            self.canvas.undo()

    def _clear_all(self):
        if self.canvas:
            self.canvas.clear_shapes()

    def _deactivate_draw(self):
        self._draw_mode_active = False
        for btn in self._shape_buttons.values():
            btn.setChecked(False)
        if self.canvas:
            self.canvas.set_mode("select")

    # ---- sinyal slot'ları ----
    def _on_shape_selected(self, shape):
        """Seçili şeklin özelliklerini panele yansıt."""
        self.slider_rotation.blockSignals(True)
        self.slider_rotation.setValue(int(shape.rotation) % 360)
        self.slider_rotation.blockSignals(False)
        self._rotation_label.setText(f"{int(shape.rotation) % 360}°")

        self.btn_fill.blockSignals(True)
        self.btn_fill.setChecked(shape.filled)
        self.btn_fill.setText("◼" if shape.filled else "◻")
        self.btn_fill.blockSignals(False)

        for w in (1, 3, 6):
            btn = getattr(self, f"_stroke_btn_{w}", None)
            if btn:
                btn.setChecked(shape.stroke_width == w)

    def _on_shape_deselected(self):
        pass

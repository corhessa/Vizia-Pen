# plugins/vizia-geometry/toolbox.py
import json
import os
import sys
from collections import deque
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QSlider, QFrame, QMenu,
    QGraphicsDropShadowEffect, QGridLayout,
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
# GLOBAL ASSET ve AYAR YOLU BULUCU
# ---------------------------------------------------------------------------
def get_asset_path(filename):
    """Assets klasöründen dosya yolu bulur."""
    # Plugin klasörü: Vizia/plugins/vizia-geometry/
    # Assets klasörü: Vizia/Assets/
    base_dir = os.path.dirname(os.path.abspath(__file__)) # vizia-geometry
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(base_dir))) # root
    
    # 1. Deneme: Üst dizinlerden Assets'e git
    path = os.path.abspath(os.path.join(base_dir, "../../Assets", filename))
    if os.path.exists(path): return path
    
    # 2. Deneme: sys._MEIPASS (PyInstaller için)
    if hasattr(sys, "_MEIPASS"):
        path = os.path.join(sys._MEIPASS, "Assets", filename)
        if os.path.exists(path): return path
        
    return None

# Ortak Ayarlar Dosyası (Tüm Vizia için tek renk havuzu)
_SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../vizia_settings.json"))

def _load_shared_palette():
    """Tüm uygulamayla ortak renk paletini yükler."""
    try:
        if os.path.exists(_SETTINGS_FILE):
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("custom_colors", [])
    except Exception:
        pass
    return []

def _save_shared_palette(colors):
    """Rengi ortak havuza kaydeder."""
    data = {}
    try:
        if os.path.exists(_SETTINGS_FILE):
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
    except Exception:
        pass
        
    data["custom_colors"] = colors
    try:
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Renk kaydetme hatası: {e}")

# Varsayılan Renkler
_DEFAULT_PALETTE = [
    "#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF",
    "#FFFF00", "#FF00FF", "#00FFFF", "#FF8800", "#8800FF",
    "#FF4444", "#44FF44", "#4444FF", "#FFAA00", "#00AAFF",
    "#AA00FF",
]

# ---------------------------------------------------------------------------
# Shared Color Picker (Vizia Ana Toolbar ile Aynı Mantık)
# ---------------------------------------------------------------------------
class SharedColorPicker(QWidget):
    color_picked = pyqtSignal(QColor)

    _STYLE = """
    QWidget#SharedColorPicker {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #353535, stop:1 #2a2a2a);
        border: 1px solid #444; border-radius: 12px;
    }
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SharedColorPicker")
        self.custom_colors = _load_shared_palette()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True) # Focus çalmaz
        self.setStyleSheet(self._STYLE)
        self._init_ui()
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24); shadow.setOffset(0,4); shadow.setColor(QColor(0,0,0,140))
        self.setGraphicsEffect(shadow)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10); layout.setSpacing(6)

        # Standart Renkler
        lbl = QLabel("Standart"); lbl.setStyleSheet("color:#ccc; font-weight:bold; font-size:11px;")
        layout.addWidget(lbl)
        grid = QGridLayout(); grid.setSpacing(3)
        for i, h in enumerate(_DEFAULT_PALETTE):
            grid.addWidget(self._cbtn(h), i//8, i%8)
        layout.addLayout(grid)

        # Kayıtlı Renkler (Ortak Havuz)
        layout.addWidget(self._sep())
        lbl2 = QLabel("Kayıtlı Renkler"); lbl2.setStyleSheet("color:#999; font-size:10px;")
        layout.addWidget(lbl2)
        
        self.custom_grid = QGridLayout(); self.custom_grid.setSpacing(3)
        self._refresh_custom_grid()
        layout.addLayout(self.custom_grid)

        # Sliderlar
        layout.addWidget(self._sep())
        self.h_slider = self._slider("Ton", 0, 359, 180, "linear-gradient(90deg, red, yellow, lime, cyan, blue, magenta, red)")
        layout.addWidget(self.h_slider)
        self.s_slider = self._slider("Doygunluk", 0, 255, 255, "linear-gradient(90deg, gray, #00aaff)")
        layout.addWidget(self.s_slider)
        self.v_slider = self._slider("Parlaklık", 0, 255, 255, "linear-gradient(90deg, black, white)")
        layout.addWidget(self.v_slider)

        # Alt Butonlar
        bot = QHBoxLayout()
        self.preview = QLabel(); self.preview.setFixedSize(36,36)
        self.preview.setStyleSheet("border-radius:6px; border:1px solid #666;")
        bot.addWidget(self.preview)

        btn_apply = QPushButton("Seç"); btn_apply.clicked.connect(self._apply)
        btn_apply.setStyleSheet("background:#00aaff; color:white; border-radius:6px; font-weight:bold;")
        bot.addWidget(btn_apply)

        btn_save = QPushButton("Kaydet"); btn_save.clicked.connect(self._save)
        btn_save.setStyleSheet("background:#444; color:white; border-radius:6px;")
        bot.addWidget(btn_save)
        layout.addLayout(bot)
        
        self._on_change()

    def _slider(self, name, min_v, max_v, val, bg):
        s = QSlider(Qt.Horizontal); s.setRange(min_v, max_v); s.setValue(val)
        s.setFixedHeight(15)
        s.setStyleSheet(f"QSlider::groove:horizontal {{ height:10px; border-radius:5px; background:{bg}; }} QSlider::handle:horizontal {{ background:white; width:14px; margin:-2px 0; border-radius:7px; border:2px solid #555; }}")
        s.valueChanged.connect(self._on_change)
        return s

    def _cbtn(self, hex_c):
        b = QPushButton(); b.setFixedSize(26,26)
        b.setStyleSheet(f"background-color:{hex_c}; border:1px solid #555; border-radius:4px;")
        b.clicked.connect(lambda: self.color_picked.emit(QColor(hex_c)))
        return b

    def _refresh_custom_grid(self):
        # Temizle
        while self.custom_grid.count():
            item = self.custom_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        # Yeniden Doldur
        for i, h in enumerate(self.custom_colors[:16]):
            self.custom_grid.addWidget(self._cbtn(h), i//8, i%8)

    def _sep(self):
        f = QFrame(); f.setFrameShape(QFrame.HLine); f.setStyleSheet("background:#555;")
        return f

    def _on_change(self):
        c = QColor.fromHsv(self.h_slider.value(), self.s_slider.value(), self.v_slider.value())
        self.preview.setStyleSheet(f"background-color:{c.name()}; border-radius:6px; border:1px solid #666;")

    def _apply(self):
        c = QColor.fromHsv(self.h_slider.value(), self.s_slider.value(), self.v_slider.value())
        self.color_picked.emit(c)

    def _save(self):
        c = QColor.fromHsv(self.h_slider.value(), self.s_slider.value(), self.v_slider.value())
        hex_c = c.name()
        if hex_c not in self.custom_colors:
            self.custom_colors.append(hex_c)
            _save_shared_palette(self.custom_colors)
            self._refresh_custom_grid()

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
            self.setChecked(False) # Sürükleyince seçimi kaldır
            return
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._drag_start = None
        super().mouseReleaseEvent(event)

# ---------------------------------------------------------------------------
# Canvas Overlay
# ---------------------------------------------------------------------------
class ShapeCanvasOverlay(QWidget):
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

    # Sürükle Bırak
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

    # Çizim
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
                draw_shape_path(painter, self._draw_type, inner)
            else:
                painter.drawRect(r)
        painter.end()

    # Mouse
    def mousePressEvent(self, event):
        pos = QPointF(event.pos())
        
        if self._mode == "draw" and event.button() == Qt.LeftButton:
            self._draw_start = pos
            self._draw_rect = QRectF(pos, pos)
            return

        if event.button() == Qt.LeftButton:
            # 1. Önce aktif şeklin tutamaklarına bak (Resize/Rotate)
            if self._active_shape and self._active_shape.selected:
                handle = self._active_shape.handle_at(event.pos()) # global gönder
                if handle is not None:
                    self._push_undo()
                    self._active_shape.start_resize(handle, event.pos())
                    return

            # 2. Sonra herhangi bir şekle tıklandı mı?
            for shape in reversed(self.shapes):
                if shape.contains(event.pos()): # global gönder
                    self._push_undo()
                    self._select(shape)
                    shape.start_move(event.pos())
                    return

            # 3. Hiçbir şeye tıklanmadı -> SEÇİMİ KALDIR
            self._deselect()
            # ÖNEMLİ: event.ignore() demiyoruz ki alttaki pencereye (kalem) geçmesin
            # Eğer kalemle de çizmek istiyorsanız event.ignore() açabilirsiniz ama
            # o zaman boşluğa tıklayınca deselect çalışır + nokta koyar. 
            # Kullanıcı "kalem seçiliyken butonlara basılsın" dedi, canvas'a değil.
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

        # Cursor değiştirme mantığı
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
# ANA ARAÇ ÇUBUĞU
# ---------------------------------------------------------------------------
_TOOLBAR_STYLE = """
QWidget#GeometryToolbar {
    background-color: #2b2b2b; /* Vizia Dolgusu */
    border: 1px solid #444;
    border-radius: 12px;
}
QPushButton, QToolButton {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 4px;
    color: #ddd;
    font-weight: bold;
    font-size: 11px;
}
QPushButton:hover, QToolButton:hover { background-color: #505050; border-color: #00aaff; }
QPushButton:pressed, QToolButton:pressed { background-color: #00aaff; color: white; }
QPushButton:checked, QToolButton:checked { background-color: #00aaff; color: white; border-color: #0088cc; }
QLabel { color: #aaa; font-size: 10px; background: transparent; }
QSlider::groove:horizontal { border: 1px solid #555; height: 6px; background: #3e3e3e; border-radius: 3px; }
QSlider::handle:horizontal { background: #00aaff; width: 14px; margin: -4px 0; border-radius: 7px; }
QFrame#Separator { background-color: #555; max-width: 1px; margin: 4px 2px; }
"""

class GeometryToolbox(QWidget):
    def __init__(self, canvas_overlay):
        super().__init__()
        self.canvas = canvas_overlay
        self.current_color = QColor(0, 255, 255, 150)
        self._shape_buttons = {}
        self._color_popup = None
        self._drag_pos = None

        # Arayüzü Başlat
        self.setObjectName("GeometryToolbar")
        # Kalem modunda tıklanabilmesi için flag ayarı:
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # WA_ShowWithoutActivating -> Focus çalmaz ama tıklamayı alır
        self.setAttribute(Qt.WA_ShowWithoutActivating, True) 
        self.setStyleSheet(_TOOLBAR_STYLE)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24); shadow.setOffset(0, 4); shadow.setColor(QColor(0,0,0,120))
        self.setGraphicsEffect(shadow)

        self._init_ui()
        
        if self.canvas:
            self.canvas.shape_selected.connect(self._on_shape_selected)

    def _init_ui(self):
        main = QVBoxLayout(self); main.setContentsMargins(10, 6, 10, 6); main.setSpacing(4)
        
        # --- ÜST SATIR ---
        top = QHBoxLayout(); top.setSpacing(3)
        drag = QLabel("☰"); drag.setFixedWidth(18); drag.setAlignment(Qt.AlignCenter)
        top.addWidget(drag); top.addWidget(self._sep())

        shapes = [("rect","Kare"), ("circle","Daire"), ("triangle","Üçgen"), ("star","Yıldız"), ("arrow","Ok"), ("note","Not"), ("line","Çizgi")]
        for k, t in shapes:
            btn = DraggableShapeButton(k, t) # Sürükle bırak özelliği burada
            btn.clicked.connect(lambda c, x=k: self._on_shape_btn(x, c))
            top.addWidget(btn); self._shape_buttons[k] = btn
        
        main.addLayout(top)
        
        # --- ALT SATIR ---
        bot = QHBoxLayout(); bot.setSpacing(3)
        
        # Renk (Ortak Palet)
        self.btn_color = QPushButton(); self.btn_color.setFixedSize(32, 32)
        self._update_color_button()
        self.btn_color.clicked.connect(self._toggle_color_popup)
        bot.addWidget(self.btn_color)

        # Dolgu
        self.btn_fill = QPushButton("◼"); self.btn_fill.setFixedSize(32, 32)
        self.btn_fill.setCheckable(True); self.btn_fill.setChecked(True)
        self.btn_fill.toggled.connect(lambda c: self.canvas.set_filled(c) if self.canvas else None)
        bot.addWidget(self.btn_fill)
        bot.addWidget(self._sep())

        # Kalınlık (Kutu sorunu düzeltildi: Sabit genişlik + ikonik yazı)
        for w, l in [(1,"İnce"), (3,"Orta"), (6,"Kalın")]:
            b = QPushButton(l); b.setFixedSize(45, 28) # Genişlik artırıldı
            b.setCheckable(True); b.setFont(QFont("Arial", 9))
            if w==3: b.setChecked(True)
            b.clicked.connect(lambda c, x=w: self._on_stroke_width(x))
            setattr(self, f"_stroke_btn_{w}", b)
            bot.addWidget(b)
        
        bot.addWidget(self._sep())

        # Döndürme
        sl = QSlider(Qt.Horizontal); sl.setRange(0, 360); sl.setFixedWidth(70)
        sl.valueChanged.connect(self._on_rot); self.slider_rot = sl
        bot.addWidget(sl)

        bot.addWidget(self._sep())

        # Geri Al (İkonlu)
        undo_path = get_asset_path("undo.png")
        btn_undo = QPushButton(); btn_undo.setFixedSize(32, 32)
        if undo_path: btn_undo.setIcon(QIcon(undo_path)); btn_undo.setIconSize(QSize(20,20))
        else: btn_undo.setText("↩")
        btn_undo.clicked.connect(lambda: self.canvas.undo() if self.canvas else None)
        bot.addWidget(btn_undo)

        # Sil (İkonlu)
        bin_path = get_asset_path("bin.png")
        btn_clear = QPushButton(); btn_clear.setFixedSize(32, 32)
        if bin_path: btn_clear.setIcon(QIcon(bin_path)); btn_clear.setIconSize(QSize(20,20))
        else: btn_clear.setText("🗑")
        btn_clear.clicked.connect(lambda: self.canvas.clear_shapes() if self.canvas else None)
        bot.addWidget(btn_clear)

        main.addLayout(bot)
        self.setLayout(main)

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
        if self._color_popup and self._color_popup.isVisible():
            self._color_popup.close(); self._color_popup = None
            return
        self._color_popup = SharedColorPicker()
        self._color_popup.color_picked.connect(self._on_color_picked)
        gp = self.btn_color.mapToGlobal(QPoint(0,0))
        self._color_popup.move(gp.x(), gp.y() - self._color_popup.height() - 10)
        self._color_popup.show()

    def _on_color_picked(self, c):
        self.current_color = c
        self._update_color_button()
        if self.canvas:
            self.canvas.set_color(c)
            if self.canvas.active_shape(): 
                self.canvas.active_shape().color = c
                self.canvas.update()
        if self._color_popup: self._color_popup.close(); self._color_popup = None

    def _update_color_button(self):
        self.btn_color.setStyleSheet(f"background-color:{self.current_color.name()}; border:2px solid #888; border-radius:8px;")

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
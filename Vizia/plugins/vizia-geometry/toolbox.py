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
    from shapes import GeometryShape, draw_shape_path # Güncellenen sınıfı import et
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from shapes import GeometryShape, draw_shape_path

# Ana projenin 'ui' klasörüne erişim sağla
vizia_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if vizia_root not in sys.path:
    sys.path.insert(0, vizia_root)

try:
    from ui.widgets.color_picker import ModernColorPicker
except ImportError:
    ModernColorPicker = None

# ---------------------------------------------------------------------------
# GLOBAL ASSET YOLU BULUCU (KORUNDU)
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
# Şekil İkonu Oluşturucu (KORUNDU)
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
# Sürükle-Bırak Butonu (KORUNDU)
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
# Stil Tanımları (CSS) - KORUNDU
# ---------------------------------------------------------------------------
_TOOLBAR_STYLE = """
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
QSlider::groove:horizontal { background: #3a3a3c; height: 4px; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #555555; border-radius: 2px; }
QSlider::handle:horizontal { background: #b0b0b0; border: none; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
QSlider::handle:horizontal:hover { background: #ffffff; }
QFrame#Separator { background-color: #48484a; max-width: 1px; margin: 4px 2px; border:none; }
"""

class GeometryToolbox(QWidget):
    def __init__(self, main_overlay):
        super().__init__()
        # Artık doğrudan main_overlay ile çalışıyoruz
        self.main_overlay = main_overlay 
        self.current_color = QColor(0, 255, 255, 150)
        self._shape_buttons = {}
        self._drag_pos = None
        self.active_shape_widget = None # O an seçili şekil widget'ı

        self.custom_color_index = 0 

        self.setObjectName("GeometryToolbar")
        # Goal 3: Z-Order (Hep önde)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._init_ui()
        
        shadow = QGraphicsDropShadowEffect(self.content_frame)
        shadow.setBlurRadius(24); shadow.setOffset(0, 4); shadow.setColor(QColor(0,0,0,120))
        self.content_frame.setGraphicsEffect(shadow)

    def _init_ui(self):
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)

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
        
        self.btn_color = QPushButton(); self.btn_color.setFixedSize(32, 32)
        self._update_color_button()
        self.btn_color.clicked.connect(self._toggle_color_popup)
        bot.addWidget(self.btn_color)

        # Goal 1: Dolgu Butonu Fix
        self.btn_fill = QPushButton("◼"); self.btn_fill.setFixedSize(32, 32)
        self.btn_fill.setCheckable(True); self.btn_fill.setChecked(True)
        self.btn_fill.toggled.connect(self._on_fill_toggled)
        bot.addWidget(self.btn_fill)
        bot.addWidget(self._sep())

        for w, l in [(1,"İnce"), (3,"Orta"), (6,"Kalın")]:
            b = QPushButton(l); b.setFixedSize(45, 28)
            b.setCheckable(True); b.setFont(QFont("Arial", 9))
            if w==3: b.setChecked(True)
            b.clicked.connect(lambda c, x=w: self._on_stroke_width(x))
            setattr(self, f"_stroke_btn_{w}", b)
            bot.addWidget(b)
        
        bot.addWidget(self._sep())

        lbl_rot = QLabel("Döndür:"); lbl_rot.setStyleSheet("margin-right: 2px;")
        bot.addWidget(lbl_rot)
        sl = QSlider(Qt.Horizontal); sl.setRange(0, 360); sl.setFixedWidth(70)
        sl.valueChanged.connect(self._on_rot); self.slider_rot = sl
        bot.addWidget(sl)
        bot.addWidget(self._sep())

        # Undo / Clear (Artık Main Overlay'i kontrol ediyor)
        undo_path = get_asset_path("undo.png")
        btn_undo = QPushButton(); btn_undo.setFixedSize(32, 32)
        if undo_path: btn_undo.setIcon(QIcon(undo_path)); btn_undo.setIconSize(QSize(20,20))
        else: btn_undo.setText("↩")
        btn_undo.clicked.connect(lambda: self.main_overlay.undo() if self.main_overlay else None)
        bot.addWidget(btn_undo)

        bin_path = get_asset_path("bin.png")
        btn_clear = QPushButton(); btn_clear.setFixedSize(32, 32)
        if bin_path: btn_clear.setIcon(QIcon(bin_path)); btn_clear.setIconSize(QSize(20,20))
        else: btn_clear.setText("🗑")
        btn_clear.clicked.connect(lambda: self.main_overlay.clear_all() if self.main_overlay else None)
        bot.addWidget(btn_clear)

        main.addLayout(bot)

    def _sep(self): f=QFrame(); f.setFrameShape(QFrame.VLine); f.setObjectName("Separator"); return f

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.LeftButton: self.move(e.globalPos() - self._drag_pos)

    # --- İŞLEVLER ---

    def _on_shape_btn(self, shape_type, checked):
        # Diğer butonları kapat
        for key, b in self._shape_buttons.items(): 
            if key != shape_type: b.setChecked(False)
            
        if checked:
            # Yeni Şekil Oluştur (Goal 2 & 5)
            # Şekli main_overlay üzerinden ekliyoruz
            self._create_shape_widget(shape_type)
            # Seçimi kaldır (Buton sadece oluşturucu olarak kalsın, basılı kalmasın)
            self._shape_buttons[shape_type].setChecked(False)

    def _create_shape_widget(self, shape_type):
        if not self.main_overlay: return
        
        # Şekil widget'ını oluştur
        # Parent olarak overlay'i veriyoruz ama add_widget_item onu yöneticek
        new_shape = GeometryShape(
            self.main_overlay, 
            shape_type, 
            self.current_color
        )
        
        # Dolgu durumunu uygula
        new_shape.update_fill(self.btn_fill.isChecked())
        
        # Ekranın ortasına yerleştir
        center = self.main_overlay.rect().center()
        new_shape.move(center.x() - 100, center.y() - 100)
        
        # Goal 5: Undo sistemine dahil et (CanvasLayer'a ekle)
        # 1. Widget olarak listeye alınıyor
        # 2. History'ye "shape" tipinde ekleniyor
        # 3. Layer'a (Desktop/Board) bağlı kalıyor
        self.main_overlay.active_layer.add_widget_item(new_shape, 'shape')
        new_shape.show()
        
        # Sinyal Bağla: Şekle tıklanınca Toolbox bilsin
        new_shape.clicked.connect(self._on_shape_clicked)
        
        # Otomatik seç
        self._select_shape(new_shape)

    def _select_shape(self, shape):
        # Önceki seçimi kaldır
        if self.active_shape_widget:
            self.active_shape_widget.set_selected(False)
            
        self.active_shape_widget = shape
        shape.set_selected(True)
        
        # UI Güncelle
        self.slider_rot.blockSignals(True)
        self.slider_rot.setValue(int(shape.rotation_angle) % 360)
        self.slider_rot.blockSignals(False)
        self.btn_fill.setChecked(shape.filled)

    def _on_shape_clicked(self, shape_obj):
        self._select_shape(shape_obj)

    def on_canvas_click(self):
        """Goal 4: Boşluğa tıklayınca seçim kalksın ve kalem aktif olsun"""
        if self.active_shape_widget:
            self.active_shape_widget.set_selected(False)
            self.active_shape_widget = None
        
        # Kalem modunu garantiye al (Main overlay zaten canvas click'te bunu yapar ama burada UI resetleyebiliriz)
        for b in self._shape_buttons.values(): b.setChecked(False)

    def _on_fill_toggled(self, checked):
        # Goal 1: Dolgu değişimini aktif şekle uygula
        if self.active_shape_widget:
            self.active_shape_widget.update_fill(checked)

    def _on_rot(self, v):
        if self.active_shape_widget:
            self.active_shape_widget.rotation_angle = float(v)
            self.active_shape_widget.update()

    def _on_stroke_width(self, w):
        for x in [1,3,6]: getattr(self, f"_stroke_btn_{x}").setChecked(x==w)
        if self.active_shape_widget:
            self.active_shape_widget.stroke_width = w
            self.active_shape_widget.update()

    def _toggle_color_popup(self):
        if not self.main_overlay: return
        if not ModernColorPicker: 
            QMessageBox.warning(self, "Hata", "Renk seçici yüklenemedi.")
            return

        custom_colors = self.main_overlay.settings.get("custom_colors")
        picker = ModernColorPicker(self.current_color, custom_colors, self.main_overlay.settings, self)
        if picker.exec_():
            self._on_color_picked(picker.selected_color)
            
    def _on_color_picked(self, c):
        self.current_color = c
        self._update_color_button()
        if self.active_shape_widget:
            self.active_shape_widget.primary_color = c
            self.active_shape_widget.update()

    def _update_color_button(self):
        self.btn_color.setStyleSheet(f"background-color:{self.current_color.name()}; border:2px solid #888; border-radius:8px;")
        
    def update_color_btn_style(self):
        self._update_color_button()
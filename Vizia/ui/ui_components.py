# ui/ui_components.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, 
                             QGridLayout, QGraphicsOpacityEffect, QSlider, QApplication, QSizeGrip, QFrame)
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QPixmap, QIcon, QCursor
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtSignal, QSize

# --- RESİM NESNESİ (Aynı kalıyor) ---
class ViziaImageItem(QWidget):
    request_close = pyqtSignal(QWidget)
    request_stamp = pyqtSignal(QWidget)
    
    def __init__(self, image_path, creation_mode, parent=None):
        super().__init__(parent)
        self.creation_mode = creation_mode
        self.setWindowFlags(Qt.SubWindow)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("background: transparent;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.control_frame = QFrame()
        self.control_frame.setFixedHeight(32)
        self.control_frame.setStyleSheet("QFrame { background-color: #1c1c1e; border-top-left-radius: 10px; border-top-right-radius: 10px; border: 1px solid #3a3a3c; }")
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
        self.control_layout.addWidget(create_btn("▲", "Öne", self.raise_))
        self.control_layout.addWidget(create_btn("▼", "Arka", self.lower))
        self.control_layout.addStretch()
        self.control_layout.addWidget(create_btn("✕", "Kapat", self.close, "#ff3b30"))
        
        self.layout.addWidget(self.control_frame)
        self.control_frame.hide()
        
        self.image_container = QLabel()
        self.original_pixmap = QPixmap(image_path)
        self.image_container.setPixmap(self.original_pixmap)
        self.image_container.setScaledContents(True)
        self.layout.addWidget(self.image_container)
        
        self.grip = QSizeGrip(self)
        self.old_pos = None
        w, h = self.original_pixmap.width(), self.original_pixmap.height()
        if w > 400: h = int(h * (400/w)); w = 400
        self.resize(w, h + 32)
        self.show()

    def resizeEvent(self, event):
        self.grip.move(self.width() - 20, self.height() - 20)
        super().resizeEvent(event)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.grip.geometry().contains(event.pos()):
            self.old_pos = event.pos(); self.raise_()
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self.old_pos: self.move(self.pos() + (event.pos() - self.old_pos))
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event): self.old_pos = None; super().mouseReleaseEvent(event)
    def enterEvent(self, event): self.control_frame.show(); self.image_container.setStyleSheet("border: 1px solid #007aff;"); super().enterEvent(event)
    def leaveEvent(self, event): self.control_frame.hide(); self.image_container.setStyleSheet("border: none;"); super().leaveEvent(event)
    def closeEvent(self, event): self.request_close.emit(self); super().closeEvent(event)

# --- NOTIFICATION (Aynı) ---
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
        screen_geo = QApplication.primaryScreen().geometry()
        self.target_y = int(screen_geo.height() * 0.12)
        self.target_x = (screen_geo.width() - self.width()) // 2
        self.move(self.target_x, self.target_y)
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

# --- RENK SEÇİCİ (ESKİ HALİNE DÖNDÜRÜLDÜ + SETTINGS ENTEGRASYONU) ---
class ModernColorPicker(QDialog):
    def __init__(self, initial_color, persistent_colors, settings_manager, parent_widget):
        super().__init__(parent_widget)
        self.selected_color = initial_color
        self.persistent_colors = persistent_colors
        self.settings_manager = settings_manager # Ayar Yöneticisi eklendi
        self.parent_context = parent_widget 
        self.hue = initial_color.hue() if initial_color.hue() != -1 else 0
        self.sat = initial_color.saturation()
        self.val = initial_color.value()
        self.custom_chips = []
        self.setWindowTitle("Renk Seç")
        self.setFixedSize(520, 360)
        self.setStyleSheet("""
            QDialog { background-color: #1c1c1e; color: white; }
            QLabel { color: #ebebeb; font-size: 12px; font-weight: bold; }
            QPushButton#ActionBtn { background-color: #2c2c2e; border: 1px solid #3a3a3c; border-radius: 6px; padding: 8px; color: white; font-size: 11px; }
            QPushButton#ActionBtn:hover { background-color: #3a3a40; border: 1px solid #007aff; }
            QPushButton#ToolBtn { background-color: #2c2c2e; border: 1.5px solid #3a3a3c; border-radius: 6px; font-size: 16px; }
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
        line.setStyleSheet("background-color: #3a3a3c; margin: 10px 0;")
        left_panel.addWidget(line)
        
        left_panel.addWidget(QLabel("Özel Renkler"))
        self.custom_grid = QGridLayout()
        for i in range(10):
            color_hex = self.persistent_colors[i]
            chip = self.create_color_chip(color_hex, empty=(color_hex == "#2c2c2e"))
            self.custom_chips.append(chip)
            self.custom_grid.addWidget(chip, i // 5, i % 5)
        left_panel.addLayout(self.custom_grid)
        
        left_panel.addStretch()
        
        # --- BUTONLAR (Ekle ve Sil) ---
        bottom_left_btns = QHBoxLayout()
        self.add_btn = QPushButton("Palete Ekle"); self.add_btn.setObjectName("ActionBtn")
        self.add_btn.clicked.connect(self.add_to_custom)
        
        self.trash_btn = QPushButton("🗑️"); self.trash_btn.setFixedSize(35, 35); self.trash_btn.setObjectName("ToolBtn")
        self.trash_btn.clicked.connect(self.reset_custom)
        
        bottom_left_btns.addWidget(self.add_btn)
        bottom_left_btns.addWidget(self.trash_btn)
        left_panel.addLayout(bottom_left_btns)
        
        main_layout.addLayout(left_panel)
        
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

    def create_color_chip(self, color_hex, empty=False):
        btn = QPushButton(); btn.setFixedSize(28, 28); btn.setCursor(Qt.PointingHandCursor)
        border = "#3a3a3c" if empty else "#007aff"
        btn.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px; border: 1.5px solid {border};")
        if not empty: btn.clicked.connect(lambda: self.set_direct_color(QColor(color_hex)))
        return btn

    def get_toolbar(self):
        # Toolbar'a ulaşmak için güvenli yol
        if hasattr(self.parent_context, 'overlay') and hasattr(self.parent_context.overlay, 'toolbar'):
            return self.parent_context.overlay.toolbar
        if hasattr(self.parent_context, 'toolbar'):
            return self.parent_context.toolbar
        return self.parent_context

    def add_to_custom(self):
        toolbar = self.get_toolbar()
        if toolbar:
            idx = toolbar.custom_color_index
            color_hex = self.selected_color.name()
            
            # Bellekte güncelle
            self.persistent_colors[idx] = color_hex
            
            # UI güncelle
            chip = self.custom_chips[idx]
            chip.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px; border: 1.5px solid #007aff;")
            try: chip.clicked.disconnect()
            except: pass
            chip.clicked.connect(lambda _, c=color_hex: self.set_direct_color(QColor(c)))
            
            toolbar.custom_color_index = (idx + 1) % 10
            
            # AYARLARA KAYDET
            if self.settings_manager:
                self.settings_manager.set("custom_colors", self.persistent_colors)

    def reset_custom(self):
        toolbar = self.get_toolbar()
        for i in range(10):
            # Bellekte güncelle
            self.persistent_colors[i] = "#2c2c2e"
            
            # UI güncelle
            chip = self.custom_chips[i]
            chip.setStyleSheet("background-color: #2c2c2e; border-radius: 4px; border: 1.5px solid #3a3a3c;")
            try: chip.clicked.disconnect()
            except: pass
            
        if toolbar: toolbar.custom_color_index = 0
        
        # AYARLARA KAYDET (Reset işlemi)
        if self.settings_manager:
            self.settings_manager.set("custom_colors", self.persistent_colors)

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
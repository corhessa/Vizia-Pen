from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, 
                             QFrame, QPushButton, QSlider, QWidget)
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, pyqtSignal, QPoint

class ModernColorPicker(QDialog):
    def __init__(self, initial_color, persistent_colors, settings_manager, parent_widget):
        super().__init__(parent_widget)
        self.selected_color = initial_color
        self.persistent_colors = persistent_colors
        self.settings_manager = settings_manager 
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
        # Güvenli lambda bağlaması
        if not empty: btn.clicked.connect(lambda checked=False, c=color_hex: self.set_direct_color(QColor(c)))
        return btn

    def get_toolbar(self):
        if hasattr(self.parent_context, 'overlay') and hasattr(self.parent_context.overlay, 'toolbar'):
            return self.parent_context.overlay.toolbar
        if hasattr(self.parent_context, 'toolbar'):
            return self.parent_context.toolbar
        return self.parent_context

    def add_to_custom(self):
        color_hex = self.selected_color.name()
        empty_color = "#2c2c2e"
        
        # 1. Aynı renk zaten paletimizde varsa tekrar ekleme
        if color_hex in self.persistent_colors:
            return 
            
        # 2. İlk boş slotu bul
        target_idx = -1
        for i in range(10):
            if self.persistent_colors[i] == empty_color:
                target_idx = i
                break
                
        # 3. Eğer boş slot varsa oraya koy, yoksa FIFO (kuyruk) yap
        if target_idx != -1:
            self.persistent_colors[target_idx] = color_hex
        else:
            self.persistent_colors.pop(0)  # En eskisini sil
            self.persistent_colors.append(color_hex)  # Yeni olanı sona ekle
            
        # 4. Arayüzü baştan çizmeden sadece butonların stilini ve işlevini güncelle
        for i in range(10):
            chip = self.custom_chips[i]
            c_hex = self.persistent_colors[i]
            
            try: chip.clicked.disconnect()
            except: pass
            
            if c_hex == empty_color:
                chip.setStyleSheet("background-color: #2c2c2e; border-radius: 4px; border: 1.5px solid #3a3a3c;")
            else:
                chip.setStyleSheet(f"background-color: {c_hex}; border-radius: 4px; border: 1.5px solid #007aff;")
                chip.clicked.connect(lambda checked=False, c=c_hex: self.set_direct_color(QColor(c)))

        # 5. Ayarları kaydet
        if self.settings_manager:
            self.settings_manager.set("custom_colors", self.persistent_colors)

    def reset_custom(self):
        empty_color = "#2c2c2e"
        for i in range(10):
            self.persistent_colors[i] = empty_color
            chip = self.custom_chips[i]
            chip.setStyleSheet("background-color: #2c2c2e; border-radius: 4px; border: 1.5px solid #3a3a3c;")
            try: chip.clicked.disconnect()
            except: pass
            
        # Sıfırlama işleminden sonra ayarları kaydet
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
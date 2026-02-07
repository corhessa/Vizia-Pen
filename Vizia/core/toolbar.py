# core/toolbar.py

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, 
                             QLabel, QFrame, QApplication, QGraphicsOpacityEffect)
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint

from ui.ui_components import ModernColorPicker
from ui.styles import TOOLBAR_STYLESHEET, get_color_btn_style

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- EK ARAÇLAR (DRAWER) ---
class ExtensionDrawer(QWidget):
    def __init__(self, parent_toolbar):
        super().__init__(None) # Bağımsız pencere
        self.toolbar_ref = parent_toolbar
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_open = False
        self.target_width = 60
        self.resize(0, 0)
        
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame { background-color: #1c1c1e; border: 1.5px solid #3a3a3c; border-radius: 15px; }
            QPushButton { background-color: transparent; border: none; border-radius: 8px; padding: 5px; }
            QPushButton:hover { background-color: #3a3a40; border: 1px solid #007aff; }
        """)
        
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(8)
        
        # Dosya Butonu
        self.btn_folder = self.create_drawer_btn("add-folder.png", "Görsel Yükle", self.action_load_image)
        self.layout.addWidget(self.btn_folder)
        
        # Geometri Butonu
        self.btn_geometry = self.create_drawer_btn("geometry.png", "Geometri Araçları", self.action_geometry)
        self.layout.addWidget(self.btn_geometry)
        
        self.layout.addStretch()
        
        self.anim = QPropertyAnimation(self, b"size")
        self.anim.setEasingCurve(QEasingCurve.OutExpo)
        self.anim.setDuration(300)

    def create_drawer_btn(self, icon_name, tooltip, func):
        btn = QPushButton()
        icon_path = resource_path(f"Vizia/Assets/{icon_name}")
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path)); btn.setIconSize(QSize(24, 24))
        else:
            btn.setText(tooltip[0]); btn.setStyleSheet("color: white; font-weight: bold;")
        
        btn.setFixedSize(40, 40)
        btn.setToolTip(tooltip)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.clicked.connect(lambda: self.handle_click_sequence(func))
        return btn

    def handle_click_sequence(self, func):
        if func: func()
        # force_focus KALDIRILDI -> Artık butonlar aktif kalıyor.

    def action_load_image(self):
        if hasattr(self.toolbar_ref, 'overlay'):
            self.toolbar_ref.overlay.open_image_loader()

    def action_geometry(self):
        if hasattr(self.toolbar_ref, 'overlay'):
            self.toolbar_ref.overlay.show_toast("Geometri Araçları (Yakında)")

    def update_position(self):
        if not self.isVisible(): return
        self.raise_() 
        tb_geo = self.toolbar_ref.geometry()
        target_x = tb_geo.x() + tb_geo.width() + 5 
        strip_btn = self.toolbar_ref.strip_btn
        strip_global_pos = strip_btn.mapToGlobal(QPoint(0,0))
        target_y = strip_global_pos.y() + (strip_btn.height() // 2) - (self.height() // 2)
        self.move(target_x, target_y)

    def toggle(self):
        self.anim.stop()
        content_height = self.layout.sizeHint().height() + 20
        
        if not self.is_open:
            self.is_open = True
            self.show()
            self.raise_()
            self.container.resize(self.target_width, content_height)
            self.resize(0, content_height)
            self.update_position()
            self.anim.setStartValue(QSize(0, content_height))
            self.anim.setEndValue(QSize(self.target_width, content_height))
            self.anim.start()
        else:
            self.is_open = False
            self.anim.setStartValue(self.size())
            self.anim.setEndValue(QSize(0, content_height))
            self.anim.finished.connect(self._on_close_finished)
            self.anim.start()

    def _on_close_finished(self):
        if not self.is_open:
            self.hide()
            try: self.anim.finished.disconnect(self._on_close_finished)
            except: pass

# --- ANA TOOLBAR (Standart) ---
class ModernToolbar(QWidget):
    def __init__(self, overlay):
        super().__init__(overlay)
        self.overlay = overlay
        self.old_pos = None
        self.custom_colors = ["#2c2c2e"] * 10 
        self.custom_color_index = 0
        self.last_active_tool = "pen"
        
        self.drawer = ExtensionDrawer(self)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setFixedWidth(95); self.setFixedHeight(640) 
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.content_frame = QFrame(); self.content_frame.setFixedWidth(75)
        self.content_frame.setStyleSheet(TOOLBAR_STYLESHEET) 
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(10, 15, 10, 15); layout.setSpacing(8)

        logo_path = resource_path("Vizia/Assets/VIZIA.ico")
        logo_label = QLabel(); logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull(): logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else: logo_label.setText("V")
        logo_label.setAlignment(Qt.AlignCenter); layout.addWidget(logo_label); layout.addSpacing(5)

        self.btn_draw = self.create_btn("pencil.png", lambda: self.safe_change("pen", self.btn_draw), "Kalem")
        layout.addWidget(self.btn_draw, 0, Qt.AlignCenter)
        self.btn_eraser = self.create_btn("eraser.png", lambda: self.safe_change("eraser", self.btn_eraser), "Silgi")
        layout.addWidget(self.btn_eraser, 0, Qt.AlignCenter)
        self.btn_text = self.create_btn("size.png", self.overlay.add_text, "Metin Ekle")
        layout.addWidget(self.btn_text, 0, Qt.AlignCenter)
        self.btn_board = self.create_btn("blackboard.png", self.toggle_board, "Beyaz Tahta / Masaüstü")
        self.btn_board.setProperty("state", "red"); layout.addWidget(self.btn_board, 0, Qt.AlignCenter)
        self.btn_move = self.create_btn("mouse.png", lambda: self.safe_change("move", self.btn_move), "Taşıma Modu")
        layout.addWidget(self.btn_move, 0, Qt.AlignCenter)
        
        layout.addSpacing(2); line = QFrame(); line.setFixedHeight(1); line.setFixedWidth(40)
        line.setStyleSheet("background-color: #48484a; border: none;"); layout.addWidget(line, 0, Qt.AlignCenter); layout.addSpacing(2)
        
        self.btn_undo = self.create_btn("undo.png", self.overlay.undo, "Geri Al"); layout.addWidget(self.btn_undo, 0, Qt.AlignCenter)
        self.btn_clear = self.create_btn("bin.png", self.overlay.clear_all, "Hepsini Temizle"); layout.addWidget(self.btn_clear, 0, Qt.AlignCenter)
        self.btn_shot = self.create_btn("dslr-camera.png", self.overlay.take_screenshot, "Ekran Görüntüsü Al"); self.btn_shot.setObjectName("btn_shot"); layout.addWidget(self.btn_shot, 0, Qt.AlignCenter)
        
        self.btn_color = QPushButton("⬤"); self.btn_color.setToolTip("Renk Seç"); self.btn_color.setFocusPolicy(Qt.NoFocus)
        self.btn_color.clicked.connect(self.select_color); self.btn_color.setFixedSize(40, 40)
        self.update_color_btn_style(); layout.addWidget(self.btn_color, 0, Qt.AlignCenter)
        
        size_box = QFrame(); size_box.setFixedHeight(75); size_box.setStyleSheet("background: transparent; border: none;")
        size_layout = QVBoxLayout(size_box); size_layout.setContentsMargins(0, 0, 0, 0); size_layout.setSpacing(2) 
        lbl_size = QLabel("BOYUT"); lbl_size.setAlignment(Qt.AlignCenter); lbl_size.setStyleSheet("font-size: 10px; font-weight: 800; color: #ffffff; letter-spacing: 1px;"); size_layout.addWidget(lbl_size)
        self.slider = QSlider(Qt.Horizontal); self.slider.setRange(2, 100); self.slider.setValue(4); self.slider.setFixedWidth(54); self.slider.valueChanged.connect(self.update_brush_size); size_layout.addWidget(self.slider, 0, Qt.AlignCenter)
        self.lbl_percent = QLabel("4%"); self.lbl_percent.setAlignment(Qt.AlignCenter); self.lbl_percent.setStyleSheet("font-size: 11px; color: #0a84ff; font-weight: bold;"); size_layout.addWidget(self.lbl_percent)
        layout.addWidget(size_box, 0, Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(self.create_btn("gear.png", lambda: None, "Ayarlar"), 0, Qt.AlignCenter)
        layout.addWidget(self.create_btn("info.png", self.show_about, "Hakkında"), 0, Qt.AlignCenter)
        btn_close = self.create_btn("close.png", QApplication.quit, "Çıkış"); btn_close.setProperty("state", "red"); layout.addWidget(btn_close, 0, Qt.AlignCenter)
        self.btn_draw.setProperty("active", True)
        
        self.strip_container = QWidget(); self.strip_container.setFixedWidth(20) 
        strip_layout = QVBoxLayout(self.strip_container); strip_layout.setContentsMargins(0, 0, 0, 0); strip_layout.setSpacing(0); strip_layout.addStretch()
        self.strip_btn = QPushButton(); self.strip_btn.setFixedSize(12, 120); self.strip_btn.setCursor(Qt.PointingHandCursor); self.strip_btn.clicked.connect(self.toggle_drawer); self.strip_btn.setToolTip("Ek Araçlar")
        self.strip_btn.setStyleSheet("QPushButton { background-color: #1c1c1e; border: 1.5px solid #3a3a3c; border-left: none; border-top-right-radius: 10px; border-bottom-right-radius: 10px; } QPushButton:hover { background-color: #2c2c2e; border-color: #007aff; }")
        strip_layout.addWidget(self.strip_btn); strip_layout.addStretch()
        
        self.main_layout.addWidget(self.content_frame); self.main_layout.addWidget(self.strip_container)

    def create_btn(self, icon_file, slot, tooltip_text=""):
        btn = QPushButton()
        icon_path = resource_path(f"Vizia/Assets/{icon_file}")
        if os.path.exists(icon_path): btn.setIcon(QIcon(icon_path)); btn.setIconSize(QSize(24, 24)) 
        else: btn.setText(tooltip_text[0] if tooltip_text else "?")
        btn.clicked.connect(slot); btn.setFocusPolicy(Qt.NoFocus); btn.setFixedSize(40, 40)
        if tooltip_text: btn.setToolTip(tooltip_text)
        return btn

    def toggle_drawer(self): self.drawer.toggle()
    def show_about(self): from ui.dialogs import AboutDialog; AboutDialog(self).exec_()
    def select_color(self):
        picker = ModernColorPicker(self.overlay.current_color, self.custom_colors, self.overlay)
        if picker.exec_(): color = picker.selected_color; self.overlay.current_color = color; self.update_color_btn_style()
        QTimer.singleShot(10, self.overlay.force_focus)
    def update_color_btn_style(self): self.btn_color.setStyleSheet(get_color_btn_style(self.overlay.current_color.name()))
    def update_brush_size(self, val): self.overlay.brush_size = val; self.lbl_percent.setText(f"{val}%")
    def toggle_board(self):
        self.overlay.whiteboard_mode = not self.overlay.whiteboard_mode
        self.btn_board.setProperty("state", "green" if self.overlay.whiteboard_mode else "red")
        self.btn_board.style().unpolish(self.btn_board); self.btn_board.style().polish(self.btn_board)
        self.overlay.redraw_canvas(); QTimer.singleShot(10, self.overlay.force_focus)
    def toggle_move_mode(self):
        if self.overlay.drawing_mode != "move": self.last_active_tool = self.overlay.drawing_mode; self.safe_change("move", self.btn_move)
        else: target_btn = self.btn_draw if self.last_active_tool == "pen" else self.btn_eraser; self.safe_change(self.last_active_tool, target_btn)
    def safe_change(self, mode, button):
        self.overlay.drawing_mode = mode
        for b in [self.btn_draw, self.btn_move, self.btn_eraser]: b.setProperty("active", False); b.style().unpolish(b); b.style().polish(b)   
        button.setProperty("active", True); button.style().unpolish(button); button.style().polish(button)
        self.overlay.setWindowFlag(Qt.WindowTransparentForInput, mode == "move"); self.overlay.show(); QTimer.singleShot(10, self.overlay.force_focus)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos; self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPos()
            if self.drawer.isVisible() and self.drawer.is_open: self.drawer.update_position()
    def closeEvent(self, event): self.drawer.close(); super().closeEvent(event)
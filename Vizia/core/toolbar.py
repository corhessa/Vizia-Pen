# core/toolbar.py

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QSlider, 
                             QLabel, QFrame, QApplication)
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize
from ui.ui_components import ModernColorPicker
from ui.styles import TOOLBAR_STYLESHEET, get_color_btn_style

def resource_path(relative_path):
    """ Dosya yollarını EXE uyumlu hale getirir """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ModernToolbar(QWidget):
    def __init__(self, overlay):
        super().__init__(overlay)
        self.overlay = overlay
        self.old_pos = None
        self.custom_colors = ["#2c2c2e"] * 10 
        self.custom_color_index = 0
        self.last_active_tool = "pen"
        
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedWidth(75)
        self.setFixedHeight(640) # İkonlar biraz yer kaplayabilir, hafif uzattım
        
        # Stilleri uygula (Slider düzelmesi için kritik)
        self.setStyleSheet(TOOLBAR_STYLESHEET)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15) 
        layout.setSpacing(8)

        # Logo
        logo_path = resource_path("Vizia/Assets/VIZIA.ico")
        logo_label = QLabel()
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("V")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        layout.addSpacing(5)

        # --- ÇİZİM ARAÇLARI (SOLDAKİ DOSYA İSİMLERİNE GÖRE) ---
        
        self.btn_draw = self.create_btn("pencil.png", lambda: self.safe_change("pen", self.btn_draw), "Kalem")
        layout.addWidget(self.btn_draw, 0, Qt.AlignCenter)
        
        self.btn_eraser = self.create_btn("eraser.png", lambda: self.safe_change("eraser", self.btn_eraser), "Silgi")
        layout.addWidget(self.btn_eraser, 0, Qt.AlignCenter)
        
        # Metin Aracı (Resimdeki 'size.png' iki tane T harfi içeriyor, metin aracı bu olmalı)
        self.btn_text = self.create_btn("size.png", self.overlay.add_text, "Metin Ekle")
        layout.addWidget(self.btn_text, 0, Qt.AlignCenter)
        
        self.btn_board = self.create_btn("blackboard.png", self.toggle_board, "Beyaz Tahta / Masaüstü")
        self.btn_board.setProperty("state", "red") 
        layout.addWidget(self.btn_board, 0, Qt.AlignCenter)
        
        self.btn_move = self.create_btn("mouse.png", lambda: self.safe_change("move", self.btn_move), "Taşıma Modu")
        layout.addWidget(self.btn_move, 0, Qt.AlignCenter)
        
        # Ayırıcı
        layout.addSpacing(2)
        line = QFrame()
        line.setFixedHeight(1)
        line.setFixedWidth(40)
        line.setStyleSheet("background-color: #48484a; border: none;") 
        layout.addWidget(line, 0, Qt.AlignCenter)
        layout.addSpacing(2)
        
        self.btn_undo = self.create_btn("undo.png", self.overlay.undo, "Geri Al")
        layout.addWidget(self.btn_undo, 0, Qt.AlignCenter)
        
        self.btn_clear = self.create_btn("bin.png", self.overlay.clear_all, "Hepsini Temizle")
        layout.addWidget(self.btn_clear, 0, Qt.AlignCenter)
        
        self.btn_shot = self.create_btn("dslr-camera.png", self.overlay.take_screenshot, "Ekran Görüntüsü Al")
        self.btn_shot.setObjectName("btn_shot") 
        layout.addWidget(self.btn_shot, 0, Qt.AlignCenter)
        
        # Renk Butonu (Emoji değil, şekil karakteri)
        self.btn_color = QPushButton("⬤")
        self.btn_color.setToolTip("Renk Seç")
        self.btn_color.setFocusPolicy(Qt.NoFocus)
        self.btn_color.clicked.connect(self.select_color)
        self.btn_color.setFixedSize(40, 40)
        self.update_color_btn_style()
        layout.addWidget(self.btn_color, 0, Qt.AlignCenter)
        
        # Boyut Slider Alanı (Düzeltildi)
        size_box = QFrame()
        size_box.setFixedHeight(75) 
        size_box.setStyleSheet("background: transparent; border: none;")
        
        size_layout = QVBoxLayout(size_box)
        size_layout.setContentsMargins(0, 0, 0, 0) # Marginleri sıfırladım, dikeyde sıkışmasın
        size_layout.setSpacing(2) 

        lbl_size = QLabel("BOYUT")
        lbl_size.setAlignment(Qt.AlignCenter)
        # Orijinal beyaz ve net görünüm
        lbl_size.setStyleSheet("font-size: 10px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        size_layout.addWidget(lbl_size)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(2, 100)
        self.slider.setValue(4)
        self.slider.setFixedWidth(54)
        # Slider stili artık styles.py içinden geliyor (QSlider)
        self.slider.valueChanged.connect(self.update_brush_size)
        size_layout.addWidget(self.slider, 0, Qt.AlignCenter)

        self.lbl_percent = QLabel("4%")
        self.lbl_percent.setAlignment(Qt.AlignCenter)
        self.lbl_percent.setStyleSheet("font-size: 11px; color: #0a84ff; font-weight: bold;")
        size_layout.addWidget(self.lbl_percent)
        
        layout.addWidget(size_box, 0, Qt.AlignCenter)
        
        layout.addStretch()

        # Alt Menü
        layout.addWidget(self.create_btn("gear.png", lambda: None, "Ayarlar"), 0, Qt.AlignCenter)
        layout.addWidget(self.create_btn("info.png", self.show_about, "Hakkında"), 0, Qt.AlignCenter)
        
        btn_close = self.create_btn("close.png", QApplication.quit, "Çıkış")
        btn_close.setProperty("state", "red")
        layout.addWidget(btn_close, 0, Qt.AlignCenter)
        
        # Başlangıçta Kalem Aktif
        self.btn_draw.setProperty("active", True)

    def create_btn(self, icon_file, slot, tooltip_text=""):
        btn = QPushButton()
        # Vizia/Assets klasöründen okuma
        icon_path = resource_path(f"Vizia/Assets/{icon_file}")
        
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24)) # İkon boyutunu biraz büyüttüm
        else:
            # İkon yoksa metin göster (Hata önleyici)
            btn.setText(tooltip_text[0] if tooltip_text else "?")
            
        btn.clicked.connect(slot)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setFixedSize(40, 40)
        if tooltip_text:
            btn.setToolTip(tooltip_text)
        return btn

    def show_about(self):
        from ui.dialogs import AboutDialog
        AboutDialog(self).exec_()

    def select_color(self):
        picker = ModernColorPicker(self.overlay.current_color, self.custom_colors, self.overlay)
        if picker.exec_():
            color = picker.selected_color
            self.overlay.current_color = color
            self.update_color_btn_style()
        QTimer.singleShot(10, self.overlay.force_focus)

    def update_color_btn_style(self):
        color_hex = self.overlay.current_color.name()
        self.btn_color.setStyleSheet(get_color_btn_style(color_hex))

    def update_brush_size(self, val):
        self.overlay.brush_size = val
        self.lbl_percent.setText(f"{val}%")

    def toggle_board(self):
        self.overlay.whiteboard_mode = not self.overlay.whiteboard_mode
        state = "green" if self.overlay.whiteboard_mode else "red"
        self.btn_board.setProperty("state", state)
        self.btn_board.style().unpolish(self.btn_board)
        self.btn_board.style().polish(self.btn_board)
        self.overlay.redraw_canvas()
        QTimer.singleShot(10, self.overlay.force_focus)
    
    def toggle_move_mode(self):
        if self.overlay.drawing_mode != "move":
            self.last_active_tool = self.overlay.drawing_mode
            self.safe_change("move", self.btn_move)
        else:
            target_btn = self.btn_draw if self.last_active_tool == "pen" else self.btn_eraser
            self.safe_change(self.last_active_tool, target_btn)

    def safe_change(self, mode, button):
        self.overlay.drawing_mode = mode
        for b in [self.btn_draw, self.btn_move, self.btn_eraser]:
            b.setProperty("active", False)
            b.style().unpolish(b) 
            b.style().polish(b)   
        button.setProperty("active", True)
        button.style().unpolish(button)
        button.style().polish(button)
        self.overlay.setWindowFlag(Qt.WindowTransparentForInput, mode == "move")
        self.overlay.show()
        QTimer.singleShot(10, self.overlay.force_focus)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QFrame, QApplication
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
from ui_components import ModernColorPicker

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
        # DÜZELTME 1: Pencere boyunu ciddi oranda kısalttık (700 -> 630)
        # Bu sayede alttaki boşluk gitti ve butonlar yukarı kaydı
        self.setFixedHeight(630) 
        
        self.setStyleSheet("""
            QWidget { background-color: #1c1c1e; border-radius: 20px; border: 1.5px solid #3a3a3c; }
            QPushButton { background-color: #2c2c2e; color: white; border: none; border-radius: 10px; font-size: 18px; min-width: 40px; min-height: 40px; }
            QPushButton:hover { background-color: #3a3a40; border: 1px solid #007aff; }
            QLabel { color: white; background: transparent; border: none; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) 
        layout.setSpacing(5) # Butonlar arası sıkı boşluk korundu

        # Logo
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_path, "Assets", "VIZIA.ico")
        logo_label = QLabel()
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("V")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        layout.addSpacing(3)

        # Çizim Araçları
        self.btn_draw = self.create_btn("🖋", lambda: self.safe_change("pen", self.btn_draw))
        layout.addWidget(self.btn_draw, 0, Qt.AlignCenter)
        
        self.btn_eraser = self.create_btn("🧼", lambda: self.safe_change("eraser", self.btn_eraser))
        layout.addWidget(self.btn_eraser, 0, Qt.AlignCenter)
        
        layout.addWidget(self.create_btn("T", self.overlay.add_text), 0, Qt.AlignCenter)
        
        self.btn_board = self.create_btn("📋", self.toggle_board)
        self.btn_board.setStyleSheet("background-color: #ff3b30;")
        layout.addWidget(self.btn_board, 0, Qt.AlignCenter)
        
        self.btn_move = self.create_btn("🖱", lambda: self.safe_change("move", self.btn_move))
        layout.addWidget(self.btn_move, 0, Qt.AlignCenter)
        
        # Ayırıcı Çizgi
        layout.addSpacing(2)
        line = QFrame()
        line.setFixedHeight(1)
        line.setFixedWidth(40)
        line.setStyleSheet("background-color: #48484a; border: none;") 
        layout.addWidget(line, 0, Qt.AlignCenter)
        layout.addSpacing(2)
        
        layout.addWidget(self.create_btn("↺", self.overlay.undo), 0, Qt.AlignCenter)
        
        btn_clear = self.create_btn("🗑️", self.overlay.clear_all)
        layout.addWidget(btn_clear, 0, Qt.AlignCenter)
        
        self.btn_shot = self.create_btn("📸", self.overlay.take_screenshot)
        self.btn_shot.setStyleSheet("background-color: #5856d6;")
        layout.addWidget(self.btn_shot, 0, Qt.AlignCenter)
        
        self.btn_color = self.create_btn("⬤", self.select_color)
        self.btn_color.setStyleSheet(f"color: {self.overlay.current_color.name()}; font-size: 20px;")
        layout.addWidget(self.btn_color, 0, Qt.AlignCenter)
        
        # --- DÜZELTME 2: DAHA KOMPAKT & YUKARIDA ---
        size_box = QFrame()
        # Yüksekliği azalttık (85 -> 70), böylece yer kaplamıyor
        size_box.setFixedHeight(70) 
        size_box.setStyleSheet("background: transparent; border: none;")
        
        size_layout = QVBoxLayout(size_box)
        # Üst boşluğu (margin) sıfırladık, böylece renk butonuna yaklaştı
        size_layout.setContentsMargins(0, 0, 0, 0) 
        # Elemanlar arası boşluğu 2px'e indirdik (birbirlerine çok yakınlar)
        size_layout.setSpacing(2) 

        lbl_size = QLabel("BOYUT")
        lbl_size.setAlignment(Qt.AlignCenter)
        lbl_size.setStyleSheet("font-size: 10px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
        size_layout.addWidget(lbl_size)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(2, 100)
        self.slider.setValue(4)
        self.slider.setFixedWidth(54)
        self.slider.setStyleSheet("""
            QSlider { margin-top: -4px; }
            QSlider::groove:horizontal { 
                background: #3a3a3c; height: 4px; border-radius: 2px; 
            }
            QSlider::sub-page:horizontal {
                background: #007aff; border-radius: 2px;
            }
            QSlider::handle:horizontal { 
                background: #ffffff; border: 2px solid #007aff; 
                width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; 
            }
            QSlider::handle:horizontal:hover {
                background: #f0f0f0; border: 2px solid #005bb5;
            }
        """)
        self.slider.valueChanged.connect(self.update_brush_size)
        size_layout.addWidget(self.slider, 0, Qt.AlignCenter)

        self.lbl_percent = QLabel("4%")
        self.lbl_percent.setAlignment(Qt.AlignCenter)
        self.lbl_percent.setStyleSheet("font-size: 11px; color: #0a84ff; font-weight: bold;")
        size_layout.addWidget(self.lbl_percent)
        
        layout.addWidget(size_box, 0, Qt.AlignCenter)
        # ------------------------------------------
        
        layout.addStretch()

        # Alt Menü
        layout.addWidget(self.create_btn("⚙️", lambda: None), 0, Qt.AlignCenter)
        layout.addWidget(self.create_btn("ℹ️", self.show_about), 0, Qt.AlignCenter)
        
        btn_close = self.create_btn("✕", QApplication.quit)
        btn_close.setStyleSheet("background-color: #ff3b30; color: white;")
        layout.addWidget(btn_close, 0, Qt.AlignCenter)
        
        self.safe_change("pen", self.btn_draw)

    def show_about(self):
        from core.overlay import AboutDialog
        AboutDialog(self).exec_()

    def select_color(self):
        picker = ModernColorPicker(self.overlay.current_color, self.custom_colors, self.overlay)
        if picker.exec_():
            color = picker.selected_color
            self.overlay.current_color = color
            self.btn_color.setStyleSheet(f"color: {color.name()}; font-size: 20px;")
        QTimer.singleShot(10, self.overlay.force_focus)

    def update_brush_size(self, val):
        self.overlay.brush_size = val
        self.lbl_percent.setText(f"{val}%")

    def create_btn(self, text, slot):
        btn = QPushButton(text)
        btn.clicked.connect(slot)
        btn.setFocusPolicy(Qt.NoFocus)
        return btn
    
    def toggle_board(self):
        self.overlay.whiteboard_mode = not self.overlay.whiteboard_mode
        self.btn_board.setStyleSheet("background-color: #4cd964;" if self.overlay.whiteboard_mode else "background-color: #ff3b30;")
        self.overlay.redraw_canvas()
        self.overlay.update()
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
            b.setStyleSheet("background-color: #2c2c2e;")
        button.setStyleSheet("background-color: #007aff; border: 1px solid white;")
        
        self.overlay.setWindowFlag(Qt.WindowTransparentForInput, mode == "move")
        self.overlay.show()
        QTimer.singleShot(10, self.overlay.force_focus)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
# Vizia/core/toolbar.py

import sys
import os
import importlib.util  # [YENİ] Dinamik yükleme için gerekli
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, 
                             QLabel, QFrame, QApplication, QGraphicsOpacityEffect)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint

from ui.widgets.color_picker import ModernColorPicker
from ui.styles import TOOLBAR_STYLESHEET, get_color_btn_style
from core.settings import SettingsDialog

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- EK ARAÇLAR (DRAWER) ---
class ExtensionDrawer(QWidget):
    def __init__(self, parent_toolbar):
        super().__init__(None) # Bağımsız
        self.toolbar_ref = parent_toolbar
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # [GÜNCELLENDİ] Tooltip ayarı
        self.setAttribute(Qt.WA_AlwaysShowToolTips, True)
        
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
        
        # --- ANA PROJEDE KALAN SABİT BUTON ---
        self.btn_folder = self.create_drawer_btn("add-folder.png", "Görsel Yükle", self.action_load_image)
        self.layout.addWidget(self.btn_folder)
        
        # [YENİ] Dinamik Eklentileri Yükle
        self.load_plugins()
        
        self.layout.addStretch()
        
        self.anim = QPropertyAnimation(self, b"size")
        self.anim.setEasingCurve(QEasingCurve.OutExpo)
        self.anim.setDuration(300)
        
    def keyPressEvent(self, event):
        key = event.key()
        overlay = self.toolbar_ref.overlay
        if overlay:
            if key == Qt.Key_Backspace:
                overlay.toolbar.toggle_board()
                event.accept()
                return

            hotkey_str = overlay.settings.get("hotkeys").get("board_mode") 
            if hotkey_str:
                seq = QKeySequence(key)
                if seq.matches(QKeySequence(hotkey_str)) == QKeySequence.ExactMatch:
                    overlay.toolbar.toggle_board()
                    event.accept() 
                    return 
        super().keyPressEvent(event)

    # [GÜNCELLENDİ] Hem Asset hem de Plugin klasöründen ikon kabul eder
    def create_drawer_btn(self, icon_path_or_name, tooltip, func):
        btn = QPushButton()
        
        # 1. Önce eklentiden gelen tam yol mu diye kontrol et
        if os.path.exists(icon_path_or_name):
            final_path = icon_path_or_name
        else:
            # 2. Değilse, ana projenin Assets klasöründe ara
            final_path = resource_path(f"Vizia/Assets/{icon_path_or_name}")

        if os.path.exists(final_path):
            btn.setIcon(QIcon(final_path))
            btn.setIconSize(QSize(24, 24))
        else:
            # İkon yoksa baş harfi göster
            text = tooltip[0] if tooltip else "?"
            btn.setText(text)
            btn.setStyleSheet("color: white; font-weight: bold;")
            
        btn.setFixedSize(40, 40)
        btn.setToolTip(tooltip)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.clicked.connect(lambda: self.handle_click_sequence(func))
        return btn

    def handle_click_sequence(self, func):
        if func: func()
        self.raise_()

    # [YENİ] Eklenti Yükleme Mantığı
    def load_plugins(self):
        # Bu dosya: Vizia/core/toolbar.py
        # Plugins klasörü: Vizia/plugins (Main.py ile aynı seviyede olması için '../plugins')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Önce 'core'un yanındaki 'plugins' klasörüne bak (Vizia/plugins)
        plugins_dir = os.path.abspath(os.path.join(current_dir, "../plugins"))
        
        # Eğer orada yoksa bir üst dizine bak (Proje kökü)
        if not os.path.exists(plugins_dir):
            plugins_dir = os.path.abspath(os.path.join(current_dir, "../../plugins"))

        if not os.path.exists(plugins_dir):
            print(f"Plugins klasörü bulunamadı: {plugins_dir}")
            return

        # Klasörleri gez
        for folder_name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, folder_name)
            plugin_file = os.path.join(plugin_path, "plugin.py")

            if os.path.isdir(plugin_path) and os.path.exists(plugin_file):
                try:
                    # Dinamik Import
                    spec = importlib.util.spec_from_file_location(f"plugins.{folder_name}", plugin_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Plugin Sınıfını Başlat
                    if hasattr(module, "ViziaPlugin"):
                        plugin_instance = module.ViziaPlugin()
                        
                        # İkon yolunu tam yola çevir
                        full_icon_path = os.path.join(plugin_path, plugin_instance.icon)
                        
                        # Butonu Oluştur ve Ekle
                        # (lambda p=... ile değişkeni sabitlemek önemli)
                        btn = self.create_drawer_btn(
                            full_icon_path, 
                            plugin_instance.name, 
                            lambda p=plugin_instance: p.run(self.toolbar_ref.overlay)
                        )
                        self.layout.addWidget(btn)
                        print(f"Eklenti Yüklendi: {plugin_instance.name}")
                        
                except Exception as e:
                    print(f"Eklenti Yükleme Hatası ({folder_name}): {e}")

    def action_load_image(self):
        if hasattr(self.toolbar_ref, 'overlay'): self.toolbar_ref.overlay.open_image_loader()

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
            self.is_open = True; self.show(); self.raise_()
            # [SİSTEM HATASI FİXİ] Windows UpdateLayeredWindowIndirect çökmesini engellemek için "0" olan başlangıç genişliğini "1" yaptık.
            self.container.resize(self.target_width, content_height); self.resize(1, content_height)
            self.update_position()
            self.anim.setStartValue(QSize(1, content_height)); self.anim.setEndValue(QSize(self.target_width, content_height)); self.anim.start()
        else:
            self.is_open = False
            self.anim.setStartValue(self.size()); self.anim.setEndValue(QSize(1, content_height)); self.anim.finished.connect(self._on_close_finished); self.anim.start()

    def _on_close_finished(self):
        if not self.is_open:
            self.hide()
            try: self.anim.finished.disconnect(self._on_close_finished)
            except: pass

class ModernToolbar(QWidget):
    def __init__(self, overlay):
        super().__init__(overlay)
        self.overlay = overlay
        self.old_pos = None
        self.custom_colors = self.overlay.settings.get("custom_colors")
        self.custom_color_index = 0
        self.last_active_tool = "pen"
        
        self.setAttribute(Qt.WA_AlwaysShowToolTips, True)
        
        self.drawer = ExtensionDrawer(self)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setFixedWidth(95); self.setFixedHeight(640) 
        self.main_layout = QHBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.content_frame = QFrame(); self.content_frame.setFixedWidth(75)
        self.content_frame.setStyleSheet(TOOLBAR_STYLESHEET) 
        layout = QVBoxLayout(self.content_frame); layout.setContentsMargins(10, 15, 10, 15); layout.setSpacing(8)

        logo_path = resource_path("Vizia/Assets/VIZIA.ico")
        logo_label = QLabel(); logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull(): logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else: logo_label.setText("V")
        logo_label.setAlignment(Qt.AlignCenter); layout.addWidget(logo_label); layout.addSpacing(5)

        self.btn_draw = self.create_btn("pencil.png", lambda: self.safe_change("pen", self.btn_draw), "Kalem"); layout.addWidget(self.btn_draw, 0, Qt.AlignCenter)
        self.btn_eraser = self.create_btn("eraser.png", lambda: self.safe_change("eraser", self.btn_eraser), "Silgi"); layout.addWidget(self.btn_eraser, 0, Qt.AlignCenter)
        self.btn_text = self.create_btn("size.png", self.overlay.add_text, "Metin Ekle"); layout.addWidget(self.btn_text, 0, Qt.AlignCenter)
        self.btn_board = self.create_btn("blackboard.png", self.toggle_board, "Beyaz Tahta / Masaüstü"); self.btn_board.setProperty("state", "red"); layout.addWidget(self.btn_board, 0, Qt.AlignCenter)
        self.btn_move = self.create_btn("mouse.png", lambda: self.safe_change("move", self.btn_move), "Taşıma Modu"); layout.addWidget(self.btn_move, 0, Qt.AlignCenter)
        
        layout.addSpacing(2); line = QFrame(); line.setFixedHeight(1); line.setFixedWidth(40); line.setStyleSheet("background-color: #48484a; border: none;"); layout.addWidget(line, 0, Qt.AlignCenter); layout.addSpacing(2)
        
        self.btn_undo = self.create_btn("undo.png", self.overlay.undo, "Geri Al"); layout.addWidget(self.btn_undo, 0, Qt.AlignCenter)
        self.btn_clear = self.create_btn("bin.png", self.overlay.clear_all, "Hepsini Temizle"); layout.addWidget(self.btn_clear, 0, Qt.AlignCenter)
        self.btn_shot = self.create_btn("dslr-camera.png", self.overlay.take_screenshot, "Ekran Görüntüsü Al"); self.btn_shot.setObjectName("btn_shot"); layout.addWidget(self.btn_shot, 0, Qt.AlignCenter)
        
        self.btn_color = QPushButton("⬤"); self.btn_color.setToolTip("Renk Seç"); self.btn_color.setFocusPolicy(Qt.NoFocus); self.btn_color.clicked.connect(self.select_color); self.btn_color.setFixedSize(40, 40)
        self.update_color_btn_style(); layout.addWidget(self.btn_color, 0, Qt.AlignCenter)
        
        size_box = QFrame(); size_box.setFixedHeight(75); size_box.setStyleSheet("background: transparent; border: none;")
        size_layout = QVBoxLayout(size_box); size_layout.setContentsMargins(0, 0, 0, 0); size_layout.setSpacing(2) 
        lbl_size = QLabel("BOYUT"); lbl_size.setAlignment(Qt.AlignCenter); lbl_size.setStyleSheet("font-size: 10px; font-weight: 800; color: #ffffff; letter-spacing: 1px;"); size_layout.addWidget(lbl_size)
        self.slider = QSlider(Qt.Horizontal); self.slider.setRange(2, 100); self.slider.setValue(4); self.slider.setFixedWidth(54); self.slider.valueChanged.connect(self.update_brush_size); size_layout.addWidget(self.slider, 0, Qt.AlignCenter)
        self.lbl_percent = QLabel("4%"); self.lbl_percent.setAlignment(Qt.AlignCenter); self.lbl_percent.setStyleSheet("font-size: 11px; color: #0a84ff; font-weight: bold;"); size_layout.addWidget(self.lbl_percent)
        layout.addWidget(size_box, 0, Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(self.create_btn("gear.png", self.show_settings, "Ayarlar"), 0, Qt.AlignCenter)
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
    def show_settings(self):
        dlg = SettingsDialog(self, self.overlay.settings)
        if dlg.exec_(): self.custom_colors = self.overlay.settings.get("custom_colors")
        QTimer.singleShot(10, self.overlay.force_focus)
    def select_color(self):
        picker = ModernColorPicker(self.overlay.current_color, self.custom_colors, self.overlay.settings, self)
        if picker.exec_(): color = picker.selected_color; self.overlay.current_color = color; self.update_color_btn_style(); self.overlay.settings.set("custom_colors", self.custom_colors)
        QTimer.singleShot(10, self.overlay.force_focus)
    def update_color_btn_style(self): self.btn_color.setStyleSheet(get_color_btn_style(self.overlay.current_color.name()))
    def update_brush_size(self, val): self.overlay.brush_size = val; self.lbl_percent.setText(f"{val}%")
    
    def toggle_board(self):
        self.overlay.whiteboard_mode = not self.overlay.whiteboard_mode
        self.btn_board.setProperty("state", "green" if self.overlay.whiteboard_mode else "red")
        self.btn_board.style().unpolish(self.btn_board)
        self.btn_board.style().polish(self.btn_board)
        # [DÜZELTME] Anında tepki için render zorlaması
        self.btn_board.repaint() 
        QApplication.processEvents()
        
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
            b.repaint() # Eski mavi rengi hemen sil   
            
        button.setProperty("active", True)
        button.style().unpolish(button)
        button.style().polish(button)
        # [DÜZELTME] Yeni mavi efekti gecikmesiz göster
        button.repaint()
        QApplication.processEvents()
        
        self.overlay.setWindowFlag(Qt.WindowTransparentForInput, mode == "move")
        self.overlay.show()
        QTimer.singleShot(10, self.overlay.force_focus)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos; self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPos()
            if self.drawer.isVisible() and self.drawer.is_open: self.drawer.update_position()
    def closeEvent(self, event): self.drawer.close(); super().closeEvent(event)
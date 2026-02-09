# Vizia/core/settings.py

import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QFileDialog, QTabWidget, QWidget, QFrame, QScrollArea, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

SETTINGS_FILE = "vizia_settings.json"

# --- VARSAYILAN AYARLAR ---
DEFAULT_SETTINGS = {
    "save_path": os.path.join(os.path.expanduser("~"), "Pictures", "Vizia Screenshots"),
    "keep_colors": True,
    "hotkeys": {
        "board_mode": "Space",
        "drawer": "E",
        "undo": "Backspace",
        "clear": "D",
        "screenshot": "S",
        "move_mode": "V",
        "color_picker": "C",
        "quit": "Q"
    },
    "custom_colors": ["#2c2c2e"] * 10
}

# --- AYAR YÖNETİCİSİ ---
class SettingsManager:
    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            self.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in data: data[k] = v
                return data
        except:
            return DEFAULT_SETTINGS.copy()

    def save_settings(self, data=None):
        if data: self.settings = data
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Ayarlar kaydedilemedi: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_key_code(self, action_name):
        key_str = self.settings["hotkeys"].get(action_name, "")
        if not key_str: return None
        seq = QKeySequence(key_str)
        return seq[0] if seq.count() > 0 else None

# --- ARAYÜZ BİLEŞENLERİ ---
class KeybindButton(QPushButton):
    def __init__(self, action_key, current_key, parent_dialog):
        super().__init__(current_key)
        self.action_key = action_key
        self.parent_dialog = parent_dialog
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton { background-color: #2c2c2e; border: 1px solid #3a3a3c; color: white; border-radius: 6px; padding: 5px 15px; font-weight: bold; }
            QPushButton:checked { background-color: #007aff; border-color: white; color: white; }
            QPushButton:hover { border-color: #007aff; }
        """)
        self.clicked.connect(self.wait_for_key)

    def wait_for_key(self):
        self.setText("Tuşa Basın...")
        self.parent_dialog.current_binding_btn = self
        self.parent_dialog.setFocus()

# --- BURASI EKSİK OLABİLİR, MUTLAKA EKLE ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        # Ayarları kopyala (İptal edilirse geri dönmek için)
        self.temp_settings = json.loads(json.dumps(self.settings_manager.settings))
        self.current_binding_btn = None
        
        self.setWindowTitle("Vizia Ayarlar")
        self.setFixedSize(500, 550)
        self.setStyleSheet("""
            QDialog { background-color: #1c1c1e; color: white; }
            QLabel { color: #ebebeb; font-size: 14px; }
            QTabWidget::pane { border: 1px solid #3a3a3c; background: #1c1c1e; }
            QTabBar::tab { background: #2c2c2e; color: #8e8e93; padding: 10px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background: #3a3a3c; color: white; border-bottom: 2px solid #007aff; }
            QLineEdit { background-color: #2c2c2e; border: 1px solid #3a3a3c; color: white; padding: 8px; border-radius: 6px; }
            QCheckBox { color: #ebebeb; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #3a3a3c; border-radius: 4px; background: #2c2c2e; }
            QCheckBox::indicator:checked { background: #007aff; border-color: #007aff; }
        """)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab_general = QWidget()
        self.tab_hotkeys = QWidget()
        
        self.setup_general_tab()
        self.setup_hotkeys_tab()
        
        self.tabs.addTab(self.tab_general, "Genel")
        self.tabs.addTab(self.tab_hotkeys, "Kısayollar")
        layout.addWidget(self.tabs)
        
        btn_box = QHBoxLayout()
        self.btn_reset = QPushButton("Varsayılanlara Dön")
        self.btn_reset.setStyleSheet("color: #ff3b30; background: transparent; font-weight: bold; text-align: left; padding-left: 0;")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_to_defaults)
        btn_box.addWidget(self.btn_reset)
        btn_box.addStretch()
        
        self.btn_save = QPushButton("Kaydet ve Çık")
        self.btn_save.setFixedSize(120, 35)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("QPushButton { background-color: #007aff; color: white; border-radius: 6px; font-weight: bold; border: none; } QPushButton:hover { background-color: #005bb5; }")
        self.btn_save.clicked.connect(self.save_and_close)
        btn_box.addWidget(self.btn_save)
        layout.addLayout(btn_box)

    def setup_general_tab(self):
        layout = QVBoxLayout(self.tab_general)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Kayıt Yeri
        layout.addWidget(QLabel("Ekran Görüntüsü Kayıt Yeri:"))
        path_box = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.temp_settings["save_path"])
        self.path_input.setReadOnly(True)
        btn_browse = QPushButton("...")
        btn_browse.setFixedSize(40, 35)
        btn_browse.setCursor(Qt.PointingHandCursor)
        btn_browse.setStyleSheet("background-color: #3a3a3c; color: white; border-radius: 6px;")
        btn_browse.clicked.connect(self.browse_path)
        path_box.addWidget(self.path_input)
        path_box.addWidget(btn_browse)
        layout.addLayout(path_box)
        
        layout.addSpacing(20)
        
        # Renk Paletini Koru
        self.chk_keep_colors = QCheckBox("Sıfırlarken Renk Paletimi Koru")
        self.chk_keep_colors.setChecked(self.temp_settings.get("keep_colors", True))
        self.chk_keep_colors.stateChanged.connect(self.update_keep_colors)
        layout.addWidget(self.chk_keep_colors)
        
        layout.addStretch()
        info = QLabel("Vizia Pen v1.0\nModern Drawing Assistant")
        info.setStyleSheet("color: #555; font-size: 11px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

    def setup_hotkeys_tab(self):
        layout = QVBoxLayout(self.tab_hotkeys)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget(); form = QVBoxLayout(content); form.setSpacing(15)
        
        labels = {"board_mode": "Beyaz Tahta", "drawer": "Ek Araçlar", "undo": "Geri Al", "clear": "Temizle", "screenshot": "Ekran Görüntüsü", "move_mode": "Taşıma Modu", "color_picker": "Renk Seçici", "quit": "Çıkış"}
        self.btn_map = {}
        for key, text in labels.items():
            row = QHBoxLayout()
            lbl = QLabel(text); lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
            btn = KeybindButton(key, self.temp_settings["hotkeys"].get(key, ""), self)
            self.btn_map[key] = btn
            row.addWidget(lbl); row.addStretch(); row.addWidget(btn)
            form.addLayout(row)
            line = QFrame(); line.setFrameShape(QFrame.HLine); line.setStyleSheet("background-color: #2c2c2e;"); form.addWidget(line)
        scroll.setWidget(content); layout.addWidget(scroll)

    def browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç", self.path_input.text())
        if folder: self.path_input.setText(folder); self.temp_settings["save_path"] = folder

    def update_keep_colors(self, state):
        self.temp_settings["keep_colors"] = (state == Qt.Checked)

    def keyPressEvent(self, event):
        if self.current_binding_btn:
            key = event.key()
            if key == Qt.Key_Escape:
                txt = self.temp_settings["hotkeys"][self.current_binding_btn.action_key]
            else:
                txt = QKeySequence(key | int(event.modifiers())).toString()
                self.temp_settings["hotkeys"][self.current_binding_btn.action_key] = txt
            self.current_binding_btn.setText(txt)
            self.current_binding_btn.setChecked(False)
            self.current_binding_btn = None
        else: super().keyPressEvent(event)

    def reset_to_defaults(self):
        should_keep = self.chk_keep_colors.isChecked()
        backup_colors = self.temp_settings.get("custom_colors", []) if should_keep else None
        
        self.temp_settings = json.loads(json.dumps(DEFAULT_SETTINGS))
        
        if should_keep and backup_colors:
            self.temp_settings["custom_colors"] = backup_colors
            self.temp_settings["keep_colors"] = True
        
        self.path_input.setText(self.temp_settings["save_path"])
        self.chk_keep_colors.setChecked(self.temp_settings.get("keep_colors", True))
        for key, btn in self.btn_map.items(): btn.setText(self.temp_settings["hotkeys"].get(key, ""))

    def save_and_close(self):
        self.settings_manager.save_settings(self.temp_settings)
        self.accept()
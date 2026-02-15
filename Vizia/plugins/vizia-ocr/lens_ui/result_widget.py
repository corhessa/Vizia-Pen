from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QTextEdit, QComboBox, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from lens_core.config import save_config

class TranslationThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, translator, text, target):
        super().__init__()
        self.translator = translator
        self.text = text
        self.target = target

    def run(self):
        res = self.translator.translate(self.text, target=self.target)
        self.result_ready.emit(res)

class LensResultWidget(QWidget):
    def __init__(self, text, crop_rect, plugin, parent=None):
        super().__init__(parent)
        self.original_text = text
        self.plugin = plugin
        self.translator = plugin.translator
        self.crop_rect = crop_rect
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.init_ui()
        self.position_widget()

    def init_ui(self):
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("""
            QFrame { background-color: #1c1c1e; border: 1.5px solid #3a3a3c; border-radius: 12px; color: white; }
            QTextEdit { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 8px; padding: 5px; color: white; selection-background-color: #0a84ff; }
            QPushButton { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 6px; padding: 4px 10px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #3a3a3c; border: 1px solid #0a84ff; }
            QComboBox { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 6px; padding: 2px 5px; color: white; }
            QComboBox::drop-down { border: none; }
        """)
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0,0,0,0)
        
        lbl_title = QLabel("OCR Sonucu")
        lbl_title.setStyleSheet("color: #0a84ff; font-weight: bold; border: none;")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch()
        
        btn_copy = QPushButton("Kopyala")
        btn_copy.clicked.connect(self.copy_original)
        top_bar.addWidget(btn_copy)
        
        btn_close = QPushButton("X")
        btn_close.setStyleSheet("background-color: #ff453a; color: white; border: none; padding: 4px 8px;")
        btn_close.clicked.connect(self.close)
        top_bar.addWidget(btn_close)
        
        layout.addLayout(top_bar)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.original_text)
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(60)
        self.text_edit.setMaximumHeight(120)
        layout.addWidget(self.text_edit)
        
        trans_bar = QHBoxLayout()
        trans_bar.setContentsMargins(0,0,0,0)
        
        lbl_trans = QLabel("Çevir:")
        lbl_trans.setStyleSheet("border: none;")
        trans_bar.addWidget(lbl_trans)
        
        self.combo_lang = QComboBox()
        self.langs = {
            "Yok": "", "Türkçe": "tr", "İngilizce": "en", "Almanca": "de",
            "Fransızca": "fr", "İspanyolca": "es", "İtalyanca": "it",
            "Rusça": "ru", "Arapça": "ar", "Çince (Basit)": "zh-CN",
            "Japonca": "ja", "Korece": "ko", "Hintçe": "hi",
            "Portekizce": "pt", "Felemenkçe": "nl", "Yunanca": "el",
            "İsveççe": "sv", "Lehçe": "pl", "Danca": "da", "Fince": "fi",
            "Çekçe": "cs", "Tayca": "th", "Vietnamca": "vi", "İbranice": "he"
        }
        self.combo_lang.addItems(list(self.langs.keys()))
        
        # Son seçilen dili yükle
        last_lang = self.plugin.config.get("target_lang", "Yok")
        if last_lang in self.langs:
            self.combo_lang.setCurrentText(last_lang)
            
        self.combo_lang.currentIndexChanged.connect(self.start_translation)
        trans_bar.addWidget(self.combo_lang)
        trans_bar.addStretch()
        
        self.btn_copy_trans = QPushButton("Çeviriyi Kopyala")
        self.btn_copy_trans.clicked.connect(self.copy_translation)
        self.btn_copy_trans.hide()
        trans_bar.addWidget(self.btn_copy_trans)
        
        layout.addLayout(trans_bar)
        
        self.trans_edit = QTextEdit()
        self.trans_edit.setReadOnly(True)
        self.trans_edit.setMinimumHeight(60)
        self.trans_edit.setMaximumHeight(120)
        self.trans_edit.hide()
        layout.addWidget(self.trans_edit)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.main_frame)
        self.resize(500, 150) # Genişlik 350'den 500'e çıkarıldı

        # Eğer açılışta çeviri seçiliyse hemen başlat
        if self.combo_lang.currentText() != "Yok":
            self.start_translation()

    # --- SÜRÜKLE BIRAK (DRAGGABLE) MANTIĞI ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def position_widget(self):
        screen_geom = QApplication.primaryScreen().geometry()
        x = self.crop_rect.x()
        y = self.crop_rect.bottom() + 10 
        
        if y + self.height() > screen_geom.height():
            y = self.crop_rect.y() - self.height() - 10
            
        if x + self.width() > screen_geom.width():
            x = screen_geom.width() - self.width() - 10
            
        self.move(x, y)

    def start_translation(self):
        target_name = self.combo_lang.currentText()
        target_code = self.langs[target_name]
        
        # Seçimi kaydet
        self.plugin.config["target_lang"] = target_name
        save_config(self.plugin.config)
        
        if not target_code:
            self.trans_edit.hide()
            self.btn_copy_trans.hide()
            self.adjustSize()
            return
            
        self.trans_edit.show()
        self.trans_edit.setPlainText("Çevriliyor... Lütfen bekleyin.")
        self.btn_copy_trans.hide()
        self.adjustSize()
        
        self.thread = TranslationThread(self.translator, self.original_text, target_code)
        self.thread.result_ready.connect(self.show_translation)
        self.thread.start()

    def show_translation(self, result):
        self.trans_edit.setPlainText(result)
        self.btn_copy_trans.show()

    def copy_original(self):
        QApplication.clipboard().setText(self.original_text)

    def copy_translation(self):
        QApplication.clipboard().setText(self.trans_edit.toPlainText())
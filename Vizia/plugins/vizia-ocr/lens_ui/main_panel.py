from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QProgressBar
from PyQt5.QtCore import Qt

# İki noktayı kaldırdık, doğrudan lens_core çağırıyoruz
from lens_core.language_manager import LanguageManager, LanguageDownloader
from .drop_zone import ViziaDropZone

# ... kodun geri kalanı aynı
class ViziaLensPanel(QWidget):
    def __init__(self, plugin, overlay):
        super().__init__()
        self.plugin = plugin
        self.overlay = overlay
        self.lang_manager = LanguageManager()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.refresh_languages()

    def init_ui(self):
        self.main_container = QFrame(self)
        self.main_container.setStyleSheet("""
            QFrame { background-color: #1c1c1e; border: 1.5px solid #3a3a3c; border-radius: 15px; color: white; }
            QPushButton { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 8px; padding: 6px; color: white; }
            QPushButton:hover { background-color: #3a3a3c; border: 1px solid #0a84ff; }
        """)
        
        layout = QVBoxLayout(self.main_container)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # --- Üst Kısım: Hızlı Ayar ---
        header = QLabel("Vizia Lens Ayarları")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #0a84ff; border: none;")
        layout.addWidget(header)
        
        self.btn_quick = QPushButton(f"Tek Tıkla Tarama: {'AÇIK' if self.plugin.quick_scan_enabled else 'KAPALI'}")
        self.btn_quick.clicked.connect(self.toggle_quick_mode)
        layout.addWidget(self.btn_quick)
        
        # --- Orta Kısım: Dil Paketleri ---
        lbl_lang = QLabel("Dil Paketleri (OCR & Çeviri)")
        lbl_lang.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px; border: none;")
        layout.addWidget(lbl_lang)
        
        self.lang_list_layout = QVBoxLayout()
        layout.addLayout(self.lang_list_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # --- Alt Kısım: Dosya İşleme (Drop Zone) ---
        lbl_drop = QLabel("Dosya Workflow")
        lbl_drop.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px; border: none;")
        layout.addWidget(lbl_drop)
        
        self.drop_zone = ViziaDropZone(self)
        layout.addWidget(self.drop_zone)

        btn_close = QPushButton("Kapat")
        btn_close.setStyleSheet("background-color: #ff453a; color: white; font-weight: bold; border: none;")
        btn_close.clicked.connect(self.hide)
        layout.addWidget(btn_close)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.main_container)
        self.resize(320, 450)

    def toggle_quick_mode(self):
        self.plugin.quick_scan_enabled = not self.plugin.quick_scan_enabled
        self.btn_quick.setText(f"Tek Tıkla Tarama: {'AÇIK' if self.plugin.quick_scan_enabled else 'KAPALI'}")

    def refresh_languages(self):
        # Temizle
        for i in reversed(range(self.lang_list_layout.count())): 
            self.lang_list_layout.itemAt(i).widget().setParent(None)
            
        langs = {"tur": "Türkçe", "eng": "İngilizce", "deu": "Almanca"}
        
        for code, name in langs.items():
            row = QFrame()
            row.setStyleSheet("border: none;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0,0,0,0)
            
            lbl = QLabel(name)
            is_installed = self.lang_manager.is_installed(code)
            
            btn = QPushButton("Sil" if is_installed else "İndir")
            if is_installed:
                btn.setStyleSheet("color: #ff453a;")
                btn.clicked.connect(lambda c=False, lc=code: self.delete_lang(lc))
            else:
                btn.setStyleSheet("color: #32d74b;")
                btn.clicked.connect(lambda c=False, lc=code: self.download_lang(lc))
                
            row_layout.addWidget(lbl)
            row_layout.addStretch()
            row_layout.addWidget(btn)
            self.lang_list_layout.addWidget(row)

    def download_lang(self, code):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.downloader = LanguageDownloader(code, self.lang_manager.tessdata_dir)
        self.downloader.progress.connect(self.progress_bar.setValue)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.start()

    def on_download_finished(self, success, msg):
        self.progress_bar.hide()
        self.refresh_languages()
        if not success:
            print(f"İndirme Hatası: {msg}")

    def delete_lang(self, code):
        self.lang_manager.delete_language(code)
        self.refresh_languages()
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QFrame, QProgressBar, QScrollArea, QTabWidget, QComboBox, 
                             QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt
from lens_core.language_manager import LanguageManager, LanguageDownloader
from lens_core.config import save_config
from workflow.orchestrator import ViziaWorkflowOrchestrator

class ViziaLensPanel(QWidget):
    def __init__(self, plugin, overlay):
        super().__init__()
        self.plugin = plugin
        self.overlay = overlay
        self.lang_manager = LanguageManager()
        self.selected_file = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.refresh_languages()

    def init_ui(self):
        self.main_container = QFrame(self)
        self.main_container.setStyleSheet("""
            QFrame#MainContainer { background-color: #1c1c1e; border: 1.5px solid #3a3a3c; border-radius: 15px; }
            QLabel { color: white; border: none; }
            QPushButton { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 8px; padding: 6px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #3a3a3c; border: 1px solid #0a84ff; }
            QPushButton#PrimaryBtn { background-color: #0a84ff; color: white; border: none; padding: 10px; border-radius: 8px; font-size: 13px; }
            QPushButton#PrimaryBtn:hover { background-color: #0070e0; }
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { background: #2c2c2e; color: #a1a1a6; padding: 8px 15px; border-radius: 6px; margin: 0px 5px 10px 0px; font-weight: bold; }
            QTabBar::tab:selected { background: #0a84ff; color: white; }
            QComboBox { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 6px; padding: 5px; color: white; }
            QCheckBox { color: white; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #48484a; background: #2c2c2e; }
            QCheckBox::indicator:checked { background: #0a84ff; }
            QProgressBar { border: none; border-radius: 5px; background-color: #2c2c2e; color: transparent; }
            QProgressBar::chunk { background-color: #32d74b; border-radius: 5px; }
        """)
        self.main_container.setObjectName("MainContainer")
        
        layout = QVBoxLayout(self.main_container)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # --- Üst Kapatma ve Başlık ---
        header_layout = QHBoxLayout()
        header = QLabel("Vizia Lens Stüdyo")
        header.setStyleSheet("font-weight: bold; font-size: 15px; color: #0a84ff;")
        btn_close = QPushButton("X")
        btn_close.setFixedSize(26, 26)
        btn_close.setStyleSheet("background-color: #ff453a; color: white; border: none; border-radius: 13px; padding: 0;")
        btn_close.clicked.connect(self.hide)
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        layout.addLayout(header_layout)

        # --- SEKMELER (TABS) ---
        self.tabs = QTabWidget()
        self.tab_scan = QWidget()
        self.tab_workflow = QWidget()
        self.tabs.addTab(self.tab_scan, "Canlı Tarama")
        self.tabs.addTab(self.tab_workflow, "Dosya Workflow")
        layout.addWidget(self.tabs)

        self.build_scan_tab()
        self.build_workflow_tab()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.main_container)
        self.resize(380, 520)

    def build_scan_tab(self):
        layout = QVBoxLayout(self.tab_scan)
        layout.setContentsMargins(0, 10, 0, 0)

        self.btn_quick = QPushButton(f"Tek Tıkla Tarama: {'AÇIK' if self.plugin.quick_scan_enabled else 'KAPALI'}")
        self.btn_quick.clicked.connect(self.toggle_quick_mode)
        layout.addWidget(self.btn_quick)
        
        lbl_lang = QLabel("Yüklü Dil Paketleri (Tesseract)")
        lbl_lang.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(lbl_lang)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.lang_list_layout = QVBoxLayout(scroll_widget)
        self.lang_list_layout.setContentsMargins(0,0,0,0)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.dl_progress = QProgressBar()
        self.dl_progress.setFixedHeight(6)
        self.dl_progress.hide()
        layout.addWidget(self.dl_progress)

    def build_workflow_tab(self):
        layout = QVBoxLayout(self.tab_workflow)
        layout.setContentsMargins(0, 10, 0, 0)

        # Dosya Seçimi
        self.btn_select_file = QPushButton("📁 Dosya Seç (PDF, DOCX, TXT)")
        self.btn_select_file.setStyleSheet("padding: 15px; border-style: dashed; border-width: 2px; border-color: #48484a;")
        self.btn_select_file.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select_file)

        self.lbl_selected_file = QLabel("Seçilen Dosya: Yok")
        self.lbl_selected_file.setStyleSheet("color: #a1a1a6; font-size: 11px;")
        layout.addWidget(self.lbl_selected_file)

        # Ayarlar Satırı
        settings_layout = QHBoxLayout()
        
        self.combo_format = QComboBox()
        self.combo_format.addItems(["Çıktı: DOCX (Önerilen)", "Çıktı: PDF", "Çıktı: TXT"])
        settings_layout.addWidget(self.combo_format)

        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Çeviri Yapma", "İngilizce (en)", "Türkçe (tr)", "Almanca (de)", "Fransızca (fr)", "İspanyolca (es)", "Rusça (ru)"])
        settings_layout.addWidget(self.combo_lang)
        
        layout.addLayout(settings_layout)

        # Görsel Ayarı
        self.chk_images = QCheckBox("Görselleri orijinal dosyadan kopyala ve dahil et")
        self.chk_images.setChecked(True)
        layout.addWidget(self.chk_images)

        layout.addStretch()

        # İşlem Geri Bildirimi
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #32d74b; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        self.wf_progress = QProgressBar()
        self.wf_progress.setFixedHeight(8)
        self.wf_progress.setValue(0)
        self.wf_progress.hide()
        layout.addWidget(self.wf_progress)

        # Başlat Butonu
        self.btn_start_wf = QPushButton("🚀 Dönüşümü Başlat")
        self.btn_start_wf.setObjectName("PrimaryBtn")
        self.btn_start_wf.clicked.connect(self.start_workflow)
        layout.addWidget(self.btn_start_wf)

    # --- CANLI TARAMA MANTIĞI ---
    def toggle_quick_mode(self):
        self.plugin.quick_scan_enabled = not self.plugin.quick_scan_enabled
        self.btn_quick.setText(f"Tek Tıkla Tarama: {'AÇIK' if self.plugin.quick_scan_enabled else 'KAPALI'}")
        self.plugin.config["quick_scan"] = self.plugin.quick_scan_enabled
        save_config(self.plugin.config)

    def refresh_languages(self):
        for i in reversed(range(self.lang_list_layout.count())): 
            self.lang_list_layout.itemAt(i).widget().setParent(None)
            
        langs = {"tur": "Türkçe", "eng": "İngilizce", "deu": "Almanca", "rus": "Rusça", "fra": "Fransızca"}
        for code, name in langs.items():
            row = QFrame()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0,0,5,0)
            lbl = QLabel(name)
            is_installed = self.lang_manager.is_installed(code)
            
            btn = QPushButton("Sil" if is_installed else "İndir")
            btn.setFixedWidth(60)
            if is_installed:
                btn.setStyleSheet("color: #ff453a; font-size: 11px;")
                btn.clicked.connect(lambda c=False, lc=code: self.lang_manager.delete_language(lc) or self.refresh_languages())
            else:
                btn.setStyleSheet("color: #32d74b; font-size: 11px;")
                btn.clicked.connect(lambda c=False, lc=code: self.download_lang(lc))
                
            row_layout.addWidget(lbl)
            row_layout.addStretch()
            row_layout.addWidget(btn)
            self.lang_list_layout.addWidget(row)

    def download_lang(self, code):
        self.dl_progress.show()
        self.downloader = LanguageDownloader(code, self.lang_manager.tessdata_dir)
        self.downloader.progress.connect(self.dl_progress.setValue)
        self.downloader.finished.connect(lambda: self.dl_progress.hide() or self.refresh_languages())
        self.downloader.start()

    # --- DOSYA WORKFLOW MANTIĞI ---
    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "İşlenecek Dosyayı Seç", "", "Desteklenenler (*.pdf *.docx *.txt)")
        if path:
            self.selected_file = path
            name = os.path.basename(path)
            self.lbl_selected_file.setText(f"Seçilen: {name if len(name)<30 else name[:27]+'...'}")
            self.lbl_status.setText("")

    def start_workflow(self):
        if not self.selected_file:
            self.lbl_status.setText("Lütfen önce bir dosya seçin!")
            self.lbl_status.setStyleSheet("color: #ff453a;")
            return

        self.btn_start_wf.setEnabled(False)
        self.wf_progress.show()
        self.wf_progress.setValue(0)
        self.lbl_status.setStyleSheet("color: #0a84ff;")
        
        fmt_map = {"Çıktı: DOCX (Önerilen)": "docx", "Çıktı: PDF": "pdf", "Çıktı: TXT": "txt"}
        t_fmt = fmt_map[self.combo_format.currentText()]
        
        lang_text = self.combo_lang.currentText()
        t_lang = lang_text[lang_text.find("(")+1 : lang_text.find(")")] if "(" in lang_text else ""

        inc_images = self.chk_images.isChecked()

        # Arka plan işçisini (Orkestratör) ateşle
        self.worker = ViziaWorkflowOrchestrator(self.selected_file, t_fmt, t_lang, inc_images, self.plugin.translator)
        self.worker.progress.connect(self.update_wf_progress)
        self.worker.finished.connect(self.wf_finished)
        self.worker.start()

    def update_wf_progress(self, val, msg):
        self.wf_progress.setValue(val)
        self.lbl_status.setText(msg)

    def wf_finished(self, success, result):
        self.btn_start_wf.setEnabled(True)
        self.wf_progress.hide()
        if success:
            self.lbl_status.setStyleSheet("color: #32d74b; font-weight: bold;")
            self.lbl_status.setText("✅ Başarıyla Kaydedildi!")
            os.startfile(os.path.dirname(result)) # Dosyanın olduğu klasörü aç
        else:
            self.lbl_status.setStyleSheet("color: #ff453a;")
            self.lbl_status.setText(f"Hata: {result}")

    # Pencereleri sürüklenebilir yapar
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
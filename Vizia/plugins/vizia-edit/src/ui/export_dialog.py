"""Export ayarları dialog'u"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QComboBox, QSpinBox, QCheckBox,
                             QPushButton, QFileDialog, QLineEdit, QProgressBar,
                             QGroupBox)
from PyQt5.QtCore import Qt
from ..core.export import ExportSettings, ExportEngine
from ..core.timeline import Timeline
from ..utils.constants import EXPORT_PRESETS, EXPORT_FPS, EXPORT_FORMATS
from ..utils.signals import export_signals


class ExportDialog(QDialog):
    """Export ayarları ve ilerleme dialog'u"""
    
    def __init__(self, timeline: Timeline, parent=None):
        super().__init__(parent)
        self.timeline = timeline
        self.export_engine = ExportEngine()
        self.settings = ExportSettings()
        
        self.setWindowTitle("Video Export")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        
        # Çıktı dosyası
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Çıktı dosyası yolu...")
        output_layout.addWidget(QLabel("Çıktı:"))
        output_layout.addWidget(self.output_edit)
        
        browse_btn = QPushButton("Gözat")
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_btn)
        
        layout.addLayout(output_layout)
        
        # Ayarlar
        settings_group = QGroupBox("Export Ayarları")
        settings_layout = QFormLayout()
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(EXPORT_FORMATS)
        settings_layout.addRow("Format:", self.format_combo)
        
        # Çözünürlük
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(list(EXPORT_PRESETS.keys()) + ["Özel"])
        settings_layout.addRow("Çözünürlük:", self.resolution_combo)
        
        # FPS
        self.fps_combo = QComboBox()
        self.fps_combo.addItems([str(fps) for fps in EXPORT_FPS])
        self.fps_combo.setCurrentText("30")
        settings_layout.addRow("FPS:", self.fps_combo)
        
        # Bitrate
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1000, 50000)
        self.bitrate_spin.setValue(8000)
        self.bitrate_spin.setSuffix(" kbps")
        settings_layout.addRow("Bitrate:", self.bitrate_spin)
        
        # Hardware encoding
        self.hw_encode_check = QCheckBox("Hardware Encoding (NVENC/QSV)")
        self.hw_encode_check.setChecked(True)
        settings_layout.addRow("", self.hw_encode_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_btn = QPushButton("Export Başlat")
        self.export_btn.setObjectName("primary")
        self.export_btn.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_btn)
        
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def connect_signals(self):
        """Export sinyal bağlantıları"""
        export_signals.export_started.connect(self.on_export_started)
        export_signals.export_progress.connect(self.on_export_progress)
        export_signals.export_completed.connect(self.on_export_completed)
        export_signals.export_failed.connect(self.on_export_failed)
    
    def browse_output(self):
        """Çıktı dosyası seç"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Çıktı Dosyası Seç",
            "",
            "MP4 Video (*.mp4);;MOV Video (*.mov);;WebM Video (*.webm)"
        )
        if filepath:
            self.output_edit.setText(filepath)
    
    def start_export(self):
        """Export'u başlatır"""
        output_path = self.output_edit.text()
        if not output_path:
            return
        
        # Ayarları hazırla
        self.settings.output_path = output_path
        self.settings.format = self.format_combo.currentText()
        
        # Çözünürlük
        res_text = self.resolution_combo.currentText()
        if res_text in EXPORT_PRESETS:
            preset = EXPORT_PRESETS[res_text]
            self.settings.resolution = (preset['width'], preset['height'])
        
        self.settings.fps = int(self.fps_combo.currentText())
        self.settings.bitrate = self.bitrate_spin.value()
        self.settings.hardware_encoding = self.hw_encode_check.isChecked()
        
        # Export başlat
        self.export_engine.export_timeline(
            self.timeline,
            self.settings,
            self.on_progress_update
        )
    
    def on_progress_update(self, progress: int):
        """İlerleme güncellemesi"""
        self.progress_bar.setValue(progress)
    
    def on_export_started(self):
        """Export başladığında"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.export_btn.setEnabled(False)
    
    def on_export_progress(self, progress: int):
        """İlerleme güncellemesi (sinyal)"""
        self.progress_bar.setValue(progress)
    
    def on_export_completed(self, filepath: str):
        """Export tamamlandığında"""
        self.progress_bar.setValue(100)
        self.export_btn.setEnabled(True)
        self.accept()
    
    def on_export_failed(self, error: str):
        """Export başarısız olduğunda"""
        self.export_btn.setEnabled(True)
        print(f"Export başarısız: {error}")

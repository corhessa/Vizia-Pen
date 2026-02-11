"""Seçili klip özellikleri paneli"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                             QSlider, QDoubleSpinBox, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
from ..core.timeline import Clip


class PropertiesPanel(QWidget):
    """Klip özelliklerini düzenleme paneli"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_clip = None
        self.setup_ui()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Özellikler")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Transform
        transform_group = QGroupBox("Dönüşüm")
        transform_layout = QFormLayout()
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        transform_layout.addRow("Opaklık:", self.opacity_slider)
        
        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(-360, 360)
        self.rotation_spin.setSuffix("°")
        transform_layout.addRow("Rotasyon:", self.rotation_spin)
        
        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)
        
        # Audio
        audio_group = QGroupBox("Ses")
        audio_layout = QFormLayout()
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)
        audio_layout.addRow("Ses Seviyesi:", self.volume_slider)
        
        self.mute_check = QCheckBox("Sessiz")
        audio_layout.addRow("", self.mute_check)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        layout.addStretch()
        
        self.info_label = QLabel("Klip seçilmedi")
        self.info_label.setObjectName("secondary")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
    
    def set_clip(self, clip: Clip):
        """Düzenlenecek klip'i ayarlar"""
        self.current_clip = clip
        if clip:
            self.opacity_slider.setValue(int(clip.opacity * 100))
            self.rotation_spin.setValue(clip.rotation)
            self.volume_slider.setValue(int(clip.volume * 100))
            self.mute_check.setChecked(clip.muted)
            self.info_label.setText(f"{clip.name}\n{clip.duration:.2f}s")
        else:
            self.info_label.setText("Klip seçilmedi")

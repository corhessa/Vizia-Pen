"""Ses mixer ve waveform görüntüleme"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QPushButton)
from PyQt5.QtCore import Qt


class AudioMixer(QWidget):
    """Ses karıştırma ve seviye kontrolü"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Ses Mixer")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Master volume
        master_layout = QHBoxLayout()
        master_layout.addWidget(QLabel("Master:"))
        
        master_slider = QSlider(Qt.Vertical)
        master_slider.setRange(0, 100)
        master_slider.setValue(100)
        master_slider.setMinimumHeight(150)
        master_layout.addWidget(master_slider)
        
        layout.addLayout(master_layout)
        
        # TODO: Track-bazlı ses kontrolleri
        # TODO: Waveform görselleştirmesi
        
        layout.addStretch()

"""Metin/altyazı düzenleme widget'ı"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QComboBox, QSpinBox,
                             QColorDialog, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class TextEditor(QWidget):
    """Metin ve altyazı ekleme widget'ı"""
    
    text_added = pyqtSignal(dict)  # Metin özellikleri
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_color = "#ffffff"
        self.setup_ui()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Metin Ekle")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Metin içeriği
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Metin içeriğini girin...")
        self.text_edit.setMaximumHeight(100)
        layout.addWidget(QLabel("İçerik:"))
        layout.addWidget(self.text_edit)
        
        # Font ayarları
        form = QFormLayout()
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Times New Roman", "Courier New", "Verdana"])
        form.addRow("Font:", self.font_combo)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(48)
        form.addRow("Boyut:", self.size_spin)
        
        color_layout = QHBoxLayout()
        self.color_label = QLabel("      ")
        self.color_label.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid #fff;")
        color_btn = QPushButton("Renk Seç")
        color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(color_btn)
        form.addRow("Renk:", color_layout)
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Center", "Top", "Bottom"])
        form.addRow("Pozisyon:", self.position_combo)
        
        layout.addLayout(form)
        
        # Ekle butonu
        add_btn = QPushButton("Timeline'a Ekle")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_text)
        layout.addWidget(add_btn)
        
        layout.addStretch()
    
    def choose_color(self):
        """Renk seçim dialog'unu açar"""
        color = QColorDialog.getColor(QColor(self.text_color), self)
        if color.isValid():
            self.text_color = color.name()
            self.color_label.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid #fff;")
    
    def add_text(self):
        """Metin ekler"""
        text_data = {
            'content': self.text_edit.toPlainText(),
            'font': self.font_combo.currentText(),
            'size': self.size_spin.value(),
            'color': self.text_color,
            'position': self.position_combo.currentText().lower()
        }
        self.text_added.emit(text_data)

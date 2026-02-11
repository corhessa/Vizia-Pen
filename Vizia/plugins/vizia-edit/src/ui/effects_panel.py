"""Efekt ve filtre seçim paneli"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                             QPushButton, QGroupBox, QListWidgetItem)
from ..core.effects import get_available_effects


class EffectsPanel(QWidget):
    """Efekt seçim ve uygulama paneli"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Efektler")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Kategoriler ve efektler
        effects = get_available_effects()
        
        for category, effect_list in effects.items():
            group = QGroupBox(category)
            group_layout = QVBoxLayout()
            
            list_widget = QListWidget()
            for effect in effect_list:
                list_widget.addItem(effect)
            
            group_layout.addWidget(list_widget)
            
            apply_btn = QPushButton("Uygula")
            group_layout.addWidget(apply_btn)
            
            group.setLayout(group_layout)
            layout.addWidget(group)
        
        layout.addStretch()

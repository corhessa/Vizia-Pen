# ui/dialogs.py

import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QFrame, 
                             QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    """ Dosya yollarını EXE uyumlu hale getirir """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # [DÜZELTME] setFixedSize iptal edildi, minimumSize ile Windows hatası giderildi.
        self.setMinimumSize(400, 520)
        self.resize(400, 520)
        self.old_pos = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) 

        # --- BEYAZ KART (Ana Taşıyıcı) ---
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 20px;
                border: 1px solid #f0f0f0;
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI', sans-serif;
                border: none;
            }
        """)
        
        # Kartın Gölgesi
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)

        # İçerik Düzeni
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(30, 45, 30, 45)
        content_layout.setSpacing(15)

        # 1. LOGO ALANI
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Logo yolunu bulmak için base_path hesaplama (Dialog dosyasının konumuna göre)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = resource_path("Vizia/Assets/VIZIA.png") 
        if not os.path.exists(logo_path):
            logo_path = os.path.join(base_path, "Assets", "VIZIA.ico")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Logoyu biraz büyüttük ve netleştirdik
            scaled_pixmap = pixmap.scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("V")
            logo_label.setStyleSheet("font-size: 80px; font-weight: bold; color: #000;")
        content_layout.addWidget(logo_label, 0, Qt.AlignHCenter)

        # 2. BAŞLIK
        title = QLabel("VIZIA PEN")
        title.setStyleSheet("font-size: 28px; font-weight: 900; letter-spacing: 0.5px; color: #111;")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)
        
        content_layout.addStretch()

        # 3. AÇIKLAMA METNİ
        # Buraya "Icons by Flaticon" yazısını ekledim (hafif silik #aaa ve küçük 10px)
        aciklama_metni = """
        <p style='line-height: 160%; font-size: 14px; color: #444;'>
        Vizia Pen, ekran üzerinde <b>özgürce</b> çizim yapmanızı ve <b>fikirlerinizi</b> 
        anında görselleştirmenizi sağlayan <b>profesyonel</b> bir araçtır.
        </p>
        <br>
        <p style='color: #aaa; font-size: 10px; margin-bottom: 5px;'>
        Icons by Flaticon
        </p>
        <p style='color: #999; font-size: 12px;'>
        Geliştirici: <b>Corhessa</b> &nbsp;|&nbsp; v1.0
        </p>
        """
        info_label = QLabel(aciklama_metni)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setTextFormat(Qt.RichText)
        content_layout.addWidget(info_label)

        content_layout.addSpacing(25)

        # 4. PREMİUM 'KAPAT' BUTONU
        btn_ok = QPushButton("Kapat")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFixedSize(160, 44) 
        
        btn_ok.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007aff, stop:1 #005bb5);
                color: #ffffff;
                border: none;
                border-radius: 22px;
                font-family: 'Segoe UI';
                font-weight: 700;
                font-size: 14px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0088ff, stop:1 #0066cc);
            }
            QPushButton:pressed {
                background-color: #004494;
                padding-top: 2px;
            }
        """)
        
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(15)
        btn_shadow.setColor(QColor(0, 122, 255, 80)) # Mavi gölge
        btn_shadow.setOffset(0, 5)
        btn_ok.setGraphicsEffect(btn_shadow)
        
        content_layout.addWidget(btn_ok, 0, Qt.AlignHCenter)

    # Pencere Sürükleme
    def mousePressEvent(self, event):
        # [DÜZELTME] Sürükleme işlemi sırasında butonun çalışmasını engellememesi için hitbox kontrolü
        child = self.childAt(event.pos())
        if isinstance(child, QPushButton):
            return  # Eğer tıklanan yer bir butonsa sürükleme eventini çalıştırma
            
        if event.button() == Qt.LeftButton: 
            self.old_pos = event.globalPos()
            
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event): 
        self.old_pos = None
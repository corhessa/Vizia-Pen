from PyQt5.QtWidgets import QTextEdit, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize
from PyQt5.QtGui import QFont, QFontMetrics, QColor, QTextCursor

class ViziaTextItem(QTextEdit):
    """
    Vizia Pen için modern, otomatik boyutlanan ve Overlay ile bütünleşik metin aracı.
    Klavye kısayolları (3. madde) hariç tutulmuştur; tamamen odak (focus) mantığıyla çalışır.
    """
    def __init__(self, owner, creation_mode, initial_color):
        super().__init__(owner) # Overlay'in bir çocuğu olarak başlatılır
        self.owner = owner
        self.creation_mode = creation_mode
        self.text_color = initial_color
        self.is_dragging = False
        self.drag_start_pos = None
        
        # Temel Ayarlar
        self.setContextMenuPolicy(Qt.NoContextMenu) # Sağ tık menüsünü kapat
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Başlangıç stili ve boyutu
        self.setFont(QFont('Segoe UI', 16, QFont.Bold))
        self.resize(50, 40) # Başlangıçta minik bir kare
        self.show()
        self.setFocus() # Doğrudan yazmaya başla
        
        # Sinyaller
        self.textChanged.connect(self.adjust_size_dynamically)
        
        # İlk stil ayarını yap
        self.update_style(editing=True)

    def adjust_size_dynamically(self):
        """Metin içeriğine göre kutunun boyutunu milimetrik ayarlar."""
        font = self.font()
        font_metrics = QFontMetrics(font)
        text = self.toPlainText()
        
        # Satırları analiz et
        lines = text.split('\n')
        max_width = 0
        for line in lines:
            rect = font_metrics.boundingRect(line)
            if rect.width() > max_width:
                max_width = rect.width()
        
        # Genişlik: En uzun satır + padding
        # Yükseklik: Satır sayısı * Satır yüksekliği + padding
        new_width = max(50, max_width + 40)
        line_height = font_metrics.lineSpacing()
        new_height = max(40, (len(lines) * line_height) + 30)
        
        self.resize(new_width, new_height)

    def update_style(self, editing):
        """Düzenleme modu ve Statik mod arasındaki stil geçişini yönetir."""
        if editing:
            # Düzenleme Modu: Hafif arka plan, kesikli kenarlık
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: rgba(255, 255, 255, 30);
                    color: {self.text_color.name()};
                    border: 1.5px dashed #007aff;
                    border-radius: 8px;
                    padding: 5px;
                }}
            """)
        else:
            # Statik Mod: Tamamen şeffaf, kenarlık yok
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: transparent;
                    color: {self.text_color.name()};
                    border: none;
                    padding: 5px;
                }}
            """)

    def focusOutEvent(self, event):
        """Kullanıcı başka bir yere tıkladığında (Odak kaybı)."""
        super().focusOutEvent(event)
        
        # Eğer metin kutusu boşsa, kullanıcı vazgeçmiş demektir; sil.
        if not self.toPlainText().strip():
            self.deleteLater()
            # Overlay listesinden de temizlemek gerekir (bunu Overlay tarafında handle etmek daha sağlıklı ama burası oto-temizlik yapar)
        else:
            # Doluysa düzenleme modunu kapat
            self.setReadOnly(True)
            self.update_style(editing=False)
            # İmleci (Selection) temizle ki mavi seçim kalmasın
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event):
        """Çift tıklama ile tekrar düzenleme moduna geç."""
        if self.isReadOnly():
            self.setReadOnly(False)
            self.update_style(editing=True)
            self.setFocus()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """Sürükleme veya imleç konumlandırma mantığı."""
        if event.button() == Qt.LeftButton:
            if self.isReadOnly():
                # Sadece okunabilir moddayken sürüklemeye izin ver
                self.is_dragging = True
                self.drag_start_pos = event.pos()
            else:
                # Düzenleme modundaysa normal metin seçimi yap
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Mouse hareketi."""
        if self.is_dragging and self.isReadOnly():
            # Widget'ı taşı
            delta = event.pos() - self.drag_start_pos
            self.move(self.pos() + delta)
            # Overlay'i güncellemeye gerek yok, widget zaten overlay'in çocuğu
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Sürüklemeyi bitir."""
        self.is_dragging = False
        super().mouseReleaseEvent(event)
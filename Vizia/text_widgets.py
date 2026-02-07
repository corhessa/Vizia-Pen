from PyQt5.QtWidgets import QTextEdit, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QColor, QTextCursor

class ViziaTextItem(QTextEdit):
    """
    Vizia Pen için modern, otomatik boyutlanan ve Overlay ile bütünleşik metin aracı.
    Crash sorunları için 'delete_requested' sinyali eklendi.
    """
    # Kendisini argüman olarak gönderen bir sinyal tanımlıyoruz
    delete_requested = pyqtSignal(object)

    def __init__(self, owner, creation_mode, initial_color):
        super().__init__(owner)
        self.owner = owner
        self.creation_mode = creation_mode
        self.text_color = initial_color
        self.is_dragging = False
        self.drag_start_pos = None
        
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.setFont(QFont('Segoe UI', 16, QFont.Bold))
        self.resize(50, 40)
        self.show()
        
        # Kritik: Oluşur oluşmaz odağı alması lazım
        self.setFocus()
        self.activateWindow()
        
        self.textChanged.connect(self.adjust_size_dynamically)
        self.update_style(editing=True)

    def adjust_size_dynamically(self):
        font = self.font()
        font_metrics = QFontMetrics(font)
        text = self.toPlainText()
        
        lines = text.split('\n')
        max_width = 0
        for line in lines:
            rect = font_metrics.boundingRect(line)
            if rect.width() > max_width:
                max_width = rect.width()
        
        new_width = max(50, max_width + 40)
        line_height = font_metrics.lineSpacing()
        new_height = max(40, (len(lines) * line_height) + 30)
        
        self.resize(new_width, new_height)

    def update_style(self, editing):
        if editing:
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
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: transparent;
                    color: {self.text_color.name()};
                    border: none;
                    padding: 5px;
                }}
            """)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        
        # Eğer metin kutusu boşsa, Overlay'e "beni sil" sinyali gönder
        if not self.toPlainText().strip():
            self.delete_requested.emit(self)
        else:
            self.setReadOnly(True)
            self.update_style(editing=False)
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event):
        if self.isReadOnly():
            self.setReadOnly(False)
            self.update_style(editing=True)
            self.setFocus()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isReadOnly():
                self.is_dragging = True
                self.drag_start_pos = event.pos()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.isReadOnly():
            delta = event.pos() - self.drag_start_pos
            self.move(self.pos() + delta)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        super().mouseReleaseEvent(event)
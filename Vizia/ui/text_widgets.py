from PyQt5.QtWidgets import (QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, 
                             QToolButton, QApplication, QListWidget, QListWidgetItem, QLabel, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QColor, QFontDatabase, QTextCursor

# --- 1. GÜVENLİ SATIR GÖRÜNÜMÜ (WIDGET TABANLI) ---
class FontRowWidget(QWidget):
    def __init__(self, font_name):
        super().__init__()
        self.setAttribute(Qt.WA_TransparentForMouseEvents) 
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        self.lbl_name = QLabel(font_name)
        self.lbl_name.setStyleSheet("color: white; font-family: 'Segoe UI'; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(self.lbl_name)
        
        self.lbl_preview = QLabel("Vizia")
        self.lbl_preview.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_preview.setStyleSheet(f"color: rgba(255, 255, 255, 150); font-family: '{font_name}'; font-size: 16px; border: none; background: transparent;")
        layout.addWidget(self.lbl_preview)

# --- 2. GENİŞLEYEN TOOLBAR ---
class TextFormatToolbar(QWidget):
    def __init__(self, parent_item):
        # KRİTİK DÜZELTME: Ana pencereyi parent olarak atıyoruz ki hep üstte kalsın.
        super().__init__(parent_item.window())
        self.target = parent_item
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.top_frame = QWidget()
        self.top_frame.setObjectName("TopFrame")
        self.setStyleSheet("""
            QWidget#TopFrame { background-color: #2c2c2e; border: 1px solid #48484a; border-radius: 10px; }
            QListWidget { background-color: #2c2c2e; border: 1px solid #48484a; border-top: none; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }
            QPushButton { background-color: #1c1c1e; color: white; border: 1px solid #3a3a3c; border-radius: 6px; padding: 5px; text-align: left; padding-left: 10px; }
            QPushButton:hover { border: 1px solid #0a84ff; }
            QSpinBox { background-color: #1c1c1e; color: white; border: 1px solid #3a3a3c; border-radius: 6px; padding: 5px; }
            QToolButton { background-color: transparent; border-radius: 6px; color: #e5e5e7; font-weight: bold; font-size: 16px; min-width: 30px; }
            QToolButton:checked { background-color: #0a84ff; color: white; }
            QToolButton:hover { background-color: #3a3a3c; }
        """)
        
        h_layout = QHBoxLayout(self.top_frame)
        h_layout.setContentsMargins(10, 5, 10, 5)
        h_layout.setSpacing(8)

        self.btn_font = QPushButton("Segoe UI")
        self.btn_font.setFixedWidth(180)
        self.btn_font.setFocusPolicy(Qt.NoFocus) # Odak çalmasını engelle
        self.btn_font.clicked.connect(self.toggle_list)
        h_layout.addWidget(self.btn_font)

        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 200); self.spin_size.setValue(16); self.spin_size.setFixedWidth(60)
        self.spin_size.valueChanged.connect(lambda v: (self.target.set_font_size(v), self.update_position(), self.target.setFocus()))
        h_layout.addWidget(self.spin_size)

        self.btn_b = QToolButton(); self.btn_b.setText("B"); self.btn_b.setCheckable(True)
        self.btn_b.setFocusPolicy(Qt.NoFocus) # Odak çalmasını engelle
        self.btn_b.clicked.connect(lambda c: (self.target.set_font_weight(c), self.target.setFocus()))
        h_layout.addWidget(self.btn_b)
        
        self.btn_i = QToolButton(); self.btn_i.setText("I"); self.btn_i.setCheckable(True)
        self.btn_i.setFocusPolicy(Qt.NoFocus) # Odak çalmasını engelle
        self.btn_i.clicked.connect(lambda c: (self.target.set_font_italic(c), self.target.setFocus()))
        h_layout.addWidget(self.btn_i)

        self.main_layout.addWidget(self.top_frame)

        self.font_list = QListWidget()
        self.font_list.setFixedHeight(250)
        self.font_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.font_list.setFocusPolicy(Qt.NoFocus)
        self.font_list.hide() 
        
        pop_fonts = ["Segoe UI", "Arial", "Calibri", "Roboto", "Verdana", "Tahoma", "Times New Roman", 
                     "Consolas", "Impact", "Comic Sans MS", "Ink Free", "Georgia", "Courier New"]
        db = QFontDatabase(); installed = db.families()
        
        for f in pop_fonts:
            if f in installed:
                item = QListWidgetItem(self.font_list)
                item.setSizeHint(QSize(0, 40)) 
                row_widget = FontRowWidget(f)
                self.font_list.setItemWidget(item, row_widget)
                item.setData(Qt.UserRole, f) 

        self.font_list.itemClicked.connect(self.on_font_click)
        self.main_layout.addWidget(self.font_list)

    def toggle_list(self):
        if self.font_list.isVisible():
            self.font_list.hide()
        else:
            self.font_list.show()
        self.adjustSize()
        QTimer.singleShot(10, self.update_position)

    def on_font_click(self, item):
        font_name = item.data(Qt.UserRole)
        self.btn_font.setText(font_name)
        self.target.set_font_family(font_name)
        self.toggle_list() 
        self.target.setFocus() 

    def update_position(self):
        if not self.target or not self.target.isVisible(): 
            self.hide(); return
        try:
            target_pos = self.target.mapToGlobal(self.target.rect().topLeft())
            self.move(target_pos.x(), target_pos.y() - self.height() - 10)
            self.show()
        except: self.hide()

# --- 3. ANA METİN KUTUSU ---
class ViziaTextItem(QTextEdit):
    delete_requested = pyqtSignal(object)

    def __init__(self, owner, creation_mode, initial_color):
        super().__init__(owner)
        self.owner = owner; self.creation_mode = creation_mode; self.text_color = initial_color
        self.is_dragging = False; self.drag_start_pos = None
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.current_font = QFont('Segoe UI', 16)
        self.setFont(self.current_font); self.setTextColor(self.text_color)
        self.resize(100, 50); self.show()
        
        self.format_toolbar = TextFormatToolbar(self)
        self.setFocus(); self.activateWindow()
        self.textChanged.connect(self.adjust_size_dynamically)
        self.update_style(editing=True)

    def contextMenuEvent(self, event):
        # KRİTİK DÜZELTME: Parent kaldırıldı (bağımsız pencere), her zaman en üstte kalması sağlandı
        menu = QMenu()
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowStaysOnTopHint | Qt.Popup) 
        menu.setStyleSheet("""
            QMenu { background-color: #2c2c2e; color: white; border: 1px solid #48484a; border-radius: 8px; padding: 5px; font-family: 'Segoe UI'; font-size: 13px; }
            QMenu::item { padding: 6px 25px; border-radius: 4px; }
            QMenu::item:selected { background-color: #007aff; }
            QMenu::separator { height: 1px; background-color: #48484a; margin: 4px 10px; }
        """)
        a_front = menu.addAction("Öne Getir")
        a_back = menu.addAction("Geriye Gönder")
        menu.addSeparator()
        a_dup = menu.addAction("Çoğalt")
        a_del = menu.addAction("Sil")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == a_front: self.raise_()
        elif action == a_back: self.lower()
        elif action == a_del:
            self.format_toolbar.close()
            self.delete_requested.emit(self)
        elif action == a_dup:
            new_item = ViziaTextItem(self.owner, self.creation_mode, self.text_color)
            new_item.setHtml(self.toHtml())
            new_item.current_font = self.current_font
            new_item.setFont(self.current_font)
            new_item.move(self.x() + 20, self.y() + 20)
            new_item.adjust_size_dynamically()
            new_item.delete_requested.connect(lambda w: [self.owner.active_layer.remove_widget_item(w), w.deleteLater()])
            self.owner.active_layer.add_widget_item(new_item, 'text')

    def set_font_family(self, name):
        self.current_font.setFamily(name); self.setFont(self.current_font); self.adjust_size_dynamically()
    def set_font_size(self, size):
        self.current_font.setPointSize(size); self.setFont(self.current_font); self.adjust_size_dynamically()
    def set_font_weight(self, b):
        self.current_font.setBold(b); self.setFont(self.current_font); self.adjust_size_dynamically()
    def set_font_italic(self, i):
        self.current_font.setItalic(i); self.setFont(self.current_font); self.adjust_size_dynamically()

    def adjust_size_dynamically(self):
        fm = QFontMetrics(self.font())
        lines = self.toPlainText().split('\n')
        max_w = 0
        for l in lines:
            w = fm.boundingRect(l).width()
            if w > max_w: max_w = w
        self.resize(max(80, max_w + 40), max(40, (len(lines) * fm.lineSpacing()) + 30))
        if self.format_toolbar.isVisible(): self.format_toolbar.update_position()

    def update_style(self, editing):
        if editing:
            self.setStyleSheet(f"background: rgba(255,255,255,20); color: {self.text_color.name()}; border: 1.5px dashed #007aff; border-radius: 8px; padding: 5px;")
            self.format_toolbar.update_position()
        else:
            self.setStyleSheet(f"""
                background: transparent; 
                color: {self.text_color.name()}; 
                border: none; 
                padding: 5px;
                selection-background-color: transparent;
                selection-color: {self.text_color.name()};
            """)
            self.format_toolbar.hide()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        QTimer.singleShot(150, self.check_focus_loss)

    def check_focus_loss(self):
        if self.hasFocus(): return
        if self.format_toolbar.underMouse(): return
        fw = QApplication.focusWidget()
        if fw and self.format_toolbar.isAncestorOf(fw): return
            
        if not self.toPlainText().strip():
            self.format_toolbar.close()
            self.delete_requested.emit(self)
        else:
            self.setReadOnly(True)
            c = self.textCursor()
            c.clearSelection()
            self.setTextCursor(c)
            self.update_style(editing=False)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setReadOnly(False); self.update_style(editing=True); self.setFocus()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isReadOnly():
            self.is_dragging = True; self.drag_start_pos = event.pos()
        else: super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.is_dragging and self.isReadOnly():
            self.move(self.pos() + (event.pos() - self.drag_start_pos))
        else: super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, e): 
        self.is_dragging = False; super().mouseReleaseEvent(e)
        
    def closeEvent(self, e): 
        self.format_toolbar.close(); super().closeEvent(e)
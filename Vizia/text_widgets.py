from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QTextEdit, QSizeGrip
from PyQt5.QtCore import Qt, QObject, QEvent, QTimer, QPoint
from ui_components import ModernColorPicker

class TextEventFilter(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.parent_widget.edit.isReadOnly():
                self.parent_widget.set_active_mode(True)
                return True
        return False

class StandaloneText(QWidget):
    def __init__(self, owner, creation_mode, initial_color):
        super().__init__()
        self.owner = owner
        self.creation_mode = creation_mode
        self.text_color = initial_color
        self.old_pos = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 100)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.container = QFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.edit = QTextEdit()
        self.edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.edit.setPlaceholderText("Yazmaya başlayın...")
        self.filter = TextEventFilter(self)
        self.edit.installEventFilter(self.filter)
        self.container_layout.addWidget(self.edit)
        self.layout.addWidget(self.container)
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(35)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(2, 5, 2, 5); self.side_layout.setSpacing(8)
        self.btn_palette = QPushButton("🎨")
        self.btn_palette.setFixedSize(28, 28)
        self.btn_palette.setStyleSheet("background: #2c2c2e; border-radius: 14px; border: 1px solid #3a3a3c; font-size: 14px;")
        self.btn_palette.clicked.connect(self.open_text_color_picker)
        self.side_layout.addWidget(self.btn_palette)
        self.btn_ok = QPushButton("✓")
        self.btn_ok.setFixedSize(28, 28)
        self.btn_ok.setStyleSheet("background: #007aff; color: white; border-radius: 14px; font-weight: bold;")
        self.btn_ok.clicked.connect(lambda: self.set_active_mode(False))
        self.side_layout.addWidget(self.btn_ok)
        self.layout.addWidget(self.side_panel)
        self.size_grip = QSizeGrip(self)
        self.layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        self.set_active_mode(True)
        self.show()

    def open_text_color_picker(self):
        picker = ModernColorPicker(self.text_color, self.owner.toolbar.custom_colors, self)
        if picker.exec_():
            self.text_color = picker.selected_color
            self.update_appearance()
        QTimer.singleShot(10, self.owner.force_focus)

    def update_appearance(self):
        f_size = max(14, self.height() // 3.5)
        if self.edit.isReadOnly():
            self.container.setStyleSheet("background: transparent; border: none;")
            self.edit.setStyleSheet(f"""
                color: {self.text_color.name()}; background: transparent; border: none; 
                font-size: {f_size}px; font-weight: 700; font-family: 'Segoe UI', sans-serif;
            """)
            self.side_panel.hide(); self.size_grip.hide()
        else:
            self.container.setStyleSheet("""
                background: rgba(255, 255, 255, 248); border: 2.5px solid #007aff; border-radius: 14px;
            """)
            self.edit.setStyleSheet(f"""
                color: black; background: transparent; border: none; 
                font-size: {f_size - 4}px; font-family: 'Segoe UI', sans-serif;
            """)
            self.side_panel.show(); self.size_grip.show()

    def set_active_mode(self, active):
        self.edit.setReadOnly(not active)
        if not active: self.owner.force_focus()
        self.update_appearance()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.edit.isReadOnly(): self.set_active_mode(True)
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos and not self.edit.isReadOnly():
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPos()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_appearance()
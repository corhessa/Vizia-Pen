"""
Vizia Dark + Purple tema ve stylesheet'ler
"""
from ..utils.constants import COLORS, DEFAULT_FONT, DEFAULT_FONT_SIZE


def get_main_stylesheet() -> str:
    """
    Ana uygulama stylesheet'ini döndürür
    
    Returns:
        QSS stylesheet string'i
    """
    return f"""
    /* Genel Ayarlar */
    * {{
        font-family: '{DEFAULT_FONT}';
        font-size: {DEFAULT_FONT_SIZE}pt;
        color: {COLORS['text_primary']};
    }}
    
    QMainWindow {{
        background-color: {COLORS['background']};
    }}
    
    /* Panel'ler */
    QWidget#panel {{
        background-color: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
    }}
    
    QWidget#surface {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
    }}
    
    /* Butonlar */
    QPushButton {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px 12px;
        color: {COLORS['text_primary']};
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['blue_accent']};
        border-color: {COLORS['blue_accent']};
    }}
    
    QPushButton:pressed {{
        background-color: #005fcc;
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['panel']};
        color: {COLORS['text_secondary']};
    }}
    
    QPushButton#primary {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {COLORS['purple_light']},
                                    stop:1 {COLORS['purple_dark']});
        border: none;
        font-weight: bold;
    }}
    
    QPushButton#primary:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #b97cff,
                                    stop:1 {COLORS['purple_light']});
    }}
    
    QPushButton#danger {{
        background-color: {COLORS['red']};
        border: none;
    }}
    
    QPushButton#danger:hover {{
        background-color: #ff5144;
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {COLORS['panel']};
        border-bottom: 1px solid {COLORS['border']};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['blue_accent']};
    }}
    
    QMenu {{
        background-color: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['blue_accent']};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {COLORS['border']};
        margin: 4px 8px;
    }}
    
    /* Toolbar */
    QToolBar {{
        background-color: {COLORS['panel']};
        border: none;
        border-bottom: 1px solid {COLORS['border']};
        spacing: 4px;
        padding: 4px;
    }}
    
    QToolButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 6px;
    }}
    
    QToolButton:hover {{
        background-color: {COLORS['surface']};
        border-color: {COLORS['border']};
    }}
    
    QToolButton:pressed {{
        background-color: {COLORS['blue_accent']};
    }}
    
    /* Scroll Bar */
    QScrollBar:vertical {{
        background-color: {COLORS['panel']};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['surface']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['border']};
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['panel']};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['surface']};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['border']};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        width: 0px;
        height: 0px;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {COLORS['border']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    /* List Widget */
    QListWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
    }}
    
    QListWidget::item:hover {{
        background-color: {COLORS['panel']};
    }}
    
    QListWidget::item:selected {{
        background-color: {COLORS['blue_accent']};
    }}
    
    /* Tree Widget */
    QTreeWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        outline: none;
    }}
    
    QTreeWidget::item {{
        padding: 4px;
    }}
    
    QTreeWidget::item:hover {{
        background-color: {COLORS['panel']};
    }}
    
    QTreeWidget::item:selected {{
        background-color: {COLORS['blue_accent']};
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        background-color: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
    }}
    
    QTabBar::tab {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 16px;
        margin-right: 2px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['panel']};
        border-bottom: 2px solid {COLORS['purple_accent']};
    }}
    
    QTabBar::tab:hover {{
        background-color: {COLORS['panel']};
    }}
    
    /* Line Edit */
    QLineEdit {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['blue_accent']};
    }}
    
    /* Text Edit */
    QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS['blue_accent']};
    }}
    
    /* Combo Box */
    QComboBox {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['blue_accent']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['blue_accent']};
        border-radius: 4px;
    }}
    
    /* Spin Box */
    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {COLORS['blue_accent']};
    }}
    
    /* Slider */
    QSlider::groove:horizontal {{
        background-color: {COLORS['surface']};
        height: 6px;
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {COLORS['purple_accent']};
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -5px 0;
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {COLORS['purple_light']};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        text-align: center;
        height: 20px;
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLORS['purple_dark']},
                                    stop:1 {COLORS['purple_accent']});
        border-radius: 3px;
    }}
    
    /* Group Box */
    QGroupBox {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: bold;
    }}
    
    QGroupBox::title {{
        color: {COLORS['text_primary']};
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 8px;
        background-color: {COLORS['panel']};
        border-radius: 4px;
    }}
    
    /* Label */
    QLabel {{
        color: {COLORS['text_primary']};
        background-color: transparent;
    }}
    
    QLabel#secondary {{
        color: {COLORS['text_secondary']};
    }}
    
    QLabel#title {{
        font-size: 14pt;
        font-weight: bold;
    }}
    
    /* Check Box */
    QCheckBox {{
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        background-color: {COLORS['surface']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['purple_accent']};
        border-color: {COLORS['purple_accent']};
    }}
    
    /* Radio Button */
    QRadioButton {{
        spacing: 8px;
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COLORS['border']};
        border-radius: 9px;
        background-color: {COLORS['surface']};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {COLORS['purple_accent']};
        border-color: {COLORS['purple_accent']};
    }}
    
    /* Dialog */
    QDialog {{
        background-color: {COLORS['background']};
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['panel']};
        border-top: 1px solid {COLORS['border']};
        color: {COLORS['text_secondary']};
    }}
    
    /* Tool Tip */
    QToolTip {{
        background-color: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px 8px;
        color: {COLORS['text_primary']};
    }}
    """


def get_timeline_stylesheet() -> str:
    """
    Timeline widget için özel stylesheet
    
    Returns:
        QSS stylesheet string'i
    """
    return f"""
    QGraphicsView {{
        background-color: {COLORS['background']};
        border: none;
    }}
    """


def get_title_bar_stylesheet() -> str:
    """
    Custom title bar için stylesheet
    
    Returns:
        QSS stylesheet string'i
    """
    return f"""
    QWidget#titleBar {{
        background-color: {COLORS['panel']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    QLabel#titleLabel {{
        color: {COLORS['text_primary']};
        font-weight: bold;
        font-size: 11pt;
    }}
    
    QPushButton#windowButton {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 6px;
        min-width: 30px;
        max-width: 30px;
        min-height: 30px;
        max-height: 30px;
    }}
    
    QPushButton#windowButton:hover {{
        background-color: {COLORS['surface']};
    }}
    
    QPushButton#closeButton:hover {{
        background-color: {COLORS['red']};
    }}
    """

import sys
import os
import tempfile
from PyQt5.QtCore import QObject, QEvent, Qt, QPoint
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QCursor

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from lens_ui.main_panel import ViziaLensPanel
from lens_ui.result_widget import LensResultWidget
from lens_core.ocr_engine import ViziaOCREngine
from lens_core.translator import ViziaTranslator
from lens_core.config import load_config, save_config

class ViziaPlugin(QObject):
    def __init__(self):
        super().__init__()
        self.name = "Vizia lens & dosya düzenleyici"
        # 1. İKON FIX: Vizia çekmecesi ikonu bulabilsin diye tam dosya yolu (Absolute Path) verdik.
        self.icon = os.path.join(current_dir, "assets", "generative-image.png")
        
        self.panel = None
        self.current_overlay = None
        self.original_finalize = None
        self.button_hooked = False
        
        self.ocr_engine = ViziaOCREngine()
        self.translator = ViziaTranslator()
        
        self.config = load_config()
        self.quick_scan_enabled = self.config.get("quick_scan", False)

    def run(self, overlay):
        self.current_overlay = overlay
        self._hook_right_click(overlay)

        if self.quick_scan_enabled:
            self.start_ocr_scan()
        else:
            self.open_settings_panel()

    def _hook_right_click(self, overlay):
        if self.button_hooked or not hasattr(overlay, 'toolbar') or not overlay.toolbar:
            return
            
        drawer = overlay.toolbar.drawer
        for i in range(drawer.layout.count()):
            widget = drawer.layout.itemAt(i).widget()
            # 2. TOOLTIP FIX: İsim eşleşmesini yakalayıp Tooltip'i zorla istediğimiz yazıya ayarlıyoruz.
            if isinstance(widget, QPushButton) and widget.toolTip() == self.name:
                widget.installEventFilter(self)
                widget.setToolTip("Vizia lens & dosya düzenleyici")
                self.button_hooked = True
                break

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if self.current_overlay:
                self.open_settings_panel()
            return True
        return super().eventFilter(obj, event)

    def open_settings_panel(self):
        if not self.panel:
            self.panel = ViziaLensPanel(self, self.current_overlay)
            # 3. ETKİLEŞİM FIX: Paneli, Vizia'nın "Korunan Arayüzler" listesine ekliyoruz.
            # Artık kalemle üstüne çizilmeyecek, direkt tıklanıp sürüklenebilecek.
            if hasattr(self.current_overlay, 'plugin_windows'):
                self.current_overlay.plugin_windows.register(self.panel)
                
        self.panel.show()
        self.panel.raise_()
        self.panel.activateWindow()

    def start_ocr_scan(self):
        overlay = self.current_overlay
        
        # 1. KESİN ÇÖZÜM: Eğer Fare (Mouse) modundaysa, Vizia'nın kendi Toolbar'ı
        # üzerinden Kalem moduna geçmeye zorluyoruz. Bu sayede 'Hayalet Ekran'
        # bayrağı (WindowTransparentForInput) resmen kapatılır ve ekran tıklanabilir olur.
        if getattr(overlay, 'drawing_mode', '') == "move":
            if overlay.toolbar:
                # Güvenli bir şekilde kalem moduna geçir ve butonları güncelle
                overlay.toolbar.safe_change("pen", overlay.toolbar.btn_draw)
                
        # 2. ÇEKMECE VE TOOLBAR GİZLEME
        if overlay.toolbar:
            overlay.toolbar.hide()
            if hasattr(overlay.toolbar, 'drawer') and overlay.toolbar.drawer:
                overlay.toolbar.drawer.hide()
                overlay.toolbar.drawer.is_open = False 
                
        overlay.drawing = False
        overlay.is_selecting_region = True
        overlay.select_start = QPoint()
        overlay.select_end = QPoint()
        overlay.setCursor(Qt.CrossCursor)
        overlay.show_toast("<center>OCR için metni seçin<br><span style='font-size: 12px; color: #a1a1a6;'>(Sağ Tık: Ayarlar | Çıkmak için ESC)</span></center>")
        
        self.original_finalize = overlay._finalize_screenshot
        overlay._finalize_screenshot = self.ocr_finalize_override
        overlay.update()

    def ocr_finalize_override(self, crop_rect=None):
        overlay = self.current_overlay
        
        overlay._finalize_screenshot = self.original_finalize
        overlay.is_selecting_region = False
        overlay.setCursor(Qt.ArrowCursor)
        
        overlay.update()
        if overlay.toolbar: 
            overlay.toolbar.show()
        
        if crop_rect and crop_rect.width() > 5 and crop_rect.height() > 5:
            overlay.show_toast("Taranıyor...")
            self._process_ocr_image(crop_rect)

    def _process_ocr_image(self, crop_rect):
        from PyQt5.QtWidgets import QApplication
        pixmap = QApplication.primaryScreen().grabWindow(0).copy(crop_rect)
        
        temp_path = os.path.join(tempfile.gettempdir(), "vizia_ocr_temp.png")
        pixmap.save(temp_path, "png")
        
        text = self.ocr_engine.extract_text(temp_path, lang="tur+eng")
        
        if text.strip():
            self.result_widget = LensResultWidget(text, crop_rect, self)
            
            # SONUÇ PANELİ ETKİLEŞİM FIX: Sonuç widget'ını da korunan arayüzlere ekliyoruz.
            if hasattr(self.current_overlay, 'plugin_windows'):
                self.current_overlay.plugin_windows.register(self.result_widget)
                
            self.result_widget.show()
            self.result_widget.raise_()
            self.result_widget.activateWindow()
        else:
            self.current_overlay.show_toast("Metin algılanamadı.")
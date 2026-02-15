import sys
import os
import tempfile
from PyQt5.QtCore import QObject, QEvent, Qt, QPoint
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QCursor

# --- KRİTİK DÜZELTME: Eklenti dizinini Python yoluna ekle ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Artık başındaki noktalar (.) olmadan doğrudan klasör adıyla çağırabiliriz
from lens_ui.main_panel import ViziaLensPanel
from lens_core.ocr_engine import ViziaOCREngine
from lens_core.translator import ViziaTranslator

# ... kodun geri kalanı aynı (class ViziaPlugin...)

class ViziaPlugin(QObject):
    def __init__(self):
        super().__init__()
        self.name = "Vizia Lens & Transcribe"
        self.icon = "assets/lens.png" # assets klasörüne bir lens.png eklemelisin
        
        self.panel = None
        self.quick_scan_enabled = False
        self.current_overlay = None
        self.original_finalize = None
        self.button_hooked = False
        
        self.ocr_engine = ViziaOCREngine()
        self.translator = ViziaTranslator()

    def run(self, overlay):
        """Toolbar'daki butona SOL tıklandığında çalışır"""
        self.current_overlay = overlay
        self._hook_right_click(overlay)

        if self.quick_scan_enabled:
            self.start_ocr_scan()
        else:
            self.open_settings_panel()

    def _hook_right_click(self, overlay):
        """Butona sağ tıklandığını algılamak için EventFilter ekler"""
        if self.button_hooked or not hasattr(overlay, 'toolbar') or not overlay.toolbar:
            return
            
        drawer = overlay.toolbar.drawer
        for i in range(drawer.layout.count()):
            widget = drawer.layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.toolTip() == self.name:
                widget.installEventFilter(self)
                self.button_hooked = True
                break

    def eventFilter(self, obj, event):
        """Sağ tıklamayı yakalar ve her zaman paneli açar"""
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if self.current_overlay:
                self.open_settings_panel()
            return True
        return super().eventFilter(obj, event)

    def open_settings_panel(self):
        if not self.panel:
            self.panel = ViziaLensPanel(self, self.current_overlay)
        self.panel.show()
        self.panel.raise_()

    def start_ocr_scan(self):
        """window.py'daki ekran alıntısı mekanizmasını geçici olarak OCR için kullanır"""
        overlay = self.current_overlay
        if overlay.toolbar: overlay.toolbar.hide()
        
        overlay.drawing = False
        overlay.is_selecting_region = True
        overlay.select_start = QPoint()
        overlay.select_end = QPoint()
        overlay.setCursor(Qt.CrossCursor)
        overlay.show_toast("<center>OCR için metni seçin<br><span style='font-size: 12px; color: #a1a1a6;'>(Sağ Tık: Ayarlar | Çıkmak için ESC)</span></center>")
        
        # Monkey-Patch: Geçici olarak ekran kaydetme fonksiyonunu kendi fonksiyonumuzla değiştiriyoruz
        self.original_finalize = overlay._finalize_screenshot
        overlay._finalize_screenshot = self.ocr_finalize_override
        overlay.update()

    def ocr_finalize_override(self, crop_rect=None):
        """Seçim bittiğinde tetiklenir"""
        overlay = self.current_overlay
        
        # Orijinal fonksiyonu derhal geri yükle
        overlay._finalize_screenshot = self.original_finalize
        overlay.is_selecting_region = False
        overlay.setCursor(Qt.ArrowCursor)
        overlay.update()
        if overlay.toolbar: overlay.toolbar.show()
        
        if crop_rect and crop_rect.width() > 5 and crop_rect.height() > 5:
            overlay.show_toast("Taranıyor...")
            self._process_ocr_image(crop_rect)

    def _process_ocr_image(self, crop_rect):
        from PyQt5.QtWidgets import QApplication
        pixmap = QApplication.primaryScreen().grabWindow(0).copy(crop_rect)
        
        # Geçici dosyaya kaydet ve OCR'a yolla
        temp_path = os.path.join(tempfile.gettempdir(), "vizia_ocr_temp.png")
        pixmap.save(temp_path, "png")
        
        # Basit bir dil yönetimi (Panelden seçilen dili alacak şekilde geliştirilebilir)
        text = self.ocr_engine.extract_text(temp_path, lang="tur+eng")
        
        if text.strip():
            translated = self.translator.translate(text, target="tr")
            # Sonucu ekranda göster
            self.current_overlay.show_toast(f"<b>Metin:</b> {text}<br><b>Çeviri:</b> {translated}")
        else:
            self.current_overlay.show_toast("Metin algılanamadı.")
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QColor, QKeySequence, QCursor, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect

from core.settings import SettingsManager
from core.screenshot import ScreenshotManager
from core.plugin_window_manager import PluginWindowManager
from .canvas import CanvasLayer

# UI Widget Importları (Dosya yolları yeni yapıya uygun)
from ui.widgets.notification import ModernNotification
from ui.widgets.image_item import ViziaImageItem
from ui.text_widgets import ViziaTextItem 

class DrawingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.plugin_windows = PluginWindowManager()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        
        # --- Canvas Yönetimi ---
        screen_size = QApplication.primaryScreen().size()
        self.desktop_layer = CanvasLayer(screen_size)
        self.board_layer = CanvasLayer(screen_size)
        
        # Varsayılan değerler
        self._whiteboard_mode = False
        self.active_layer = self.desktop_layer 
        self.drawing_mode = "pen"
        self.current_color = QColor(255, 45, 85)
        self.brush_size = 4
        
        self.drawing = False
        self.start_point = QPoint()
        self.last_point = QPoint()
        self.current_stroke_path = QPainterPath()
        
        self.is_selecting_region = False
        self.select_start = QPoint()
        self.select_end = QPoint()
        
        self.toolbar = None 
        self.setFocusPolicy(Qt.StrongFocus)

    # --- [UYUMLULUK] Toolbar.py'nin beklediği property ---
    @property
    def whiteboard_mode(self):
        return self._whiteboard_mode

    @whiteboard_mode.setter
    def whiteboard_mode(self, value):
        self._whiteboard_mode = value
        self.active_layer = self.board_layer if value else self.desktop_layer
        self.plugin_windows.on_mode_changed(value)
        self.update()

    # --- [UYUMLULUK] Toolbar.py'nin çağırdığı metod ---
    def redraw_canvas(self):
        """Toolbar bu metodu çağırdığında aktif katmanı yeniden çizer"""
        self.active_layer.redraw()
        self.update()
        self.bring_ui_to_front()

    # --- [DÜZELTME] Recorder ve UI Kontrolü ---
    def bring_ui_to_front(self):
        if not self.toolbar: return
        if self.toolbar.isVisible(): self.toolbar.raise_()
        
        if hasattr(self.toolbar, 'drawer'):
            drawer = self.toolbar.drawer
            if drawer.isVisible(): drawer.raise_()
        
        self.plugin_windows.bring_all_to_front()

    def is_mouse_on_ui(self, pos):
        """Farenin arayüz üzerinde olup olmadığını kontrol eder"""
        if self.toolbar:
            global_pos = self.mapToGlobal(pos)
            
            # 1. Toolbar
            if self.toolbar.isVisible() and self.toolbar.geometry().contains(global_pos): 
                self.toolbar.raise_()
                return True
            
            # 2. Drawer
            drawer = getattr(self.toolbar, 'drawer', None)
            if drawer and drawer.isVisible() and drawer.geometry().contains(global_pos): 
                drawer.raise_()
                return True
            
            # 3. Eklenti pencereleri
            if self.plugin_windows.is_mouse_on_any(global_pos):
                return True
        
        return False

    def force_focus(self):
        pos = self.mapFromGlobal(QCursor.pos())
        if not self.is_mouse_on_ui(pos) and self.drawing_mode != "move":
            self.activateWindow()
            self.setFocus()

    def keyPressEvent(self, event):
        if self.is_selecting_region and event.key() == Qt.Key_Escape:
            self.cancel_screenshot(); return
            
        key = event.key()
        modifiers = int(event.modifiers())
        
        def check_hotkey(action_name):
            hotkey_str = self.settings.get("hotkeys").get(action_name)
            if not hotkey_str: return False
            seq = QKeySequence(key | modifiers)
            return seq.matches(QKeySequence(hotkey_str)) == QKeySequence.ExactMatch or \
                   (modifiers == 0 and key == QKeySequence(hotkey_str)[0])

        if key == Qt.Key_Backspace: self.undo()
        elif check_hotkey("board_mode"): 
            if self.toolbar: self.toolbar.toggle_board()
        elif check_hotkey("drawer"): self.toolbar.toggle_drawer() if self.toolbar else None
        elif check_hotkey("undo"): self.undo()
        elif check_hotkey("quit"): QApplication.quit()
        elif check_hotkey("screenshot"): self.take_screenshot()
        elif check_hotkey("clear"): self.clear_all()
        elif check_hotkey("move_mode"): self.toolbar.toggle_move_mode() if self.toolbar else None
        elif check_hotkey("color_picker"): self.toolbar.select_color() if self.toolbar else None

    def mousePressEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton: self.select_start = event.pos(); self.select_end = event.pos(); self.update()
            return 
        
        if self.is_mouse_on_ui(event.pos()): return 
        if self.childAt(event.pos()): return 

        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos(); self.last_point = event.pos()
            self.current_stroke_path = QPainterPath(); self.current_stroke_path.moveTo(self.start_point)

    def mouseMoveEvent(self, event):
        if self.is_selecting_region: self.select_end = event.pos(); self.update(); return 
        
        if not self.drawing: 
            self.is_mouse_on_ui(event.pos())
            return
        
        if self.drawing_mode in ["pen", "eraser"]:
            # CanvasLayer üzerinden anlık çizim (Eski hızında)
            self.active_layer.draw_segment(self.last_point, event.pos(), self.current_color, self.brush_size, self.drawing_mode, self._whiteboard_mode)
            self.current_stroke_path.lineTo(event.pos())
            self.last_point = event.pos()
            
        self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_end = event.pos(); selection_rect = QRect(self.select_start, self.select_end).normalized()
                if selection_rect.width() < 5: self._finalize_screenshot(None) 
                else: self._finalize_screenshot(selection_rect)
            return 
            
        if not self.drawing: return
        
        if self.drawing_mode in ["pen", "eraser"]:
            self.active_layer.add_stroke_to_history(self.current_stroke_path, self.current_color, self.brush_size, self.drawing_mode, self._whiteboard_mode)
        elif self.drawing_mode in ["line", "rect", "ellipse"]:
            self.active_layer.add_shape(self.drawing_mode, self.start_point, event.pos(), self.current_color, self.brush_size)
            
        self.drawing = False
        self.current_stroke_path = QPainterPath()
        self.update()
        self.bring_ui_to_front()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.white if self._whiteboard_mode else QColor(0,0,0,1))
        p.drawPixmap(0, 0, self.active_layer.pixmap)
        
        # Şekil Önizlemesi (Kalem/Silgi hariç)
        if self.drawing and self.drawing_mode in ["line", "rect", "ellipse"]:
            p.setPen(QPen(self.current_color, self.brush_size))
            target_pos = self.mapFromGlobal(QCursor.pos())
            if self.drawing_mode == "line": p.drawLine(self.start_point, target_pos)
            elif self.drawing_mode == "rect": p.drawRect(QRect(self.start_point, target_pos).normalized())
            elif self.drawing_mode == "ellipse": p.drawEllipse(QRect(self.start_point, target_pos).normalized())

        # Screenshot Seçim
        if self.is_selecting_region:
            p.setBrush(QColor(0,0,0,80)); p.setPen(Qt.NoPen)
            r = self.rect(); s = QRect(self.select_start, self.select_end).normalized()
            p.setClipRegion(QRegion(r).subtracted(QRegion(s))); p.fillRect(r, QColor(0,0,0,80)); p.setClipRegion(QRegion(r))
            p.setPen(QPen(Qt.white, 2, Qt.DashLine)); p.setBrush(Qt.NoBrush); p.drawRect(s)
            
        self.bring_ui_to_front()

    # --- Araçlar ---
    def undo(self):
        self.active_layer.undo()
        self.update()

    def clear_all(self):
        self.active_layer.clear()
        self.update()

    # --- [UYUMLULUK] Toolbar.py bu metodu çağırıyor ---
    def add_text(self):
        txt = ViziaTextItem(self, self._whiteboard_mode, self.current_color)
        txt.move(100,100)
        # Sinyal bağlantısı
        txt.delete_requested.connect(lambda w: self.active_layer.remove_widget_item(w))
        self.active_layer.add_widget_item(txt, 'text')

    def open_image_loader(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görsel", "", "Resim (*.png *.jpg)")
        if path:
            img = ViziaImageItem(path, self._whiteboard_mode, self)
            img.request_close.connect(lambda w: self.active_layer.remove_widget_item(w))
            img.request_stamp.connect(lambda: self.stamp_image(img))
            self.active_layer.add_widget_item(img, 'image')
        self.force_focus()

    def remove_from_history(self, widget):
        # Toolbar.py çağırmasa da bazı eski modüller için yedek
        self.active_layer.remove_widget_item(widget)

    def stamp_image(self, widget):
        if not widget or not widget.isVisible(): return
        try:
            pos = self.mapFromGlobal(widget.image_container.mapToGlobal(QPoint(0,0)))
            p = QPainter(self.active_layer.pixmap)
            p.setRenderHint(QPainter.SmoothPixmapTransform)
            p.drawPixmap(pos, widget.image_container.pixmap().scaled(widget.image_container.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            p.end()
            widget.close()
            self.update()
            self.force_focus()
        except: pass

    # --- Screenshot ---
    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        self.drawing = False; self.is_selecting_region = True
        self.select_start = QPoint(); self.select_end = QPoint()
        self.setCursor(Qt.CrossCursor)
        self.show_toast("Alan seçin veya tam ekran için tek tıklayın")
        self.update()

    def cancel_screenshot(self):
        self.is_selecting_region = False
        self.setCursor(Qt.ArrowCursor)
        if self.toolbar: self.toolbar.show()
        self.update()

    def _finalize_screenshot(self, crop_rect=None):
        self.is_selecting_region = False; self.setCursor(Qt.ArrowCursor)
        self.update(); QApplication.processEvents()
        QTimer.singleShot(100, lambda: self._perform_save(crop_rect))

    def _perform_save(self, crop_rect):
        try:
            success = ScreenshotManager.save_screenshot(crop_rect, self.settings.get("save_path"))
            self.show_toast("Kaydedildi!" if success else "Hata!")
        except: self.show_toast("Hata")
        if self.toolbar: self.toolbar.show()
        self.force_focus()

    def show_toast(self, m): 
        self.toast = ModernNotification(m, self)
        self.toast.show_animated()
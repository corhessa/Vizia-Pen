from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QColor, QKeySequence, QCursor, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect, QMimeData

from core.settings import SettingsManager
from core.screenshot import ScreenshotManager
from core.plugin_window_manager import PluginWindowManager
from .canvas import CanvasLayer

# UI Widget Importları
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
        
        # 1. Drag & Drop Desteğini Aç
        self.setAcceptDrops(True)
        # Eklentilerin drop olaylarını dinlemesi için liste
        self.drop_handlers = []

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
        self.last_point = QPoint()
        self.current_stroke_path = QPainterPath()
        
        self.is_selecting_region = False
        self.select_start = QPoint()
        self.select_end = QPoint()
        
        self.toolbar = None 
        self.setFocusPolicy(Qt.StrongFocus)

    @property
    def whiteboard_mode(self):
        return self._whiteboard_mode

    @whiteboard_mode.setter
    def whiteboard_mode(self, value):
        self._whiteboard_mode = value
        self.active_layer = self.board_layer if value else self.desktop_layer
        
        for w in self.desktop_layer.widgets:
            w.setVisible(not value)
        for w in self.board_layer.widgets:
            w.setVisible(value)
            
        self.plugin_windows.on_mode_changed(value)
        self.update()
        QTimer.singleShot(50, self.bring_ui_to_front)

    def redraw_canvas(self):
        self.active_layer.redraw()
        self.update()
        self.bring_ui_to_front()

    def bring_ui_to_front(self):
        if not self.toolbar: return
        if self.toolbar.isVisible(): self.toolbar.raise_()
        
        if hasattr(self.toolbar, 'drawer'):
            drawer = self.toolbar.drawer
            if drawer and drawer.isVisible(): drawer.raise_()
        
        self.plugin_windows.bring_all_to_front()

    def is_mouse_on_ui(self, pos):
        if self.toolbar:
            global_pos = self.mapToGlobal(pos)
            
            if self.toolbar.isVisible() and self.toolbar.geometry().contains(global_pos): 
                self.toolbar.raise_()
                return True
            
            drawer = getattr(self.toolbar, 'drawer', None)
            if drawer and drawer.isVisible() and drawer.geometry().contains(global_pos): 
                drawer.raise_()
                return True
            
            if self.plugin_windows.is_mouse_on_any(global_pos):
                return True
        
        return False

    def force_focus(self):
        pos = self.mapFromGlobal(QCursor.pos())
        if not self.is_mouse_on_ui(pos) and self.drawing_mode != "move":
            self.activateWindow()
            self.setFocus()

    # --- DRAG & DROP EVENTLARI ---
    def dragEnterEvent(self, event):
        mime = event.mimeData()
        accepted = False
        for handler in self.drop_handlers:
            if handler(mime, event.pos(), check_only=True):
                event.acceptProposedAction()
                accepted = True
                break
        
        if not accepted:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()
        for handler in self.drop_handlers:
            if handler(mime, event.pos(), check_only=False):
                event.acceptProposedAction()
                self.force_focus() 
                break

    def keyPressEvent(self, event):
        if self.is_selecting_region and event.key() == Qt.Key_Escape:
            self.cancel_screenshot(); return
            
        key = event.key()
        modifiers = int(event.modifiers())
        
        try:
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
        except Exception as e:
            print(f"Kısayol hatası: {e}")

    def mousePressEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton: 
                self.select_start = event.pos()
                self.select_end = event.pos()
                self.update()
            return 
        
        if not self.is_mouse_on_ui(event.pos()):
            self.plugin_windows.notify_canvas_click()
            
        if self.is_mouse_on_ui(event.pos()): return 
        if self.childAt(event.pos()): return 

        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.current_stroke_path = QPainterPath()
            self.current_stroke_path.moveTo(self.last_point)

    def mouseMoveEvent(self, event):
        if self.is_selecting_region: 
            self.select_end = event.pos()
            self.update()
            return 
        
        if not self.drawing: 
            self.is_mouse_on_ui(event.pos())
            return
        
        if self.drawing_mode in ["pen", "eraser"]:
            new_point = event.pos()
            control_point = self.last_point
            
            end_point = (control_point + new_point) / 2
            self.current_stroke_path.quadTo(control_point, end_point)
            
            self.active_layer.draw_segment(self.last_point, new_point, self.current_color, self.brush_size, self.drawing_mode, self._whiteboard_mode)
            
            self.last_point = new_point
            
        self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_end = event.pos()
                selection_rect = QRect(self.select_start, self.select_end).normalized()
                if selection_rect.width() < 5: self._finalize_screenshot(None) 
                else: self._finalize_screenshot(selection_rect)
            return 
            
        if not self.drawing: return
        
        if self.drawing_mode in ["pen", "eraser"]:
            self.active_layer.add_stroke_to_history(self.current_stroke_path, self.current_color, self.brush_size, self.drawing_mode, self._whiteboard_mode)
        elif self.drawing_mode in ["line", "rect", "ellipse"]:
            start_pos = self.current_stroke_path.pointAtPercent(0)
            self.active_layer.add_shape(self.drawing_mode, start_pos, event.pos(), self.current_color, self.brush_size)
            
        self.drawing = False
        self.current_stroke_path = QPainterPath() 
        self.update()
        self.bring_ui_to_front()

    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        
        p.fillRect(self.rect(), Qt.white if self._whiteboard_mode else QColor(0,0,0,1))
        p.drawPixmap(0, 0, self.active_layer.pixmap)
        
        if self.drawing and self.drawing_mode in ["line", "rect", "ellipse"]:
            p.setPen(QPen(self.current_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            target_pos = self.mapFromGlobal(QCursor.pos())
            start_pos = self.current_stroke_path.pointAtPercent(0)
            
            if self.drawing_mode == "line": p.drawLine(start_pos, target_pos)
            elif self.drawing_mode == "rect": p.drawRect(QRect(start_pos, target_pos).normalized())
            elif self.drawing_mode == "ellipse": p.drawEllipse(QRect(start_pos, target_pos).normalized())

        if self.is_selecting_region:
            p.setBrush(QColor(0,0,0,80)); p.setPen(Qt.NoPen)
            r = self.rect(); s = QRect(self.select_start, self.select_end).normalized()
            p.setClipRegion(QRegion(r).subtracted(QRegion(s))); p.fillRect(r, QColor(0,0,0,80)); p.setClipRegion(QRegion(r))
            p.setPen(QPen(Qt.white, 2, Qt.DashLine)); p.setBrush(Qt.NoBrush); p.drawRect(s)

    # --- Araçlar ---
    def undo(self):
        self.active_layer.undo()
        self.update()

    def clear_all(self):
        self.active_layer.clear()
        self.update()

    def add_text(self):
        txt = ViziaTextItem(self, self._whiteboard_mode, self.current_color)
        txt.move(100,100)
        txt.delete_requested.connect(lambda w: [self.active_layer.remove_widget_item(w), w.deleteLater()])
        self.active_layer.add_widget_item(txt, 'text')

    def open_image_loader(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görsel", "", "Resim (*.png *.jpg)")
        if path:
            img = ViziaImageItem(path, self._whiteboard_mode, self)
            img.request_close.connect(lambda w: [self.active_layer.remove_widget_item(w), w.deleteLater()])
            img.request_stamp.connect(lambda: self.stamp_image(img))
            self.active_layer.add_widget_item(img, 'image')
        self.force_focus()

    def remove_from_history(self, widget):
        self.active_layer.remove_widget_item(widget)

    def stamp_image(self, widget):
        if not widget or not widget.isVisible(): return
        try:
            pos = self.mapFromGlobal(widget.image_container.mapToGlobal(QPoint(0,0)))
            p = QPainter(self.active_layer.pixmap)
            p.setRenderHint(QPainter.SmoothPixmapTransform)
            p.setRenderHint(QPainter.Antialiasing)
            p.drawPixmap(pos, widget.image_container.pixmap().scaled(widget.image_container.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            p.end()
            widget.close()
            widget.deleteLater() 
            self.update()
            self.force_focus()
        except Exception as e: 
            print(f"Resim damgalama hatası: {e}")

    # --- Screenshot ---
    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        self.drawing = False; self.is_selecting_region = True
        self.select_start = QPoint(); self.select_end = QPoint()
        self.setCursor(Qt.CrossCursor)
        self.show_toast("<center>Alan seçin veya tam ekran için tek tıklayın<br><span style='font-size: 12px; color: #a1a1a6;'>(Çıkmak için ESC basınız)</span></center>")
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
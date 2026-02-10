# Vizia/core/overlay.py

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath, QColor, QPen, QRegion, QCursor, QKeySequence
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect

from core.settings import SettingsManager
from ui.widgets.notification import ModernNotification
from ui.widgets.image_item import ViziaImageItem
from ui.text_widgets import ViziaTextItem 
from core.screenshot import ScreenshotManager

class DrawingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        
        # Overlay Ayarları
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        
        self.canvas = QPixmap(QApplication.primaryScreen().size())
        self.canvas.fill(Qt.transparent)
        
        self.drawing_mode = "pen"
        self.whiteboard_mode = False
        self.desktop_history, self.board_history = [], []
        self.image_widgets = []
        
        self.current_stroke_path = QPainterPath()
        self.start_point = QPoint(); self.last_point = QPoint()
        self.current_color = QColor(255, 45, 85)
        self.brush_size = 4
        self.drawing = False
        self.toolbar = None
        
        self.is_selecting_region = False
        self.select_start = QPoint()
        self.select_end = QPoint()
        
        self.setFocusPolicy(Qt.StrongFocus)

    def bring_ui_to_front(self):
        if not self.toolbar: return
        
        # 1. Ana Toolbar
        if self.toolbar.isVisible(): self.toolbar.raise_()
        
        # 2. Drawer ve İçindekiler
        if hasattr(self.toolbar, 'drawer'):
            drawer = self.toolbar.drawer
            if drawer.isVisible(): drawer.raise_()
            
            # 3. Recorder Pencereleri (4 parça)
            rec_win = getattr(drawer, 'recorder_window', None)
            if rec_win:
                if rec_win.isVisible(): rec_win.raise_()
                if hasattr(rec_win, 'mini_panel') and rec_win.mini_panel.isVisible():
                    rec_win.mini_panel.raise_()
                if hasattr(rec_win, 'camera_widget') and rec_win.camera_widget.isVisible():
                    rec_win.camera_widget.raise_()

    def is_mouse_on_ui(self, pos):
        if self.toolbar:
            global_pos = self.mapToGlobal(pos)
            
            # Toolbar
            if self.toolbar.isVisible() and self.toolbar.geometry().contains(global_pos): 
                self.toolbar.raise_()
                return True
            
            # Drawer
            drawer = getattr(self.toolbar, 'drawer', None)
            if drawer and drawer.isVisible() and drawer.geometry().contains(global_pos): 
                drawer.raise_()
                return True
            
            # Recorder Pencereleri
            if drawer:
                rec_win = getattr(drawer, 'recorder_window', None)
                if rec_win:
                    if rec_win.isVisible() and rec_win.geometry().contains(global_pos):
                        rec_win.raise_(); rec_win.activateWindow()
                        return True
                    
                    mini_panel = getattr(rec_win, 'mini_panel', None)
                    if mini_panel and mini_panel.isVisible() and mini_panel.geometry().contains(global_pos):
                         mini_panel.raise_(); mini_panel.activateWindow()
                         return True

                    cam_widget = getattr(rec_win, 'camera_widget', None)
                    if cam_widget and cam_widget.isVisible() and cam_widget.geometry().contains(global_pos):
                        cam_widget.raise_(); cam_widget.activateWindow()
                        return True
        return False

    def force_focus(self):
        pos = self.mapFromGlobal(QCursor.pos())
        if self.is_mouse_on_ui(pos): return
        if self.drawing_mode != "move":
            self.activateWindow()
            self.setFocus()

    def update_cursor(self): pass

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

    # [GÜNCELLENDİ] Bildirim Metni
    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        self.drawing = False
        self.is_selecting_region = True
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
        self.is_selecting_region = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        QApplication.processEvents()
        QTimer.singleShot(100, lambda: self._perform_save(crop_rect))

    def _perform_save(self, crop_rect):
        try:
            save_path = self.settings.get("save_path")
            success = ScreenshotManager.save_screenshot(crop_rect, save_path)
            self.show_toast("Kaydedildi!" if success else "Hata!")
        except: self.show_toast("Hata")
        if self.toolbar: self.toolbar.show()
        self.force_focus()

    def mousePressEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton: self.select_start = event.pos(); self.select_end = event.pos(); self.update()
            return 
        
        if self.is_mouse_on_ui(event.pos()): return 

        child = self.childAt(event.pos())
        if child: return 

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
            painter = QPainter(self.canvas); painter.setRenderHint(QPainter.Antialiasing)
            if self.drawing_mode == "eraser":
                if self.whiteboard_mode: painter.setCompositionMode(QPainter.CompositionMode_SourceOver); pen = QPen(Qt.white, self.brush_size * 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                else: painter.setCompositionMode(QPainter.CompositionMode_Clear); pen = QPen(Qt.transparent, self.brush_size * 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            else:
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver); pen = QPen(self.current_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen); painter.drawLine(self.last_point, event.pos()); painter.end()
            self.current_stroke_path.lineTo(event.pos()); self.last_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_end = event.pos(); selection_rect = QRect(self.select_start, self.select_end).normalized()
                if selection_rect.width() < 5: self._finalize_screenshot(None) 
                else: self._finalize_screenshot(selection_rect)
            return 
        if not self.drawing: return
        
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        color_to_save = self.current_color
        if self.drawing_mode == "eraser": color_to_save = Qt.white if self.whiteboard_mode else Qt.transparent
        
        if self.drawing_mode in ["pen", "eraser"]:
            hist.append({'type': 'path', 'path': QPainterPath(self.current_stroke_path), 'color': color_to_save, 'width': self.brush_size * (3 if self.drawing_mode == 'eraser' else 1), 'mode': self.drawing_mode})
        elif self.drawing_mode in ["line", "rect", "ellipse"]:
            hist.append({'type': 'shape', 'shape': self.drawing_mode, 'start': self.start_point, 'end': event.pos(), 'color': QColor(self.current_color), 'width': self.brush_size}); self.redraw_canvas()
        self.drawing = False; self.update()
        
        self.bring_ui_to_front()

    def open_image_loader(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görsel", "", "Resim (*.png *.jpg)")
        if path:
            img = ViziaImageItem(path, self.whiteboard_mode, self)
            img.request_close.connect(self.remove_from_history)
            img.request_stamp.connect(lambda: self.stamp_image(img))
            self.image_widgets.append(img)
            (self.board_history if self.whiteboard_mode else self.desktop_history).append({'type': 'image', 'obj': img})
        self.force_focus()

    def remove_from_history(self, widget):
        if widget in self.image_widgets: self.image_widgets.remove(widget)
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        for i in range(len(hist) - 1, -1, -1):
            if hist[i].get('obj') == widget: hist.pop(i); break

    def stamp_image(self, widget):
        if not widget or not widget.isVisible(): return
        try:
            pos = self.mapFromGlobal(widget.image_container.mapToGlobal(QPoint(0,0)))
            p = QPainter(self.canvas); p.setRenderHint(QPainter.SmoothPixmapTransform)
            p.drawPixmap(pos, widget.image_container.pixmap().scaled(widget.image_container.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            p.end(); self.update(); widget.close(); self.force_focus()
        except: pass

    def undo(self):
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        if hist:
            last = hist.pop()
            if last.get('type') in ['text', 'image']:
                if last.get('obj'): last['obj'].close()
                if last.get('obj') in self.image_widgets: self.image_widgets.remove(last['obj'])
            self.redraw_canvas()

    def clear_all(self):
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in hist:
            if item.get('obj'): item['obj'].close()
        hist.clear(); self.image_widgets.clear(); self.canvas.fill(Qt.transparent); self.update(); self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.fill(Qt.transparent)
        p = QPainter(self.canvas); p.setRenderHint(QPainter.Antialiasing)
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in hist:
            if item.get('type') == 'path':
                p.setCompositionMode(QPainter.CompositionMode_Clear if item.get('mode')=='eraser' and not self.whiteboard_mode else QPainter.CompositionMode_SourceOver)
                p.setPen(QPen(item['color'], item['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.drawPath(item['path'])
            elif item.get('type') == 'shape':
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                p.setPen(QPen(item['color'], item['width'])); 
                if item['shape']=='line': p.drawLine(item['start'], item['end'])
                elif item['shape']=='rect': p.drawRect(QRect(item['start'], item['end']).normalized())
                elif item['shape']=='ellipse': p.drawEllipse(QRect(item['start'], item['end']).normalized())
        p.end(); self.update()
        
        self.bring_ui_to_front()

    def show_toast(self, m): self.toast = ModernNotification(m, self); self.toast.show_animated()
    
    def remove_text_item(self, t):
        h = self.board_history if self.whiteboard_mode else self.desktop_history
        for i, item in enumerate(h): 
            if item.get('obj') == t: h.pop(i); break
        t.deleteLater()
    def add_text(self):
        txt = ViziaTextItem(self, self.whiteboard_mode, self.current_color); txt.move(100,100)
        txt.delete_requested.connect(self.remove_text_item)
        (self.board_history if self.whiteboard_mode else self.desktop_history).append({'type': 'text', 'obj': txt})

    def paintEvent(self, e):
        p = QPainter(self); p.fillRect(self.rect(), Qt.white if self.whiteboard_mode else QColor(0,0,0,1))
        p.drawPixmap(0, 0, self.canvas)
        if self.is_selecting_region:
            p.setBrush(QColor(0,0,0,80)); p.setPen(Qt.NoPen)
            r = self.rect(); s = QRect(self.select_start, self.select_end).normalized()
            p.setClipRegion(QRegion(r).subtracted(QRegion(s))); p.fillRect(r, QColor(0,0,0,80)); p.setClipRegion(QRegion(r))
            p.setPen(QPen(Qt.white, 2, Qt.DashLine)); p.setBrush(Qt.NoBrush); p.drawRect(s)
        if self.drawing and self.drawing_mode in ["line", "rect", "ellipse"]:
            p.setPen(QPen(self.current_color, self.brush_size)); 
            if self.drawing_mode=="line": p.drawLine(self.start_point, self.last_point)
            elif self.drawing_mode=="rect": p.drawRect(QRect(self.start_point, self.last_point).normalized())
            elif self.drawing_mode=="ellipse": p.drawEllipse(QRect(self.start_point, self.last_point).normalized())
            
        self.bring_ui_to_front()
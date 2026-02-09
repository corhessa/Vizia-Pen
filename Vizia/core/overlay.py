# Vizia/core/overlay.py

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath, QColor, QPen, QRegion, QCursor
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect

from core.settings import SettingsManager
from ui.ui_components import ModernNotification, ViziaImageItem
from ui.text_widgets import ViziaTextItem 
from core.screenshot import ScreenshotManager

class DrawingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        
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
        
        # KİLİT YOK - KISITLAMA YOK
        
        self.is_selecting_region = False
        self.select_start = QPoint()
        self.select_end = QPoint()
        
        self.setFocusPolicy(Qt.StrongFocus)

    # UI Kontrolü: Mouse UI üzerindeyse çizimi engelle ama tıklamayı engelleme
    def is_mouse_on_ui(self, pos):
        if self.toolbar:
            global_pos = self.mapToGlobal(pos)
            if self.toolbar.geometry().contains(global_pos): return True
            if hasattr(self.toolbar, 'drawer') and self.toolbar.drawer.isVisible():
                if self.toolbar.drawer.geometry().contains(global_pos): return True
                
            # Recorder penceresi üzerindeyse çizimi engelle
            if hasattr(self.toolbar.drawer, 'recorder_window') and \
               self.toolbar.drawer.recorder_window and \
               self.toolbar.drawer.recorder_window.isVisible():
                if self.toolbar.drawer.recorder_window.geometry().contains(global_pos):
                    return True
        return False

    def force_focus(self):
        if self.drawing_mode != "move":
            self.activateWindow()
            self.setFocus()

    def update_cursor(self): pass

    def keyPressEvent(self, event):
        if self.is_selecting_region and event.key() == Qt.Key_Escape:
            self.cancel_screenshot(); return
            
        key = event.key()
        if key == Qt.Key_Backspace: self.undo()
        elif key == self.settings.get_key_code("board_mode"): self.toolbar.toggle_board() if self.toolbar else None
        elif key == self.settings.get_key_code("drawer"): self.toolbar.toggle_drawer() if self.toolbar else None
        elif key == self.settings.get_key_code("undo"): self.undo()
        elif key == self.settings.get_key_code("quit"): QApplication.quit()
        elif key == self.settings.get_key_code("screenshot"): self.take_screenshot()
        elif key == self.settings.get_key_code("clear"): self.clear_all()
        elif key == self.settings.get_key_code("move_mode"): self.toolbar.toggle_move_mode() if self.toolbar else None
        elif key == self.settings.get_key_code("color_picker"): self.toolbar.select_color() if self.toolbar else None

    # Screenshot
    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        self.drawing = False
        self.is_selecting_region = True
        self.select_start = QPoint(); self.select_end = QPoint()
        self.setCursor(Qt.CrossCursor)
        self.show_toast("Seçim Yapın")
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

    # Mouse Events - KİLİT YOK
    def mousePressEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton: self.select_start = event.pos(); self.select_end = event.pos(); self.update()
            return 

        if self.is_mouse_on_ui(event.pos()): 
            event.ignore() # Tıklamayı alttaki pencereye geçir
            return 

        child = self.childAt(event.pos())
        if child: return 

        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos(); self.last_point = event.pos()
            self.current_stroke_path = QPainterPath(); self.current_stroke_path.moveTo(self.start_point)

    def mouseMoveEvent(self, event):
        if self.is_selecting_region: self.select_end = event.pos(); self.update(); return 
        if not self.drawing: return
        
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

    # Yardımcı Fonksiyonlar (Aynı)
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
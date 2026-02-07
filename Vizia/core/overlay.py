# core/overlay.py

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath, QColor, QPen, QRegion
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect

from core.settings import SettingsManager
from ui.ui_components import ModernNotification, ViziaImageItem
from ui.text_widgets import ViziaTextItem 
from core.screenshot import ScreenshotManager

class DrawingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        
        # Overlay en altta olmalı (çizim alanı), diğer pencereler bunun üstüne çıkacak
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

    def keyPressEvent(self, event):
        if self.is_selecting_region and event.key() == Qt.Key_Escape:
            self.cancel_screenshot()
            return
            
        key = event.key()
        if key == self.settings.get_key_code("board_mode"): self.toolbar.toggle_board() if self.toolbar else None
        elif key == self.settings.get_key_code("drawer"): self.toolbar.toggle_drawer() if self.toolbar else None
        elif key == self.settings.get_key_code("undo"): self.undo()
        elif key == self.settings.get_key_code("quit"): QApplication.quit()
        elif key == self.settings.get_key_code("screenshot"): self.take_screenshot()
        elif key == self.settings.get_key_code("clear"): self.clear_all()
        elif key == self.settings.get_key_code("move_mode"): self.toolbar.toggle_move_mode() if self.toolbar else None
        elif key == self.settings.get_key_code("color_picker"): self.toolbar.select_color() if self.toolbar else None

    # --- SCREENSHOT İŞLEMLERİ ---
    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        self.drawing = False 
        self.is_selecting_region = True
        self.select_start = QPoint()
        self.select_end = QPoint()
        self.setCursor(Qt.CrossCursor)
        # İSTENEN METİN:
        self.show_toast("Alanı seçmek için sürükleyin (Tam ekran için tıklayın)")
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
        QApplication.processEvents() # UI'ın güncellenmesini bekle
        QTimer.singleShot(100, lambda: self._perform_save(crop_rect))

    def _perform_save(self, crop_rect):
        try:
            save_path = self.settings.get("save_path")
            success = ScreenshotManager.save_screenshot(crop_rect, save_path)
            
            if success:
                self.show_toast(f"Kaydedildi!")
            else:
                self.show_toast("Hata: Kaydedilemedi!")
        except Exception as e:
            print(f"Save Crash Prevention: {e}")
            self.show_toast("Hata: Beklenmedik bir sorun oluştu.")
            
        if self.toolbar: self.toolbar.show()
        self.force_focus()

    # --- MOUSE OLAYLARI (SS Modunda Return ile Çıkış) ---
    def mousePressEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_start = event.pos()
                self.select_end = event.pos()
                self.update()
            return # Çizim yapma, çık

        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.last_point = event.pos()
            self.current_stroke_path = QPainterPath()
            self.current_stroke_path.moveTo(self.start_point)

    def mouseMoveEvent(self, event):
        if self.is_selecting_region:
            self.select_end = event.pos()
            self.update()
            return # Çizim yapma, çık

        if not self.drawing: return
        if self.drawing_mode == "pen":
            painter = QPainter(self.canvas)
            painter.setPen(QPen(self.current_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, event.pos())
            painter.end()
            self.current_stroke_path.lineTo(event.pos())
            self.last_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_end = event.pos()
                selection_rect = QRect(self.select_start, self.select_end).normalized()
                # Çok küçükse tam ekran al
                if selection_rect.width() < 5 or selection_rect.height() < 5:
                    self._finalize_screenshot(None)
                else:
                    self._finalize_screenshot(selection_rect)
            return # Çizim yapma, çık

        if not self.drawing: return
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        if self.drawing_mode == "pen":
            hist.append({'type': 'path', 'path': QPainterPath(self.current_stroke_path), 'color': QColor(self.current_color), 'width': self.brush_size})
        elif self.drawing_mode in ["line", "rect", "ellipse"]:
            hist.append({'type': 'shape', 'shape': self.drawing_mode, 'start': self.start_point, 'end': event.pos(), 'color': QColor(self.current_color), 'width': self.brush_size})
            self.redraw_canvas()
        self.drawing = False
        self.update()

    # --- DİĞER STANDART FONKSİYONLAR ---
    def open_image_loader(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Resimler (*.png *.jpg *.jpeg *.bmp)")
        if path:
            img = ViziaImageItem(path, self.whiteboard_mode, self)
            img.request_close.connect(self.remove_from_history)
            img.request_stamp.connect(self.stamp_image)
            self.image_widgets.append(img)
            hist = self.board_history if self.whiteboard_mode else self.desktop_history
            hist.append({'type': 'image', 'obj': img})

    def remove_from_history(self, widget):
        if widget in self.image_widgets: self.image_widgets.remove(widget)
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in hist[:]:
            if item.get('obj') == widget: hist.remove(item)

    def stamp_image(self, widget):
        label_geo = widget.image_container.geometry()
        pos = self.mapFromGlobal(widget.mapToGlobal(label_geo.topLeft()))
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(pos, widget.image_container.pixmap().scaled(widget.image_container.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        painter.end()
        widget.close()
        self.update()

    def undo(self):
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        if hist:
            last = hist.pop()
            if last['type'] in ['text', 'image']:
                try: last['obj'].close()
                except: pass
            self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.fill(Qt.transparent)
        painter = QPainter(self.canvas)
        hist = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in hist:
            if item.get('type') == 'path':
                painter.setPen(QPen(item['color'], item['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(item['path'])
            elif item.get('type') == 'shape':
                painter.setPen(QPen(item['color'], item['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                if item['shape'] == 'line': painter.drawLine(item['start'], item['end'])
                elif item['shape'] == 'rect': painter.drawRect(QRect(item['start'], item['end']).normalized())
                elif item['shape'] == 'ellipse': painter.drawEllipse(QRect(item['start'], item['end']).normalized())
        painter.end()
        for img in self.image_widgets: img.setVisible(img.creation_mode == self.whiteboard_mode)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white if self.whiteboard_mode else QColor(0,0,0,1))
        painter.drawPixmap(0, 0, self.canvas)
        if self.is_selecting_region:
            painter.setBrush(QColor(0, 0, 0, 80)); painter.setPen(Qt.NoPen)
            full_rect = self.rect(); selection_rect = QRect(self.select_start, self.select_end).normalized()
            clip = QRegion(full_rect).subtracted(QRegion(selection_rect))
            painter.setClipRegion(clip); painter.fillRect(full_rect, QColor(0, 0, 0, 80)); painter.setClipRegion(QRegion(full_rect)) 
            painter.setPen(QPen(Qt.white, 2, Qt.DashLine)); painter.setBrush(Qt.NoBrush); painter.drawRect(selection_rect)
        if self.drawing and self.drawing_mode in ["line", "rect", "ellipse"]:
            painter.setPen(QPen(self.current_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            if self.drawing_mode == "line": painter.drawLine(self.start_point, self.last_point)
            elif self.drawing_mode == "rect": painter.drawRect(QRect(self.start_point, self.last_point).normalized())
            elif self.drawing_mode == "ellipse": painter.drawEllipse(QRect(self.start_point, self.last_point).normalized())

    def force_focus(self): self.activateWindow(); self.raise_(); self.setFocus()
    def clear_all(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        for item in target[:]:
            if item.get('type') == 'text': item['obj'].close()
            if item.get('type') == 'image': 
                if item['obj'] in self.image_widgets: self.image_widgets.remove(item['obj'])
                item['obj'].close()
        target.clear(); self.canvas.fill(Qt.transparent); self.update(); self.redraw_canvas()
    def show_toast(self, m): self.toast = ModernNotification(m, self); self.toast.show_animated()
    def remove_text_item(self, t):
        h = self.board_history if self.whiteboard_mode else self.desktop_history
        for i, item in enumerate(h): 
            if item.get('obj') == t: h.pop(i); break
        t.deleteLater(); self.update()
    def add_text(self):
        txt = ViziaTextItem(self, self.whiteboard_mode, self.current_color)
        txt.move(100, 100); txt.delete_requested.connect(self.remove_text_item)
        (self.board_history if self.whiteboard_mode else self.desktop_history).append({'type': 'text', 'obj': txt})
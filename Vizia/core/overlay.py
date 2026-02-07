# core/overlay.py

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog)
from PyQt5.QtGui import (QPainter, QPixmap, QPainterPath, QColor, QPen, QRegion)
from PyQt5.QtCore import (Qt, QPoint, QTimer, QRect)

from ui.ui_components import ModernNotification, ViziaImageItem
from ui.text_widgets import ViziaTextItem 
from core.screenshot import ScreenshotManager

class DrawingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        
        self.canvas = QPixmap(QApplication.primaryScreen().size())
        self.canvas.fill(Qt.transparent)
        
        self.drawing_mode = "pen"
        self.whiteboard_mode = False
        
        # History listeleri hem çizimleri hem de nesneleri (resim, metin) sırasıyla tutar
        self.desktop_history = [] 
        self.board_history = []
        
        self.image_widgets = [] 
        
        self.current_stroke_path = QPainterPath()
        self.last_point = QPoint()
        self.current_color = QColor(255, 45, 85)
        self.brush_size = 4
        self.drawing = False
        self.toolbar = None
        self.toast = None
        
        self.is_selecting_region = False
        self.select_start = QPoint()
        self.select_end = QPoint()
        
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if self.is_selecting_region and event.key() == Qt.Key_Escape:
            self.cancel_screenshot()
            return
            
        if event.key() == Qt.Key_Space:
            if self.toolbar: self.toolbar.toggle_board()
        elif event.key() == Qt.Key_E:
            if self.toolbar: self.toolbar.toggle_drawer()
        elif event.key() == Qt.Key_Backspace: self.undo()
        elif event.key() == Qt.Key_Q: QApplication.quit()
        elif event.key() == Qt.Key_S: self.take_screenshot()
        elif event.key() == Qt.Key_D: self.clear_all()
        elif event.key() == Qt.Key_V:
            if self.toolbar: self.toolbar.toggle_move_mode()
        elif event.key() == Qt.Key_C:
            if self.toolbar: self.toolbar.select_color()

    def open_image_loader(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Görsel Seç", "", "Resimler (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.add_image_to_screen(file_path)

    def add_image_to_screen(self, path):
        try:
            # Resmi oluştururken mevcut modu (whiteboard_mode) veriyoruz
            img_item = ViziaImageItem(path, self.whiteboard_mode, self)
            
            img_item.request_close.connect(self.remove_image_widget_from_ui)
            img_item.request_stamp.connect(self.stamp_image)
            
            screen_geo = QApplication.primaryScreen().geometry()
            x = (screen_geo.width() - img_item.width()) // 2
            y = (screen_geo.height() - img_item.height()) // 2
            img_item.move(x, y)
            
            img_item.show()
            self.image_widgets.append(img_item)
            
            # Undo sistemi için history'ye ekle
            target_history = self.board_history if self.whiteboard_mode else self.desktop_history
            target_history.append({'type': 'image', 'obj': img_item})
            
        except Exception:
            self.show_toast("Hata: Resim yüklenemedi!")

    def remove_image_widget_from_ui(self, widget):
        # UI'dan kaldırır (Kapat butonuna basınca)
        if widget in self.image_widgets:
            self.image_widgets.remove(widget)
        widget.deleteLater()
        
        # History'den de temizle ki Undo yapınca hata vermesin
        target_hist = self.board_history if self.whiteboard_mode else self.desktop_history
        for i in range(len(target_hist) - 1, -1, -1):
            item = target_hist[i]
            if item.get('type') == 'image' and item.get('obj') == widget:
                target_hist.pop(i)
                break

    def stamp_image(self, widget):
        if not widget: return
        label_geo = widget.image_container.geometry()
        global_pos = widget.mapToGlobal(label_geo.topLeft())
        overlay_pos = self.mapFromGlobal(global_pos)
        
        pixmap = widget.image_container.pixmap()
        if pixmap:
            painter = QPainter(self.canvas)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            scaled_pix = pixmap.scaled(widget.image_container.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(overlay_pos, scaled_pix)
            painter.end()
            self.update()
            
            # Widget'ı kapat ama history'ye bu sefer 'path' benzeri bir işlem eklemiyoruz,
            # çünkü canvas'a boyandı. Geri almak için son yapılan "stamp" işlemi geri alınamaz (canvas boyandı).
            # VEYA: Stamp işlemi bir "Path" gibi algılanmalı.
            # Şimdilik basitçe widget'ı kaldırıyoruz.
            self.remove_image_widget_from_ui(widget)
            self.show_toast("Görsel Sabitlendi ✓")

    def undo(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        if target:
            last_item = target.pop()
            
            if last_item['type'] == 'path':
                # Çizimi geri al: Yeniden çizim (redraw_canvas) bunu halleder
                self.redraw_canvas()
                
            elif last_item['type'] == 'text':
                try: last_item['obj'].close()
                except: pass
                
            elif last_item['type'] == 'image':
                # Resmi geri al: Widget'ı kapat ve listeden sil
                widget = last_item['obj']
                if widget in self.image_widgets:
                    self.image_widgets.remove(widget)
                try: widget.close()
                except: pass
                
            self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.fill(Qt.transparent)
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        
        active_hist = self.board_history if self.whiteboard_mode else self.desktop_history
        
        # 1. Çizimleri (Path) çiz
        for item in active_hist:
            if item.get('type') == 'path':
                if item['mode'] == 'eraser' and not self.whiteboard_mode:
                    painter.setCompositionMode(QPainter.CompositionMode_Clear); pen_color = Qt.transparent
                else:
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    pen_color = Qt.white if item['mode'] == 'eraser' else item['color']
                painter.setPen(QPen(pen_color, item['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(item['path'])
        painter.end()
        
        # 2. Nesnelerin Görünürlüğünü Ayarla (KATMAN YÖNETİMİ)
        # Tüm nesneleri (hem masaüstü hem beyaz tahta) kontrol et
        # Eğer nesne şu anki modda yaratıldıysa GÖSTER, değilse GİZLE.
        
        # Metinler
        all_text_items = [x for x in (self.desktop_history + self.board_history) if x.get('type') == 'text']
        for item in all_text_items:
            try: item['obj'].setVisible(item['obj'].creation_mode == self.whiteboard_mode)
            except: pass
            
        # Resimler
        for img_widget in self.image_widgets:
            try:
                img_widget.setVisible(img_widget.creation_mode == self.whiteboard_mode)
            except: pass
            
        self.update()

    def force_focus(self):
        self.activateWindow(); self.raise_(); self.setFocus()

    def clear_all(self):
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        
        # Sadece mevcut moddaki nesneleri temizle
        for item in target[:]:
            if item.get('type') == 'text': item['obj'].close()
            if item.get('type') == 'image': 
                if item['obj'] in self.image_widgets:
                    self.image_widgets.remove(item['obj'])
                item['obj'].close()
        
        target.clear()
        self.canvas.fill(Qt.transparent)
        self.update()
        self.redraw_canvas() 

    # --- Ekran Görüntüsü ve Diğerleri (Aynı) ---
    def take_screenshot(self):
        if self.toolbar: self.toolbar.hide()
        self.is_selecting_region = True
        self.select_start = QPoint(); self.select_end = QPoint()
        self.setCursor(Qt.CrossCursor)
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
        QApplication.processEvents() 
        QTimer.singleShot(50, lambda: self._perform_save(crop_rect))

    def _perform_save(self, crop_rect):
        success = ScreenshotManager.save_screenshot(crop_rect)
        if success: self.show_toast("Başarıyla Kaydedildi !")
        else: self.show_toast("Hata: Kaydedilemedi!")
        if self.toolbar: self.toolbar.show()
        self.force_focus()

    def show_toast(self, message):
        self.toast = ModernNotification(message, self)
        self.toast.show_animated()

    def remove_text_item(self, text_item):
        # Metin silindiğinde history'den de sil
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        for i in range(len(target) - 1, -1, -1):
            item = target[i]
            if item.get('obj') == text_item:
                target.pop(i)
                break
        text_item.deleteLater()
        self.update()

    def add_text(self):
        txt = ViziaTextItem(self, self.whiteboard_mode, self.current_color)
        start_x, start_y = 100, 100
        if self.toolbar:
            start_x = self.toolbar.x() + self.toolbar.width() + 20
            start_y = self.toolbar.y()
        txt.move(start_x, start_y)
        txt.delete_requested.connect(self.remove_text_item)
        target = self.board_history if self.whiteboard_mode else self.desktop_history
        target.append({'type': 'text', 'obj': txt})

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.whiteboard_mode: painter.fillRect(self.rect(), Qt.white)
        else: painter.fillRect(self.rect(), QColor(0, 0, 0, 1)) 
        painter.drawPixmap(0, 0, self.canvas)
        if self.is_selecting_region:
            painter.setBrush(QColor(0, 0, 0, 80)); painter.setPen(Qt.NoPen)
            full_rect = self.rect()
            selection_rect = QRect(self.select_start, self.select_end).normalized()
            clip_region = QRegion(full_rect).subtracted(QRegion(selection_rect))
            painter.setClipRegion(clip_region)
            painter.fillRect(full_rect, QColor(0, 0, 0, 80))
            painter.setClipRegion(QRegion(full_rect)) 
            pen = QPen(Qt.white, 2, Qt.DashLine)
            painter.setPen(pen); painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection_rect)
            if selection_rect.width() > 0:
                txt = f"{selection_rect.width()} x {selection_rect.height()}"
                painter.setPen(Qt.white)
                painter.drawText(selection_rect.topLeft() + QPoint(5, -5), txt)

    def mousePressEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_start = event.pos(); self.select_end = event.pos(); self.update()
            return 
        if self.drawing_mode != "move": self.force_focus()
        if self.drawing_mode in ["pen", "eraser"] and event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.current_stroke_path = QPainterPath()
            self.current_stroke_path.moveTo(self.last_point)

    def mouseMoveEvent(self, event):
        if self.is_selecting_region:
            self.select_end = event.pos(); self.update()
            return
        if not self.drawing: return
        current_pos = event.pos()
        mid_point = (self.last_point + current_pos) / 2
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.drawing_mode == 'eraser' and not self.whiteboard_mode:
            painter.setCompositionMode(QPainter.CompositionMode_Clear); pen_color = Qt.transparent
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen_color = Qt.white if self.drawing_mode == 'eraser' else self.current_color
        painter.setPen(QPen(pen_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path_segment = QPainterPath()
        path_segment.moveTo(self.last_point); path_segment.quadTo(self.last_point, mid_point); path_segment.lineTo(current_pos)
        painter.drawPath(path_segment); painter.end()
        self.current_stroke_path.quadTo(self.last_point, mid_point); self.current_stroke_path.lineTo(current_pos)
        self.last_point = current_pos; self.update()

    def mouseReleaseEvent(self, event):
        if self.is_selecting_region:
            if event.button() == Qt.LeftButton:
                self.select_end = event.pos()
                selection_rect = QRect(self.select_start, self.select_end).normalized()
                if selection_rect.width() < 10 or selection_rect.height() < 10: self._finalize_screenshot(None) 
                else: self._finalize_screenshot(selection_rect)
            return
        if self.drawing:
            item = {'type': 'path', 'path': QPainterPath(self.current_stroke_path), 
                    'color': QColor(self.current_color), 'width': self.brush_size, 'mode': self.drawing_mode}
            target = self.board_history if self.whiteboard_mode else self.desktop_history
            target.append(item)
        self.drawing = False; self.update()
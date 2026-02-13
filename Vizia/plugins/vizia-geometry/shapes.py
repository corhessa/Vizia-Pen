import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QTransform, 
    QFont, QBrush, QCursor, QTextOption, QFontMetrics
)

# ---------------------------------------------------------------------------
# Çizim Fonksiyonları
# ---------------------------------------------------------------------------
def draw_shape_path(painter, shape_type, rect, extra_flags=None):
    if extra_flags is None: extra_flags = {}

    if shape_type == "rect":
        painter.drawRoundedRect(rect, 4, 4)
    elif shape_type == "circle":
        painter.drawEllipse(rect)
    elif shape_type == "triangle":
        path = QPainterPath()
        path.moveTo(rect.center().x(), rect.top())
        path.lineTo(rect.bottomLeft())
        path.lineTo(rect.bottomRight())
        path.closeSubpath()
        painter.drawPath(path)
    elif shape_type == "hex":
        _draw_hex_path(painter, rect)
    elif shape_type == "grid":
        _draw_grid_path(painter, rect)
    elif shape_type == "star":
        _draw_star_path(painter, rect)
    elif shape_type == "line":
        if extra_flags.get("flipped", False):
            painter.drawLine(rect.topRight(), rect.bottomLeft())
        else:
            painter.drawLine(rect.topLeft(), rect.bottomRight())     
    elif shape_type == "arrow":
        _draw_arrow_path(painter, rect)
    elif shape_type == "note":
        _draw_note_path(painter, rect)

def _draw_hex_path(painter, rect):
    path = QPainterPath()
    w, h = rect.width(), rect.height()
    cx, cy = rect.center().x(), rect.center().y()
    points = []
    radius_x = w / 2
    radius_y = h / 2
    for i in range(6):
        angle_deg = 60 * i 
        angle_rad = math.radians(angle_deg)
        px = cx + radius_x * math.cos(angle_rad)
        py = cy + radius_y * math.sin(angle_rad)
        points.append(QPointF(px, py))
    path.moveTo(points[0])
    for p in points[1:]:
        path.lineTo(p)
    path.closeSubpath()
    painter.drawPath(path)

def _draw_grid_path(painter, rect):
    old_brush = painter.brush()
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(rect)
    step = max(20, int(min(rect.width(), rect.height()) / 4))
    if step < 5: step = 5 
    x = rect.left() + step
    while x < rect.right():
        painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
        x += step
    y = rect.top() + step
    while y < rect.bottom():
        painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
        y += step
    painter.setBrush(old_brush)

def _draw_star_path(painter, rect):
    cx, cy = rect.center().x(), rect.center().y()
    r_out = min(rect.width(), rect.height()) / 2
    r_in = r_out * 0.4
    path = QPainterPath()
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = r_out if i % 2 == 0 else r_in
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        if i == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    path.closeSubpath()
    painter.drawPath(path)

def _draw_arrow_path(painter, rect):
    w = rect.width()
    h = rect.height()
    shaft_h = h * 0.35
    head_start = w * 0.60
    path = QPainterPath()
    cy = rect.center().y()
    path.moveTo(rect.left(), cy - shaft_h / 2)
    path.lineTo(rect.left() + head_start, cy - shaft_h / 2)
    path.lineTo(rect.left() + head_start, rect.top())
    path.lineTo(rect.right(), cy)
    path.lineTo(rect.left() + head_start, rect.bottom())
    path.lineTo(rect.left() + head_start, cy + shaft_h / 2)
    path.lineTo(rect.left(), cy + shaft_h / 2)
    path.closeSubpath()
    painter.drawPath(path)

def _draw_note_path(painter, rect):
    fold = min(rect.width(), rect.height()) * 0.2
    path = QPainterPath()
    path.moveTo(rect.left(), rect.top())
    path.lineTo(rect.right() - fold, rect.top())
    path.lineTo(rect.right(), rect.top() + fold)
    path.lineTo(rect.right(), rect.bottom())
    path.lineTo(rect.left(), rect.bottom())
    path.closeSubpath()
    painter.drawPath(path)

    old_brush = painter.brush()
    c = QColor(painter.brush().color())
    c.setAlpha(min(255, c.alpha() + 50))
    painter.setBrush(c)
    
    fold_path = QPainterPath()
    fold_path.moveTo(rect.right() - fold, rect.top())
    fold_path.lineTo(rect.right() - fold, rect.top() + fold)
    fold_path.lineTo(rect.right(), rect.top() + fold)
    fold_path.closeSubpath()
    painter.drawPath(fold_path)
    painter.setBrush(old_brush)
    
    pen = QPen(QColor(0,0,0, 40), 1)
    old_pen = painter.pen()
    painter.setPen(pen)
    line_spacing = max(15, rect.height() / 6)
    y = rect.top() + fold + 10
    while y < rect.bottom() - 10:
        painter.drawLine(QPointF(rect.left() + 10, y), QPointF(rect.right() - 10, y))
        y += line_spacing
    painter.setPen(old_pen)

# ---------------------------------------------------------------------------
# GeometryShape
# ---------------------------------------------------------------------------
class GeometryShape(QWidget):
    
    clicked = pyqtSignal(object) 
    rotation_changed = pyqtSignal(float) 
    
    HANDLE_SIZE = 12 
    ROTATION_HANDLE_DIST = 35
    MARGIN = 60 # Handle'ların ve döndürme çubuğunun kesilmemesi için iç boşluk

    def __init__(self, parent, shape_type, color, width=160, height=160):
        super().__init__(parent)
        self.shape_type = shape_type
        self.primary_color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        
        self.opacity_val = 255 

        # Widget Ayarları
        # Widget'ı fiziksel olarak şekilden daha büyük yapıyoruz (Margin kadar)
        self.resize(width + self.MARGIN * 2, height + self.MARGIN * 2) 
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.ClickFocus)
        self.show()
        
        # Durum Değişkenleri
        self.rotation_angle = 0.0
        self.filled = True
        self.is_selected = False
        self.text = ""
        self.is_flipped = False
        
        # Etkileşim Değişkenleri
        self._resize_handle = None    
        self._rotating = False
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._rot_start_angle = 0.0   

        # Çizim alanı (Rect) her zaman margin'den başlar ama (0,0,w,h) boyutundadır mantıksal olarak
        # Bu rect sadece şeklin boyutunu tutar, pozisyonu paintEvent içinde margin ile verilir.
        self._logical_rect = QRectF(0, 0, width, height)

    def set_selected(self, val):
        self.is_selected = val
        self.update()
        if val: 
            self.raise_() 
            self.setFocus() 

    def update_fill(self, is_filled):
        self.filled = is_filled
        self.update()

    def set_opacity(self, val):
        self.opacity_val = val
        self.update()

    def keyPressEvent(self, event):
        if self.shape_type == "note" and self.is_selected:
            if event.key() == Qt.Key_Backspace:
                self.text = self.text[:-1]
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.text += "\n"
            else:
                if event.text():
                    self.text += event.text()
            self.update()
        else:
            super().keyPressEvent(event)

    # ------ ÇİZİM (Paint Event) ------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Margin kadar içeri kaydır (Padding)
        # Bu sayede döndürme tutamağı üstte kesilmez.
        painter.translate(self.MARGIN, self.MARGIN)

        # Döndürme işlemi - Şeklin kendi merkezinde
        rect = self._logical_rect
        center = rect.center()
        
        painter.save()
        painter.translate(center)
        painter.rotate(self.rotation_angle)
        painter.translate(-center)

        final_color = QColor(self.primary_color)
        final_color.setAlpha(self.opacity_val)
        
        if self.filled and self.shape_type != "line":
            painter.setBrush(final_color)
        else:
            painter.setBrush(Qt.NoBrush)

        if self.shape_type == "line":
            line_pen_color = QColor(final_color) 
            line_pen_color.setAlpha(self.opacity_val)
            pen = QPen(line_pen_color, self.stroke_width)
        else:
            pen = QPen(self.border_color, self.stroke_width)
            
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        flags = {"flipped": self.is_flipped}
        draw_shape_path(painter, self.shape_type, rect, flags)

        if self.shape_type == "note" and self.text:
            painter.setPen(QColor(0,0,0, 220)) 
            text_rect = rect.adjusted(10, 20, -10, -10)
            
            font_size = 100
            min_size = 8
            
            while font_size > min_size:
                f = QFont("Segoe UI", font_size)
                f.setBold(True)
                fm = QFontMetrics(f)
                bbox = fm.boundingRect(text_rect.toRect(), Qt.TextWordWrap, self.text)
                if bbox.width() <= text_rect.width() and bbox.height() <= text_rect.height():
                    break
                font_size -= 2
            
            painter.setFont(QFont("Segoe UI", max(font_size, min_size), QFont.Bold))
            opt = QTextOption()
            opt.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            painter.drawText(text_rect, self.text, opt)

        if self.is_selected:
            self._draw_handles(painter, rect)

        painter.restore()

    def _draw_handles(self, painter, rect):
        hs = self.HANDLE_SIZE
        sel_pen = QPen(QColor(100, 100, 255), 1.5, Qt.SolidLine)
        painter.setPen(sel_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)
        
        handles = self._get_handle_info(rect)
        for h_type, r in handles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            if h_type == "corner":
                painter.drawEllipse(r)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(100, 100, 255), 2))
                painter.drawEllipse(r)
            elif h_type == "side":
                painter.drawRoundedRect(r, 3, 3)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(100, 100, 255), 2))
                painter.drawRoundedRect(r, 3, 3)

        rot_pos = QPointF(rect.center().x(), rect.top() - self.ROTATION_HANDLE_DIST)
        painter.setPen(QPen(QColor(100, 100, 255), 1.5))
        painter.drawLine(QPointF(rect.center().x(), rect.top()), rot_pos)
        
        painter.setBrush(Qt.white)
        painter.setPen(QPen(QColor(100, 100, 255), 2))
        painter.drawEllipse(rot_pos, hs/1.5, hs/1.5)

    def _get_handle_info(self, rect):
        if self.shape_type == "line":
            hs = self.HANDLE_SIZE
            p1 = rect.topLeft()
            p2 = rect.bottomRight()
            if self.is_flipped:
                p1 = rect.topRight()
                p2 = rect.bottomLeft()
            return [
                ("corner", QRectF(p1.x()-hs/2, p1.y()-hs/2, hs, hs)),
                ("corner", QRectF(p2.x()-hs/2, p2.y()-hs/2, hs, hs))
            ]

        hs = self.HANDLE_SIZE
        cx, cy = rect.center().x(), rect.center().y()
        corners = [
            ("corner", QRectF(rect.left()-hs/2, rect.top()-hs/2, hs, hs)),      # TL (0)
            ("corner", QRectF(rect.right()-hs/2, rect.top()-hs/2, hs, hs)),     # TR (1)
            ("corner", QRectF(rect.left()-hs/2, rect.bottom()-hs/2, hs, hs)),   # BL (2)
            ("corner", QRectF(rect.right()-hs/2, rect.bottom()-hs/2, hs, hs))   # BR (3)
        ]
        bar_w, bar_h = 16, 6
        sides = [
            ("side", QRectF(cx-bar_w/2, rect.top()-bar_h/2, bar_w, bar_h)),       # Top (4)
            ("side", QRectF(cx-bar_w/2, rect.bottom()-bar_h/2, bar_w, bar_h)),    # Bottom (5)
            ("side", QRectF(rect.left()-bar_h/2, cy-bar_w/2, bar_h, bar_w)),      # Left (6)
            ("side", QRectF(rect.right()-bar_h/2, cy-bar_w/2, bar_h, bar_w))      # Right (7)
        ]
        return corners + sides

    def _get_rotation_handle_rect(self, rect):
        hs = self.HANDLE_SIZE
        pos = QPointF(rect.center().x(), rect.top() - self.ROTATION_HANDLE_DIST)
        return QRectF(pos.x() - hs/2, pos.y() - hs/2, hs, hs)

    def map_mouse_to_logic(self, global_pos):
        # 1. Widget'ın sol üst köşesine göre (Margin dahil)
        local_pos = self.mapFromGlobal(global_pos)
        
        # 2. Margin'i çıkar (Mantıksal alana geç)
        logic_x = local_pos.x() - self.MARGIN
        logic_y = local_pos.y() - self.MARGIN
        
        # 3. Döndürme ters işlemi
        rect = self._logical_rect
        center = rect.center()
        
        # Noktayı merkeze taşı
        dx = logic_x - center.x()
        dy = logic_y - center.y()
        
        # Ters döndür
        angle_rad = math.radians(-self.rotation_angle)
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        
        # Geri taşı
        final_x = rx + center.x()
        final_y = ry + center.y()
        
        return QPointF(final_x, final_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Mouse'u mantıksal koordinata çevir
            logic_mouse = self.map_mouse_to_logic(event.globalPos())
            rect = self._logical_rect
            
            # Handle Kontrolü
            handles = self._get_handle_info(rect)
            for i, (htype, h_rect) in enumerate(handles):
                if h_rect.contains(logic_mouse):
                    self._resize_handle = i
                    self.clicked.emit(self)
                    # Resize başlangıcı için global pos
                    self._drag_start_pos = event.globalPos()
                    # O anki geometriyi sakla
                    self._start_geometry = self.geometry()
                    return

            # Döndürme Tutamağı
            if self._get_rotation_handle_rect(rect).contains(logic_mouse):
                self._rotating = True
                center = rect.center()
                # Döndürme için widget merkezine göre açı
                widget_center = self.rect().center()
                local_mouse = self.mapFromGlobal(event.globalPos())
                self._rot_start_angle = math.degrees(math.atan2(local_mouse.y() - widget_center.y(), local_mouse.x() - widget_center.x())) - self.rotation_angle
                self.clicked.emit(self)
                return
            
            # Şekil İçine Tıklama
            if rect.contains(logic_mouse):
                self._dragging = True
                self._drag_start_pos = event.globalPos() - self.pos()
                self.clicked.emit(self)
                self.setFocus()
            else:
                event.ignore()

    def mouseMoveEvent(self, event):
        if self._dragging:
            # Sadece widget'ı taşı, içeriği değiştirme
            self.move(event.globalPos() - self._drag_start_pos)
            return

        if self._rotating:
            widget_center = self.rect().center()
            local_mouse = self.mapFromGlobal(event.globalPos())
            angle = math.degrees(math.atan2(local_mouse.y() - widget_center.y(), local_mouse.x() - widget_center.x()))
            new_angle = angle - self._rot_start_angle
            self.rotation_angle = new_angle
            self.rotation_changed.emit(new_angle)
            self.update()
            return

        if self._resize_handle is not None:
            # Resize İşlemi: Widget'ın kendisini (geometry) değiştiriyoruz.
            # Bu, fiziksel büyümeyi sağlar ve kesilmeyi önler.
            
            delta = event.globalPos() - self._drag_start_pos
            start_geo = self._start_geometry
            
            idx = self._resize_handle
            
            # Line için özel mantık yok, rect mantığı yeterli çünkü container büyüyor
            # Ancak line'ın sadece 2 noktası var
            
            new_x = start_geo.x()
            new_y = start_geo.y()
            new_w = start_geo.width()
            new_h = start_geo.height()
            
            # Margin payını hesaba katmadan delta uyguluyoruz çünkü margin sabit
            dx = delta.x()
            dy = delta.y()
            
            if self.shape_type == "line":
                if idx == 0: # Start Point
                   if self.is_flipped: # Top Right
                       new_y += dy; new_w += dx; # Basit mantık, geliştirilebilir
                   else: # Top Left
                       new_x += dx; new_y += dy; new_w -= dx; new_h -= dy
                elif idx == 1: # End Point
                    new_w += dx; new_h += dy
            else:
                is_corner = idx <= 3
                if idx == 0: # TL
                    new_x += dx; new_y += dy; new_w -= dx; new_h -= dy
                elif idx == 1: # TR
                    new_y += dy; new_w += dx; new_h -= dy
                elif idx == 2: # BL
                    new_x += dx; new_w -= dx; new_h += dy
                elif idx == 3: # BR
                    new_w += dx; new_h += dy
                elif idx == 4: # Top
                    new_y += dy; new_h -= dy
                elif idx == 5: # Bottom
                    new_h += dy
                elif idx == 6: # Left
                    new_x += dx; new_w -= dx
                elif idx == 7: # Right
                    new_w += dx

            # Minimum boyut kontrolü (Margin + 20px)
            min_size = self.MARGIN * 2 + 20
            if new_w < min_size: new_w = min_size
            if new_h < min_size: new_h = min_size
            
            # Widget'ı güncelle
            self.setGeometry(int(new_x), int(new_y), int(new_w), int(new_h))
            
            # Logical Rect'i de güncelle (Widget boyutu - 2*Margin)
            log_w = new_w - self.MARGIN * 2
            log_h = new_h - self.MARGIN * 2
            self._logical_rect = QRectF(0, 0, log_w, log_h)
            
            self.update()
            return

        # Cursor Değiştirme
        logic_mouse = self.map_mouse_to_logic(event.globalPos())
        rect = self._logical_rect
        
        if self._get_rotation_handle_rect(rect).contains(logic_mouse):
            self.setCursor(Qt.PointingHandCursor)
            return
            
        handles = self._get_handle_info(rect)
        for i, (htype, r) in enumerate(handles):
            if r.contains(logic_mouse):
                if htype == "corner":
                    if i in [0, 3]: self.setCursor(Qt.SizeFDiagCursor) 
                    else: self.setCursor(Qt.SizeBDiagCursor)          
                else:
                    if i in [4, 5]: self.setCursor(Qt.SizeVerCursor)   
                    else: self.setCursor(Qt.SizeHorCursor)             
                return

        if rect.contains(logic_mouse):
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._rotating = False
        self._resize_handle = None
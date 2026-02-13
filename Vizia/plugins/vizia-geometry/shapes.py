import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint
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

    def __init__(self, parent, shape_type, color, width=160, height=160):
        super().__init__(parent)
        self.shape_type = shape_type
        self.primary_color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        
        self.opacity_val = 255 

        # Widget Ayarları
        # Başlangıçta padding veriyoruz ki handle'lar kesilmesin
        self.padding = 40
        self.resize(width + self.padding, height + self.padding) 
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

        # İç Rect (Çizim alanı) - Widget'ın ortasında başlat
        self.drawing_rect = QRectF(self.padding/2, self.padding/2, width, height)

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
        
        # Dönme işlemi - KENDİ MERKEZİNDE
        # Widget'ın merkezi etrafında koordinat sistemini döndür
        center = self.rect().center()
        
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

        r_draw = self.drawing_rect
        flags = {"flipped": self.is_flipped}
        draw_shape_path(painter, self.shape_type, r_draw, flags)

        # DÜZELTME: Metin Görünümü
        if self.shape_type == "note" and self.text:
            painter.setPen(QColor(0,0,0, 220)) 
            text_rect = r_draw.adjusted(10, 20, -10, -10)
            
            # Yazı boyutunu daha iyi hesapla (Kutunun %'si değil, sığana kadar)
            font_size = 100
            min_size = 8
            
            # Binary search ya da iterative küçültme ile sığdır
            # Basit iterative yaklaşım:
            while font_size > min_size:
                f = QFont("Segoe UI", font_size)
                f.setBold(True)
                fm = QFontMetrics(f)
                
                # Metin bounding rect hesapla
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
            self._draw_handles(painter)

        painter.restore()

    def _draw_handles(self, painter):
        hs = self.HANDLE_SIZE
        sel_pen = QPen(QColor(100, 100, 255), 1.5, Qt.SolidLine)
        painter.setPen(sel_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.drawing_rect)
        
        handles = self._get_handle_info()
        for h_type, rect in handles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            if h_type == "corner":
                painter.drawEllipse(rect)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(100, 100, 255), 2))
                painter.drawEllipse(rect)
            elif h_type == "side":
                painter.drawRoundedRect(rect, 3, 3)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(100, 100, 255), 2))
                painter.drawRoundedRect(rect, 3, 3)

        rot_pos = QPointF(self.drawing_rect.center().x(), self.drawing_rect.top() - self.ROTATION_HANDLE_DIST)
        painter.setPen(QPen(QColor(100, 100, 255), 1.5))
        painter.drawLine(QPointF(self.drawing_rect.center().x(), self.drawing_rect.top()), rot_pos)
        
        painter.setBrush(Qt.white)
        painter.setPen(QPen(QColor(100, 100, 255), 2))
        painter.drawEllipse(rot_pos, hs/1.5, hs/1.5)

    def _get_handle_info(self):
        if self.shape_type == "line":
            r = self.drawing_rect
            hs = self.HANDLE_SIZE
            p1 = r.topLeft()
            p2 = r.bottomRight()
            if self.is_flipped:
                p1 = r.topRight()
                p2 = r.bottomLeft()
            return [
                ("corner", QRectF(p1.x()-hs/2, p1.y()-hs/2, hs, hs)),
                ("corner", QRectF(p2.x()-hs/2, p2.y()-hs/2, hs, hs))
            ]

        hs = self.HANDLE_SIZE
        r = self.drawing_rect
        cx, cy = r.center().x(), r.center().y()
        corners = [
            ("corner", QRectF(r.left()-hs/2, r.top()-hs/2, hs, hs)),      # TL (0)
            ("corner", QRectF(r.right()-hs/2, r.top()-hs/2, hs, hs)),     # TR (1)
            ("corner", QRectF(r.left()-hs/2, r.bottom()-hs/2, hs, hs)),   # BL (2)
            ("corner", QRectF(r.right()-hs/2, r.bottom()-hs/2, hs, hs))   # BR (3)
        ]
        bar_w, bar_h = 16, 6
        sides = [
            ("side", QRectF(cx-bar_w/2, r.top()-bar_h/2, bar_w, bar_h)),       # Top (4)
            ("side", QRectF(cx-bar_w/2, r.bottom()-bar_h/2, bar_w, bar_h)),    # Bottom (5)
            ("side", QRectF(r.left()-bar_h/2, cy-bar_w/2, bar_h, bar_w)),      # Left (6)
            ("side", QRectF(r.right()-bar_h/2, cy-bar_w/2, bar_h, bar_w))      # Right (7)
        ]
        return corners + sides

    def _get_rotation_handle_rect(self):
        hs = self.HANDLE_SIZE
        r = self.drawing_rect
        pos = QPointF(r.center().x(), r.top() - self.ROTATION_HANDLE_DIST)
        return QRectF(pos.x() - hs/2, pos.y() - hs/2, hs, hs)

    # -----------------------------------------------------------------------
    # DÜZELTME: Koordinat Dönüşümleri (Döndürülmüş Uzay için)
    # -----------------------------------------------------------------------
    def map_mouse_to_shape_space(self, global_pos):
        """
        Global fare pozisyonunu, şeklin döndürülmüş (unrotated) yerel koordinat sistemine çevirir.
        Böylece fareyi sağa çektiğinizde, şekil 45 derece dönük olsa bile 'sağ' kenar büyür.
        """
        local_pos = self.mapFromGlobal(global_pos)
        
        # Transformu tersine çevir (Merkeze göre)
        center = self.rect().center()
        t = QTransform()
        t.translate(center.x(), center.y())
        t.rotate(-self.rotation_angle) # Tersine döndür
        t.translate(-center.x(), -center.y())
        
        return t.map(local_pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 1. Tıklama Kontrolü (Hit Test) - DÜZELTME
            # Fareyi 'düzeltilmiş' uzaya çevirip kontrol ediyoruz.
            # Böylece boş köşelere tıklayınca seçilmez.
            
            rotated_mouse = self.map_mouse_to_shape_space(event.globalPos())
            
            # Handle Kontrolü (Düzeltilmiş uzayda)
            handles = self._get_handle_info()
            for i, (htype, rect) in enumerate(handles):
                # Handle rect'leri zaten düzeltilmiş uzayda (drawing_rect'e bağlı)
                if rect.contains(rotated_mouse):
                    self._resize_handle = i
                    self.clicked.emit(self)
                    return

            # Döndürme Tutamağı
            if self._get_rotation_handle_rect().contains(rotated_mouse):
                self._rotating = True
                center = self.rect().center()
                # Döndürme için ekran koordinatlarını kullanmak daha doğal
                local_mouse = self.mapFromGlobal(event.globalPos())
                self._rot_start_angle = math.degrees(math.atan2(local_mouse.y() - center.y(), local_mouse.x() - center.x())) - self.rotation_angle
                self.clicked.emit(self)
                return
            
            # Şekil İçine Tıklama
            if self.drawing_rect.contains(rotated_mouse):
                self._dragging = True
                self._drag_start_pos = event.globalPos() - self.pos()
                self.clicked.emit(self)
                self.setFocus()
            else:
                # Boşluğa tıklandı - Olayı yoksay (Overlay'e geçsin)
                event.ignore()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPos() - self._drag_start_pos)
            return

        if self._rotating:
            center = self.rect().center()
            local_mouse = self.mapFromGlobal(event.globalPos())
            angle = math.degrees(math.atan2(local_mouse.y() - center.y(), local_mouse.x() - center.x()))
            new_angle = angle - self._rot_start_angle
            self.rotation_angle = new_angle
            self.rotation_changed.emit(new_angle)
            self.update()
            return

        if self._resize_handle is not None:
            # DÜZELTME: Mouse pozisyonunu 'düzeltilmiş' uzayda al
            # Bu sayede şekil ne kadar dönük olursa olsun, tutamaklar mantıklı çalışır.
            mouse = self.map_mouse_to_shape_space(event.globalPos())
            r = self.drawing_rect
            
            # Line (Çizgi) Mantığı
            if self.shape_type == "line":
                idx = self._resize_handle
                l, t, r_b, b = r.left(), r.top(), r.right(), r.bottom()
                target_x, target_y = mouse.x(), mouse.y()
                
                if idx == 0: # Start point
                    if self.is_flipped: r_b, t = target_x, target_y
                    else: l, t = target_x, target_y
                elif idx == 1: # End point
                    if self.is_flipped: l, b = target_x, target_y
                    else: r_b, b = target_x, target_y

                new_l = min(l, r_b); new_r = max(l, r_b)
                new_t = min(t, b); new_b = max(t, b)
                self.drawing_rect.setCoords(new_l, new_t, new_r, new_b)

            else:
                # Normal Şekiller - Canva Tarzı Resize
                idx = self._resize_handle
                l, t, r_b, b = r.left(), r.top(), r.right(), r.bottom()
                
                is_corner = idx <= 3
                
                # Sadece ilgili kenarı mouse koordinatına taşı
                if is_corner:
                    # Serbest Köşe
                    if idx == 0: l, t = mouse.x(), mouse.y()       # TL
                    if idx == 1: r_b, t = mouse.x(), mouse.y()     # TR
                    if idx == 2: l, b = mouse.x(), mouse.y()       # BL
                    if idx == 3: r_b, b = mouse.x(), mouse.y()     # BR
                else:
                    # Kenar Esnetme
                    if idx == 4: t = mouse.y()      # Top
                    if idx == 5: b = mouse.y()      # Bottom
                    if idx == 6: l = mouse.x()      # Left
                    if idx == 7: r_b = mouse.x()    # Right
                
                # Rect'i normalize et (negatif genişliği önle)
                self.drawing_rect.setCoords(min(l, r_b), min(t, b), max(l, r_b), max(t, b))
            
            # Widget Boyutunu Güncelle (Kesilmeyi Önle)
            # Drawing Rect + Padding kadar widget'ı büyüt
            needed_w = self.drawing_rect.right() + self.padding
            needed_h = self.drawing_rect.bottom() + self.padding
            
            # Widget küçülürse diye minimum kontrolü yapmıyoruz, 
            # dinamik olarak büyümesi yeterli.
            if needed_w > self.width() or needed_h > self.height():
                 self.resize(max(self.width(), int(needed_w)), max(self.height(), int(needed_h)))

            self.update()
            return

        # Cursor Değiştirme
        # Burada da "düzeltilmiş" koordinat kullanıyoruz ki cursor doğru yerde değişsin
        rotated_mouse = self.map_mouse_to_shape_space(event.globalPos())
        
        if self._get_rotation_handle_rect().contains(rotated_mouse):
            self.setCursor(Qt.PointingHandCursor)
            return
            
        handles = self._get_handle_info()
        for i, (htype, rect) in enumerate(handles):
            if rect.contains(rotated_mouse):
                if htype == "corner":
                    if i in [0, 3]: self.setCursor(Qt.SizeFDiagCursor) 
                    else: self.setCursor(Qt.SizeBDiagCursor)          
                else:
                    if i in [4, 5]: self.setCursor(Qt.SizeVerCursor)   
                    else: self.setCursor(Qt.SizeHorCursor)             
                return

        if self.drawing_rect.contains(rotated_mouse):
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._rotating = False
        self._resize_handle = None
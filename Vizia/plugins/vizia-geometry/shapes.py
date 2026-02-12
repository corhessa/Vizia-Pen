import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QTransform, QFont, QBrush, QCursor

# ---------------------------------------------------------------------------
# Çizim Fonksiyonları (Render Motoru - ORİJİNAL KODLAR KORUNDU)
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

    pen = QPen(QColor(0,0,0, 50), 1)
    old_pen = painter.pen()
    painter.setPen(pen)
    
    line_spacing = max(15, rect.height() / 6)
    y = rect.top() + fold + 10
    while y < rect.bottom() - 10:
        painter.drawLine(QPointF(rect.left() + 10, y), QPointF(rect.right() - 10, y))
        y += line_spacing
    painter.setPen(old_pen)

# ---------------------------------------------------------------------------
# [GÜNCELLENDİ] GeometryShape (Artık QWidget)
# ---------------------------------------------------------------------------
class GeometryShape(QWidget):
    """
    Artık bir QWidget! Bu sayede MainOverlay'e eklenebilir, 
    Z-Order yönetilebilir ve Undo sistemine dahil olabilir.
    """
    clicked = pyqtSignal(object) # Tıklandığında kendini bildirir
    
    HANDLE_SIZE = 12 
    ROTATION_HANDLE_DIST = 35

    def __init__(self, parent, shape_type, color, width=160, height=160):
        super().__init__(parent)
        self.shape_type = shape_type
        self.primary_color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        
        # Widget Ayarları
        self.resize(width + 40, height + 40) # Padding payı
        self.setAttribute(Qt.WA_DeleteOnClose)
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

        # İç Rect (Çizim alanı)
        self.drawing_rect = QRectF(20, 20, width, height)

    def set_selected(self, val):
        self.is_selected = val
        self.update()
        if val: self.raise_() # Seçilince öne getir

    def update_fill(self, is_filled):
        self.filled = is_filled
        self.update()

    # ------ ÇİZİM (Paint Event) ------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dönme işlemi için transform
        center = self.rect().center()
        
        painter.save()
        painter.translate(center)
        painter.rotate(self.rotation_angle)
        painter.translate(-center)

        # Dolgu ve Kenarlık
        if self.filled:
            painter.setBrush(self.primary_color)
        else:
            painter.setBrush(Qt.NoBrush)

        pen = QPen(self.border_color, self.stroke_width)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # Çizim
        r_draw = self.drawing_rect
        flags = {"flipped": self.is_flipped}
        draw_shape_path(painter, self.shape_type, r_draw, flags)

        # Metin (Note tipi için)
        if self.shape_type == "note" and self.text:
            painter.setPen(QColor(0,0,0, 200))
            f = QFont("Segoe UI", 10)
            painter.setFont(f)
            text_rect = r_draw.adjusted(10, 10, -10, -10)
            painter.drawText(text_rect, Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, self.text)

        # Seçim Tutamaçları
        if self.is_selected:
            self._draw_handles(painter)

        painter.restore()

    def _draw_handles(self, painter):
        hs = self.HANDLE_SIZE
        
        # Seçim kutusu
        sel_pen = QPen(QColor(0, 170, 255), 1, Qt.DashLine)
        painter.setPen(sel_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.drawing_rect)
        
        painter.setBrush(QColor(0, 170, 255))
        painter.setPen(QPen(Qt.white, 2))
        
        # Köşe ve Kenar noktaları
        for rect in self._get_handle_rects():
            painter.drawEllipse(rect)

        # Döndürme kolu
        rot_pos = QPointF(self.drawing_rect.center().x(), self.drawing_rect.top() - self.ROTATION_HANDLE_DIST)
        painter.setPen(QPen(QColor(255, 170, 0), 1, Qt.DashLine))
        painter.drawLine(QPointF(self.drawing_rect.center().x(), self.drawing_rect.top()), rot_pos)
        
        painter.setBrush(QColor(255, 170, 0))
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(rot_pos, hs/2, hs/2)

    # ------ HESAPLAMALAR ------
    def _get_handle_rects(self):
        hs = self.HANDLE_SIZE
        r = self.drawing_rect
        cx, cy = r.center().x(), r.center().y()
        
        # Sırasıyla: Sol-Üst, Sağ-Üst, Sol-Alt, Sağ-Alt, Üst-Orta, Alt-Orta, Sol-Orta, Sağ-Orta
        points = [
            r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight(),
            QPointF(cx, r.top()), QPointF(cx, r.bottom()), QPointF(r.left(), cy), QPointF(r.right(), cy)
        ]
        return [QRectF(p.x() - hs/2, p.y() - hs/2, hs, hs) for p in points]

    def _get_rotation_handle_rect(self):
        hs = self.HANDLE_SIZE
        r = self.drawing_rect
        pos = QPointF(r.center().x(), r.top() - self.ROTATION_HANDLE_DIST)
        return QRectF(pos.x() - hs/2, pos.y() - hs/2, hs, hs)

    def _map_to_local_rotation(self, global_pos):
        """Global fare pozisyonunu, şeklin dönme açısına göre yerel koordinata çevirir"""
        center = self.mapToGlobal(self.rect().center().toPoint())
        t = QTransform()
        t.translate(center.x(), center.y())
        t.rotate(-self.rotation_angle)
        t.translate(-center.x(), -center.y())
        return t.map(global_pos)

    # ------ MOUSE OLAYLARI (QWidget Eventleri) ------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self) # Toolbox'a haber ver
            
            # Global koordinatı, şeklin dönüşüne göre ayarla
            local_mouse = event.pos() # Zaten widget içi koordinat ama döndürme mantığı için logic gerekebilir
            # Basitleştirilmiş: Widget zaten kare olduğu için rect üzerinden işlem yapıyoruz
            
            # Handle Kontrolü
            for i, rect in enumerate(self._get_handle_rects()):
                if rect.contains(local_mouse):
                    self._resize_handle = i
                    return

            if self._get_rotation_handle_rect().contains(local_mouse):
                self._rotating = True
                center = self.rect().center()
                self._rot_start_angle = math.degrees(math.atan2(event.y() - center.y(), event.x() - center.x())) - self.rotation_angle
                return
            
            # Taşıma
            if self.drawing_rect.contains(local_mouse):
                self._dragging = True
                self._drag_start_pos = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPos() - self._drag_start_pos)
            return

        if self._rotating:
            center = self.rect().center()
            angle = math.degrees(math.atan2(event.y() - center.y(), event.x() - center.x()))
            self.rotation_angle = angle - self._rot_start_angle
            self.update()
            return

        if self._resize_handle is not None:
            # Resize mantığı (Basitleştirilmiş)
            # Burada widget'ın geometry'sini değiştirmek yerine drawing_rect'i güncellemek daha sağlıklı
            # Ancak widget boyutu da artmalı.
            # Şimdilik basitçe drawing_rect güncelliyoruz
            mouse = event.pos()
            r = self.drawing_rect
            idx = self._resize_handle
            
            min_size = 20
            l, t, r_b, b = r.left(), r.top(), r.right(), r.bottom()

            if idx in [0, 2, 6]: l = min(mouse.x(), r_b - min_size)
            if idx in [1, 3, 7]: r_b = max(mouse.x(), l + min_size)
            if idx in [0, 1, 4]: t = min(mouse.y(), b - min_size)
            if idx in [2, 3, 5]: b = max(mouse.y(), t + min_size)
            
            self.drawing_rect.setCoords(l, t, r_b, b)
            self.update()
            
            # Widget boyutunu çizime göre genişletmek gerekirse:
            # self.resize(int(r_b + 40), int(b + 40)) 
            return

        # Cursor değiştirme
        mouse = event.pos()
        if self._get_rotation_handle_rect().contains(mouse):
            self.setCursor(Qt.CrossCursor)
        elif any(r.contains(mouse) for r in self._get_handle_rects()):
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.drawing_rect.contains(mouse):
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._rotating = False
        self._resize_handle = None
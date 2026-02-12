import math
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QTransform, QFont

# ---------------------------------------------------------------------------
# Çizim Fonksiyonları (Render Motoru)
# ---------------------------------------------------------------------------
def draw_shape_path(painter, shape_type, rect, extra_flags=None):
    """
    Verilen rect içine şekil çizer.
    *extra_flags*: Şekle özel ek durumlar (örn: çizgi yönü)
    """
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
        # DÜZELTME: Çapraz çizgi yönünü kontrol et
        if extra_flags.get("flipped", False):
            # Anti-diagonal (Sağ-Üst <-> Sol-Alt veya tam tersi)
            painter.drawLine(rect.topRight(), rect.bottomLeft())
        else:
            # Normal (Sol-Üst <-> Sağ-Alt)
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
# Gelişmiş Şekil Sınıfı
# ---------------------------------------------------------------------------
class CanvasShape:
    """
    Canvas üzerinde çizilen şekil. 
    Koordinat dönüşümleri (map_to_local) içerir.
    """
    HANDLE_SIZE = 12 
    ROTATION_HANDLE_DIST = 35

    def __init__(self, shape_type, color, x=0.0, y=0.0, w=160.0, h=160.0):
        self.shape_type = shape_type
        self.color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        # Rect her zaman şeklin DÜZ (0 derece) halindeki sınırlarıdır
        self.rect = QRectF(x, y, w, h)
        self.rotation = 0.0
        self.filled = True
        self.selected = False
        self.text = ""
        
        # Çizgi yönü (True ise anti-diagonal / şeklindedir)
        self.is_flipped = False
        
        self._drag_offset = None      
        self._resize_handle = None    
        self._rotating = False        
        self._rot_start_angle = 0.0   

    def snapshot(self):
        return {
            "shape_type": self.shape_type,
            "color": QColor(self.color),
            "border_color": QColor(self.border_color),
            "stroke_width": self.stroke_width,
            "rect": QRectF(self.rect),
            "rotation": self.rotation,
            "filled": self.filled,
            "text": self.text,
            "is_flipped": self.is_flipped # Kaydet
        }

    # ------ MATEMATİKSEL DÖNÜŞÜMLER ------
    
    def map_from_scene(self, scene_pos):
        """Global (ekran) koordinatını, şeklin kendi (döndürülmüş) yerel koordinatına çevirir."""
        center = self.rect.center()
        t = QTransform()
        t.translate(center.x(), center.y())
        t.rotate(-self.rotation) # Tersi yönde çevir
        t.translate(-center.x(), -center.y())
        return t.map(scene_pos)

    # ------ ÇİZİM ------
    
    def paint(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.save()

        center = self.rect.center()
        painter.translate(center)
        painter.rotate(self.rotation)
        painter.translate(-center)

        if self.filled:
            painter.setBrush(self.color)
        else:
            painter.setBrush(Qt.NoBrush)

        pen = QPen(self.border_color, self.stroke_width)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        inset = self.stroke_width / 2
        r_draw = self.rect.adjusted(inset, inset, -inset, -inset)
        
        # Flags gönder
        flags = {"flipped": self.is_flipped}
        draw_shape_path(painter, self.shape_type, r_draw, flags)

        if self.shape_type == "note" and self.text:
            painter.setPen(QColor(0,0,0, 200))
            f = QFont("Segoe UI", 10)
            painter.setFont(f)
            text_rect = r_draw.adjusted(10, 10, -10, -10)
            painter.drawText(text_rect, Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, self.text)

        if self.selected:
            sel_pen = QPen(QColor(0, 170, 255), 1, Qt.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect)
            
            painter.restore() 
            painter.save()
            painter.translate(center)
            painter.rotate(self.rotation)
            painter.translate(-center)
            
            self._draw_handles(painter)

        painter.restore()

    def _draw_handles(self, painter):
        hs = self.HANDLE_SIZE
        painter.setBrush(QColor(0, 170, 255))
        painter.setPen(QPen(Qt.white, 2))
        
        for rect in self._handle_rects() + self._edge_handle_rects():
            painter.drawEllipse(rect)

        rot_pos = self._rotation_handle_pos()
        painter.setPen(QPen(QColor(255, 170, 0), 1, Qt.DashLine))
        painter.drawLine(QPointF(self.rect.center().x(), self.rect.top()), rot_pos)
        
        painter.setBrush(QColor(255, 170, 0))
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(rot_pos, hs/2, hs/2)

    # ------ HESAPLAMALAR ------

    def _handle_rects(self):
        hs = self.HANDLE_SIZE
        r = self.rect
        return [
            QRectF(r.left() - hs/2, r.top() - hs/2, hs, hs),
            QRectF(r.right() - hs/2, r.top() - hs/2, hs, hs),
            QRectF(r.left() - hs/2, r.bottom() - hs/2, hs, hs),
            QRectF(r.right() - hs/2, r.bottom() - hs/2, hs, hs),
        ]

    def _edge_handle_rects(self):
        hs = self.HANDLE_SIZE
        r = self.rect
        cx, cy = r.center().x(), r.center().y()
        return [
            QRectF(cx - hs/2, r.top() - hs/2, hs, hs),
            QRectF(cx - hs/2, r.bottom() - hs/2, hs, hs),
            QRectF(r.left() - hs/2, cy - hs/2, hs, hs),
            QRectF(r.right() - hs/2, cy - hs/2, hs, hs),
        ]

    def _rotation_handle_pos(self):
        return QPointF(self.rect.center().x(), self.rect.top() - self.ROTATION_HANDLE_DIST)

    # ------ ETKİLEŞİM ------

    def contains(self, global_point):
        local_point = self.map_from_scene(global_point)
        # Çizgiler için daha geniş tıklama alanı
        if self.shape_type == "line":
             # Basitçe rect içinde mi diye bakıyoruz ama çizgi ince olabilir.
             # Kullanıcı kolay seçsin diye rect zaten bounding box.
             pass 
        return self.rect.contains(local_point)

    def handle_at(self, global_point):
        local_point = self.map_from_scene(global_point)
        rot_pos = self._rotation_handle_pos()
        
        if (local_point - rot_pos).manhattanLength() < self.HANDLE_SIZE * 1.5:
            return "rotate"
        for i, rect in enumerate(self._handle_rects()):
            if rect.adjusted(-5,-5,5,5).contains(local_point):
                return i
        for i, rect in enumerate(self._edge_handle_rects()):
            if rect.adjusted(-5,-5,5,5).contains(local_point):
                return i + 4
        return None

    def start_move(self, global_pos):
        self._drag_offset = global_pos - self.rect.topLeft()

    def do_move(self, global_pos):
        if self._drag_offset is not None:
            self.rect.moveTopLeft(global_pos - self._drag_offset)

    def end_move(self):
        self._drag_offset = None

    def start_resize(self, handle_idx, global_pos):
        if handle_idx == "rotate":
            self._rotating = True
            center = self.rect.center()
            self._rot_start_angle = math.degrees(
                math.atan2(global_pos.y() - center.y(), global_pos.x() - center.x())
            ) - self.rotation
        else:
            self._resize_handle = handle_idx

    def do_resize(self, global_pos):
        if self._rotating:
            center = self.rect.center()
            current_angle = math.degrees(
                math.atan2(global_pos.y() - center.y(), global_pos.x() - center.x())
            )
            self.rotation = current_angle - self._rot_start_angle
            return

        if self._resize_handle is None:
            return

        local_pos = self.map_from_scene(global_pos)
        r = self.rect
        idx = self._resize_handle
        min_size = 20

        left, top, right, bottom = r.left(), r.top(), r.right(), r.bottom()

        if idx in [0, 2, 6]: left = min(local_pos.x(), right - min_size)
        if idx in [1, 3, 7]: right = max(local_pos.x(), left + min_size)
        if idx in [0, 1, 4]: top = min(local_pos.y(), bottom - min_size)
        if idx in [2, 3, 5]: bottom = max(local_pos.y(), top + min_size)

        self.rect.setCoords(left, top, right, bottom)

    def end_resize(self):
        self._resize_handle = None
        self._rotating = False
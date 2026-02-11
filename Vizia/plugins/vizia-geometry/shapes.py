# plugins/vizia-geometry/shapes.py
import math
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QTransform, QFont


def draw_shape_path(painter, shape_type, rect):
    """Verilen rect içine şekil çizer (önizleme ve ana çizim için ortak)."""
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
    x = rect.left()
    while x < rect.right():
        painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
        x += step
    y = rect.top()
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
    """Ok (arrow) şekli çizer – sağa bakan ok."""
    w = rect.width()
    h = rect.height()
    shaft_h = h * 0.35
    head_start = w * 0.55

    path = QPainterPath()
    # Gövde sol üst
    path.moveTo(rect.left(), rect.center().y() - shaft_h / 2)
    path.lineTo(rect.left() + head_start, rect.center().y() - shaft_h / 2)
    # Ok başı üst
    path.lineTo(rect.left() + head_start, rect.top())
    # Ok ucu
    path.lineTo(rect.right(), rect.center().y())
    # Ok başı alt
    path.lineTo(rect.left() + head_start, rect.bottom())
    path.lineTo(rect.left() + head_start, rect.center().y() + shaft_h / 2)
    # Gövde sol alt
    path.lineTo(rect.left(), rect.center().y() + shaft_h / 2)
    path.closeSubpath()
    painter.drawPath(path)


def _draw_note_path(painter, rect):
    """Not kutusu çizer – köşe kıvrımlı kağıt."""
    fold = min(rect.width(), rect.height()) * 0.18
    path = QPainterPath()
    path.moveTo(rect.left(), rect.top())
    path.lineTo(rect.right() - fold, rect.top())
    path.lineTo(rect.right(), rect.top() + fold)
    path.lineTo(rect.right(), rect.bottom())
    path.lineTo(rect.left(), rect.bottom())
    path.closeSubpath()
    painter.drawPath(path)

    # Kıvrım üçgeni
    old_brush = painter.brush()
    fold_color = QColor(painter.brush().color())
    fold_color.setAlpha(min(255, fold_color.alpha() + 40))
    painter.setBrush(fold_color)
    fold_path = QPainterPath()
    fold_path.moveTo(rect.right() - fold, rect.top())
    fold_path.lineTo(rect.right() - fold, rect.top() + fold)
    fold_path.lineTo(rect.right(), rect.top() + fold)
    fold_path.closeSubpath()
    painter.drawPath(fold_path)
    painter.setBrush(old_brush)

    # Not çizgileri
    line_pen = QPen(QColor(255, 255, 255, 60), 1)
    old_pen = painter.pen()
    painter.setPen(line_pen)
    margin = rect.width() * 0.12
    line_y = rect.top() + fold + margin
    while line_y < rect.bottom() - margin:
        painter.drawLine(
            QPointF(rect.left() + margin, line_y),
            QPointF(rect.right() - margin, line_y),
        )
        line_y += max(14, rect.height() * 0.12)
    painter.setPen(old_pen)


class CanvasShape:
    """Canvas üzerinde çizilen şekil nesnesi (pencere değil)."""

    HANDLE_SIZE = 10
    ROTATION_HANDLE_DIST = 28  # Döndürme tutamağının şekilden uzaklığı (piksel)

    def __init__(self, shape_type, color, x=0.0, y=0.0, w=160.0, h=160.0):
        self.shape_type = shape_type
        self.color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        self.rect = QRectF(x, y, w, h)
        self.rotation = 0.0          # derece cinsinden döndürme
        self.filled = True           # dolgu açık/kapalı
        self.selected = False
        self.locked = False
        self.text = ""               # not kutusu için metin
        self._drag_offset = None
        self._resize_handle = None
        self._rotating = False
        self._rot_start_angle = 0.0

    def snapshot(self):
        """Geri alma için şeklin kopyasını döndürür."""
        return {
            "shape_type": self.shape_type,
            "color": QColor(self.color),
            "border_color": QColor(self.border_color),
            "stroke_width": self.stroke_width,
            "rect": QRectF(self.rect),
            "rotation": self.rotation,
            "filled": self.filled,
            "text": self.text,
        }

    # ------ çizim ------
    def paint(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.save()

        # Döndürme
        center = self.rect.center()
        painter.translate(center)
        painter.rotate(self.rotation)
        painter.translate(-center)

        # Dolgu
        if self.filled:
            painter.setBrush(self.color)
        else:
            painter.setBrush(Qt.NoBrush)

        pen = QPen(self.border_color, self.stroke_width)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        r = self.rect.adjusted(
            self.stroke_width, self.stroke_width,
            -self.stroke_width, -self.stroke_width,
        )

        draw_shape_path(painter, self.shape_type, r)

        # Not kutusu metin
        if self.shape_type == "note" and self.text:
            painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
            painter.setFont(QFont("sans-serif", 10))
            text_rect = r.adjusted(r.width() * 0.1, r.height() * 0.25,
                                   -r.width() * 0.1, -r.height() * 0.05)
            painter.drawText(text_rect, Qt.TextWordWrap, self.text)

        painter.restore()

        if self.selected:
            self._draw_handles(painter)

    def _draw_handles(self, painter):
        """Belirgin yuvarlak köşe tutamakları + döndürme tutamağı çizer."""
        hs = self.HANDLE_SIZE
        # Köşe tutamakları – yuvarlak, belirgin
        for hr in self._handle_rects():
            painter.setBrush(QColor(0, 170, 255))
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(hr)

        # Kenar orta tutamakları – küçük, yatay/dikey boyutlandırma
        for er in self._edge_handle_rects():
            painter.setBrush(QColor(0, 140, 220))
            painter.setPen(QPen(QColor(255, 255, 255), 1.5))
            painter.drawEllipse(er)

        # Döndürme tutamağı – üstte
        rot_pos = self._rotation_handle_pos()
        painter.setBrush(QColor(255, 165, 0))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawEllipse(rot_pos, hs / 2, hs / 2)
        # Bağlantı çizgisi
        painter.setPen(QPen(QColor(255, 165, 0, 150), 1.5, Qt.DashLine))
        painter.drawLine(QPointF(self.rect.center().x(), self.rect.top()), rot_pos)

    def _handle_rects(self):
        hs = self.HANDLE_SIZE
        r = self.rect
        return [
            QRectF(r.left() - hs / 2, r.top() - hs / 2, hs, hs),
            QRectF(r.right() - hs / 2, r.top() - hs / 2, hs, hs),
            QRectF(r.left() - hs / 2, r.bottom() - hs / 2, hs, hs),
            QRectF(r.right() - hs / 2, r.bottom() - hs / 2, hs, hs),
        ]

    def _edge_handle_rects(self):
        """Kenar ortası tutamakları (yatay/dikey boyutlandırma)."""
        hs = self.HANDLE_SIZE * 0.7
        r = self.rect
        cx, cy = r.center().x(), r.center().y()
        return [
            QRectF(cx - hs / 2, r.top() - hs / 2, hs, hs),       # üst orta
            QRectF(cx - hs / 2, r.bottom() - hs / 2, hs, hs),     # alt orta
            QRectF(r.left() - hs / 2, cy - hs / 2, hs, hs),       # sol orta
            QRectF(r.right() - hs / 2, cy - hs / 2, hs, hs),      # sağ orta
        ]

    def _rotation_handle_pos(self):
        return QPointF(self.rect.center().x(),
                       self.rect.top() - self.ROTATION_HANDLE_DIST)

    # ------ isabet testi ------
    def contains(self, point):
        if self.rotation == 0:
            return self.rect.contains(point)
        # Döndürülmüş şekil için noktayı ters döndür
        center = self.rect.center()
        t = QTransform()
        t.translate(center.x(), center.y())
        t.rotate(-self.rotation)
        t.translate(-center.x(), -center.y())
        unrotated = t.map(point)
        return self.rect.contains(unrotated)

    def handle_at(self, point):
        # Döndürme tutamağı
        rot_pos = self._rotation_handle_pos()
        if (point - rot_pos).manhattanLength() < self.HANDLE_SIZE + 6:
            return "rotate"
        # Köşe tutamakları
        for idx, hr in enumerate(self._handle_rects()):
            if hr.adjusted(-5, -5, 5, 5).contains(point):
                return idx
        # Kenar tutamakları
        for idx, er in enumerate(self._edge_handle_rects()):
            if er.adjusted(-5, -5, 5, 5).contains(point):
                return 4 + idx  # 4=üst, 5=alt, 6=sol, 7=sağ
        return None

    # ------ etkileşim ------
    def start_move(self, pos):
        self._drag_offset = pos - self.rect.topLeft()

    def do_move(self, pos):
        if self._drag_offset is not None:
            self.rect.moveTopLeft(pos - self._drag_offset)

    def end_move(self):
        self._drag_offset = None

    def start_resize(self, handle_idx, pos):
        if handle_idx == "rotate":
            self._rotating = True
            center = self.rect.center()
            self._rot_start_angle = math.degrees(
                math.atan2(pos.y() - center.y(), pos.x() - center.x())
            ) - self.rotation
        else:
            self._resize_handle = handle_idx

    def do_resize(self, pos):
        if self._rotating:
            center = self.rect.center()
            angle = math.degrees(
                math.atan2(pos.y() - center.y(), pos.x() - center.x())
            )
            self.rotation = angle - self._rot_start_angle
            return

        if self._resize_handle is None:
            return
        r = self.rect
        idx = self._resize_handle
        min_size = 30
        if idx == 0:  # sol üst
            r.setTopLeft(QPointF(min(pos.x(), r.right() - min_size),
                                  min(pos.y(), r.bottom() - min_size)))
        elif idx == 1:  # sağ üst
            r.setTopRight(QPointF(max(pos.x(), r.left() + min_size),
                                   min(pos.y(), r.bottom() - min_size)))
        elif idx == 2:  # sol alt
            r.setBottomLeft(QPointF(min(pos.x(), r.right() - min_size),
                                     max(pos.y(), r.top() + min_size)))
        elif idx == 3:  # sağ alt
            r.setBottomRight(QPointF(max(pos.x(), r.left() + min_size),
                                      max(pos.y(), r.top() + min_size)))
        elif idx == 4:  # üst orta
            r.setTop(min(pos.y(), r.bottom() - min_size))
        elif idx == 5:  # alt orta
            r.setBottom(max(pos.y(), r.top() + min_size))
        elif idx == 6:  # sol orta
            r.setLeft(min(pos.x(), r.right() - min_size))
        elif idx == 7:  # sağ orta
            r.setRight(max(pos.x(), r.left() + min_size))

    def end_resize(self):
        self._resize_handle = None
        self._rotating = False
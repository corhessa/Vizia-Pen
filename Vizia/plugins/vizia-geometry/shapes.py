import math
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QTransform, 
    QFont, QBrush, QCursor, QTextOption, QFontMetrics,
    QLinearGradient
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
    elif shape_type == "cylinder":
        color = painter.brush().color()
        _draw_cylinder_path(painter, rect, color)
    elif shape_type == "grid":
        _draw_grid_path(painter, rect)
    elif shape_type == "star":
        _draw_star_path(painter, rect)
    elif shape_type == "arrow":
        _draw_arrow_path(painter, rect)
    elif shape_type == "note":
        _draw_note_path(painter, rect)
    elif shape_type == "line":
        if extra_flags.get("flipped", False):
            painter.drawLine(rect.topRight(), rect.bottomLeft())
        else:
            painter.drawLine(rect.topLeft(), rect.bottomRight())

def _draw_cylinder_path(painter, rect, base_color):
    w = rect.width()
    h = rect.height()
    el_h = min(h * 0.25, w * 0.5) 
    
    if base_color.alpha() == 0:
        base_color = QColor(200, 200, 200, 50)
        
    light_color = base_color.lighter(130)
    dark_color = base_color.darker(110)
    
    painter.save()
    painter.setPen(Qt.NoPen) 
    
    body_path = QPainterPath()
    body_path.moveTo(rect.left(), rect.top() + el_h/2)
    body_path.lineTo(rect.left(), rect.bottom() - el_h/2)
    body_path.arcTo(QRectF(rect.left(), rect.bottom() - el_h, w, el_h), 180, 180)
    body_path.lineTo(rect.right(), rect.top() + el_h/2)
    body_path.arcTo(QRectF(rect.left(), rect.top(), w, el_h), 0, -180)
    body_path.closeSubpath()
    
    grad = QLinearGradient(rect.left(), 0, rect.right(), 0)
    grad.setColorAt(0.0, dark_color)
    grad.setColorAt(0.2, base_color)
    grad.setColorAt(0.5, light_color)
    grad.setColorAt(0.8, base_color)
    grad.setColorAt(1.0, dark_color)
    
    painter.setBrush(QBrush(grad))
    painter.drawPath(body_path)
    
    painter.setBrush(QBrush(light_color))
    painter.drawEllipse(QRectF(rect.left(), rect.top(), w, el_h))
    
    painter.restore()
    
    old_pen = painter.pen()
    if old_pen.style() != Qt.NoPen:
        painter.drawEllipse(QRectF(rect.left(), rect.top(), w, el_h))
        painter.drawArc(QRectF(rect.left(), rect.bottom() - el_h, w, el_h), 180 * 16, 180 * 16)
        painter.drawLine(QPointF(rect.left(), rect.top() + el_h/2), QPointF(rect.left(), rect.bottom() - el_h/2))
        painter.drawLine(QPointF(rect.right(), rect.top() + el_h/2), QPointF(rect.right(), rect.bottom() - el_h/2))

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
    MARGIN = 50 

    def __init__(self, parent, shape_type, color, width=160, height=160):
        super().__init__(parent)
        self.shape_type = shape_type
        self.primary_color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        
        self.opacity_val = 255 
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.ClickFocus)
        
        self.rotation_angle = 0.0
        self.filled = True
        self.is_selected = False
        self.text = ""
        self.is_flipped = False
        
        self._resize_handle = None    
        self._rotating = False
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._rot_start_angle = 0.0   
        self._anchor_pos_parent = None 
        self._rotation_pivot_parent = None 

        if self.shape_type == "line":
            self.line_p1 = QPointF(self.MARGIN, self.MARGIN)
            self.line_p2 = QPointF(self.MARGIN + width, self.MARGIN + height)
            self.resize(width + self.MARGIN * 2, height + self.MARGIN * 2)
            self.show()
        else:
            self._logical_rect = QRectF(0, 0, width, height)
            self.update_widget_size()
            self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        # Menünün arkada kalmasını engelleyen kritik bayrak
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowStaysOnTopHint) 
        menu.setStyleSheet("""
            QMenu { background-color: #2c2c2e; color: white; border: 1px solid #48484a; border-radius: 8px; padding: 5px; font-family: 'Segoe UI'; font-size: 13px; }
            QMenu::item { padding: 6px 25px; border-radius: 4px; }
            QMenu::item:selected { background-color: #007aff; }
            QMenu::separator { height: 1px; background-color: #48484a; margin: 4px 10px; }
        """)
        a_front = menu.addAction("Öne Getir")
        a_back = menu.addAction("Geriye Gönder")
        menu.addSeparator()
        a_dup = menu.addAction("Çoğalt")
        a_del = menu.addAction("Sil")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == a_front: self.raise_()
        elif action == a_back: self.lower()
        elif action == a_del: self.close()
        elif action == a_dup:
            if self.shape_type == "line":
                new_shape = GeometryShape(self.parentWidget(), self.shape_type, self.primary_color.name(), self.width() - self.MARGIN*2, self.height() - self.MARGIN*2)
            else:
                new_shape = GeometryShape(self.parentWidget(), self.shape_type, self.primary_color.name(), self._logical_rect.width(), self._logical_rect.height())
            
            new_shape.opacity_val = self.opacity_val
            new_shape.rotation_angle = self.rotation_angle
            new_shape.filled = self.filled
            new_shape.text = self.text
            new_shape.is_flipped = self.is_flipped
            new_shape.stroke_width = self.stroke_width
            
            if self.shape_type == "line":
                new_shape.line_p1 = QPointF(self.line_p1)
                new_shape.line_p2 = QPointF(self.line_p2)
                new_shape.resize(self.size())
            else:
                new_shape._logical_rect = QRectF(self._logical_rect)
                new_shape.update_widget_size()
            
            new_shape.move(self.x() + 20, self.y() + 20)
            new_shape.show()
            
            parent_overlay = self.parentWidget()
            if hasattr(parent_overlay, 'plugin_windows'):
                parent_overlay.plugin_windows.register(new_shape)

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
            
    # ------ GEOMETRİ GÜNCELLEME ------
    def update_widget_size(self, parent_anchor=None, new_anchor_logic=None, rotation_pivot=None):
        if self.shape_type == "line": return
        
        parent_center_initial = self.pos() + self.rect().center()
        
        t = QTransform().rotate(self.rotation_angle)
        w, h = self._logical_rect.width(), self._logical_rect.height()
        centered_rect = QRectF(-w/2, -h/2, w, h)
        rotated_rect = t.mapRect(centered_rect)
        
        new_widget_w = rotated_rect.width() + self.MARGIN * 2
        new_widget_h = rotated_rect.height() + self.MARGIN * 2
        
        self.resize(int(new_widget_w), int(new_widget_h))
        
        if rotation_pivot is not None:
            new_local_center = QPoint(int(new_widget_w/2), int(new_widget_h/2))
            self.move(rotation_pivot - new_local_center)
        elif parent_anchor is not None and new_anchor_logic is not None:
            new_local_anchor = t.map(new_anchor_logic) + QPointF(new_widget_w/2, new_widget_h/2)
            self.move((parent_anchor - new_local_anchor).toPoint())
        else:
            new_local_center = QPoint(int(new_widget_w/2), int(new_widget_h/2))
            self.move(parent_center_initial - new_local_center)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        final_color = QColor(self.primary_color)
        final_color.setAlpha(self.opacity_val)

        if self.shape_type == "line":
            line_pen_color = QColor(final_color) 
            line_pen_color.setAlpha(self.opacity_val)
            pen = QPen(line_pen_color, self.stroke_width)
            pen.setJoinStyle(Qt.RoundJoin)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            painter.drawLine(self.line_p1, self.line_p2)
            
            if self.is_selected:
                hs = self.HANDLE_SIZE
                painter.setPen(Qt.NoPen)
                painter.setBrush(Qt.white)
                
                r1 = QRectF(self.line_p1.x() - hs/2, self.line_p1.y() - hs/2, hs, hs)
                r2 = QRectF(self.line_p2.x() - hs/2, self.line_p2.y() - hs/2, hs, hs)
                
                painter.drawEllipse(r1)
                painter.drawEllipse(r2)
                
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(100, 100, 255), 2))
                painter.drawEllipse(r1)
                painter.drawEllipse(r2)
            return

        center = self.rect().center()
        painter.translate(center)
        painter.rotate(self.rotation_angle)
        
        w, h = self._logical_rect.width(), self._logical_rect.height()
        draw_rect = QRectF(-w/2, -h/2, w, h)

        if self.shape_type == "cylinder":
             painter.setBrush(final_color) 
        elif self.filled:
            painter.setBrush(final_color)
        else:
            painter.setBrush(Qt.NoBrush)

        pen = QPen(self.border_color, self.stroke_width)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        flags = {"flipped": self.is_flipped}
        draw_shape_path(painter, self.shape_type, draw_rect, flags)

        if self.shape_type == "note" and self.text:
            painter.setPen(QColor(0,0,0, 220)) 
            text_rect = draw_rect.adjusted(10, 20, -10, -10)
            
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
            self._draw_handles(painter, draw_rect)

    def _draw_handles(self, painter, rect):
        hs = self.HANDLE_SIZE
        bound_rect = rect.adjusted(-4, -4, 4, 4)
        
        sel_pen = QPen(QColor(100, 100, 255), 1.5, Qt.SolidLine)
        painter.setPen(sel_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(bound_rect)
        
        handles = self._get_handle_info(bound_rect)
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

        rot_pos = QPointF(bound_rect.center().x(), bound_rect.top() - self.ROTATION_HANDLE_DIST)
        painter.setPen(QPen(QColor(100, 100, 255), 1.5))
        painter.drawLine(QPointF(bound_rect.center().x(), bound_rect.top()), rot_pos)
        
        painter.setBrush(Qt.white)
        painter.setPen(QPen(QColor(100, 100, 255), 2))
        painter.drawEllipse(rot_pos, hs/1.5, hs/1.5)

    def _get_handle_info(self, rect):
        hs = self.HANDLE_SIZE
        cx, cy = rect.center().x(), rect.center().y()
        corners = [
            ("corner", QRectF(rect.left()-hs/2, rect.top()-hs/2, hs, hs)),      
            ("corner", QRectF(rect.right()-hs/2, rect.top()-hs/2, hs, hs)),     
            ("corner", QRectF(rect.left()-hs/2, rect.bottom()-hs/2, hs, hs)),   
            ("corner", QRectF(rect.right()-hs/2, rect.bottom()-hs/2, hs, hs))   
        ]
        bar_w, bar_h = 16, 6
        sides = [
            ("side", QRectF(cx-bar_w/2, rect.top()-bar_h/2, bar_w, bar_h)),       
            ("side", QRectF(cx-bar_w/2, rect.bottom()-bar_h/2, bar_w, bar_h)),    
            ("side", QRectF(rect.left()-bar_h/2, cy-bar_w/2, bar_h, bar_w)),      
            ("side", QRectF(rect.right()-bar_h/2, cy-bar_w/2, bar_h, bar_w))      
        ]
        return corners + sides

    def _get_rotation_handle_rect(self, rect):
        hs = self.HANDLE_SIZE
        pos = QPointF(rect.center().x(), rect.top() - self.ROTATION_HANDLE_DIST)
        return QRectF(pos.x() - hs/2, pos.y() - hs/2, hs, hs)

    def map_mouse_to_logic(self, global_pos):
        local_pos = self.mapFromGlobal(global_pos)
        widget_center = self.rect().center()
        
        dx = local_pos.x() - widget_center.x()
        dy = local_pos.y() - widget_center.y()
        
        angle_rad = math.radians(-self.rotation_angle)
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        
        return QPointF(rx, ry)

    def _get_opposite_handle_index(self, idx):
        if idx == 0: return 3
        if idx == 1: return 2
        if idx == 2: return 1
        if idx == 3: return 0
        if idx == 4: return 5
        if idx == 5: return 4
        if idx == 6: return 7
        if idx == 7: return 6
        return -1

    def _get_logical_point_from_handle_index(self, idx):
        w, h = self._logical_rect.width(), self._logical_rect.height()
        draw_rect = QRectF(-w/2, -h/2, w, h)
        if idx == 0: return draw_rect.topLeft()
        if idx == 1: return draw_rect.topRight()
        if idx == 2: return draw_rect.bottomLeft()
        if idx == 3: return draw_rect.bottomRight()
        if idx == 4: return QPointF(0, draw_rect.top())
        if idx == 5: return QPointF(0, draw_rect.bottom())
        if idx == 6: return QPointF(draw_rect.left(), 0)
        if idx == 7: return QPointF(draw_rect.right(), 0)
        return QPointF(0,0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.shape_type == "line":
                local_mouse = event.pos()
                hs = self.HANDLE_SIZE
                r1 = QRectF(self.line_p1.x() - hs, self.line_p1.y() - hs, hs*2, hs*2) 
                r2 = QRectF(self.line_p2.x() - hs, self.line_p2.y() - hs, hs*2, hs*2)
                
                if r1.contains(local_mouse):
                    self._resize_handle = 0
                    self.clicked.emit(self)
                    return
                elif r2.contains(local_mouse):
                    self._resize_handle = 1
                    self.clicked.emit(self)
                    return
                else:
                    self._dragging = True
                    self._drag_start_pos = event.globalPos() - self.pos()
                    self.clicked.emit(self)
                    self.setFocus()
                    return

            logic_mouse = self.map_mouse_to_logic(event.globalPos())
            w, h = self._logical_rect.width(), self._logical_rect.height()
            draw_rect = QRectF(-w/2, -h/2, w, h).adjusted(-4,-4,4,4)
            
            handles = self._get_handle_info(draw_rect)
            for i, (htype, h_rect) in enumerate(handles):
                if h_rect.contains(logic_mouse):
                    self._resize_handle = i
                    self.clicked.emit(self)
                    self._drag_start_pos = event.globalPos()
                    self._start_rect = QRectF(self._logical_rect)
                    
                    opp_idx = self._get_opposite_handle_index(i)
                    if opp_idx != -1:
                        anchor_logic = self._get_logical_point_from_handle_index(opp_idx)
                        t = QTransform().rotate(self.rotation_angle)
                        local_anchor = t.map(anchor_logic) + QPointF(self.width()/2, self.height()/2)
                        self._anchor_pos_parent = self.pos() + local_anchor.toPoint()
                    else:
                        self._anchor_pos_parent = None
                    return

            if self._get_rotation_handle_rect(draw_rect).contains(logic_mouse):
                self._rotating = True
                self._rotation_pivot_parent = self.pos() + self.rect().center()
                local_mouse = self.mapFromGlobal(event.globalPos())
                center = self.rect().center()
                self._rot_start_angle = math.degrees(math.atan2(local_mouse.y() - center.y(), local_mouse.x() - center.x())) - self.rotation_angle
                self.clicked.emit(self)
                return
            
            if draw_rect.contains(logic_mouse):
                self._dragging = True
                self._drag_start_pos = event.globalPos() - self.pos()
                self.clicked.emit(self)
                self.setFocus()
            else:
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
            self.update_widget_size(rotation_pivot=self._rotation_pivot_parent) 
            self.update()
            return

        if self._resize_handle is not None:
            idx = self._resize_handle
            
            if self.shape_type == "line":
                target_global = event.globalPos()
                
                p1_local = QPoint(int(self.line_p1.x()), int(self.line_p1.y()))
                p2_local = QPoint(int(self.line_p2.x()), int(self.line_p2.y()))
                
                if idx == 0:
                    g1 = target_global
                    g2 = self.mapToGlobal(p2_local)
                else:
                    g1 = self.mapToGlobal(p1_local)
                    g2 = target_global
                    
                parent_p1 = self.parentWidget().mapFromGlobal(g1)
                parent_p2 = self.parentWidget().mapFromGlobal(g2)
                
                left = min(parent_p1.x(), parent_p2.x()) - self.MARGIN
                top = min(parent_p1.y(), parent_p2.y()) - self.MARGIN
                w = abs(parent_p1.x() - parent_p2.x()) + self.MARGIN * 2
                h = abs(parent_p1.y() - parent_p2.y()) + self.MARGIN * 2
                
                self.setGeometry(int(left), int(top), int(w), int(h))
                
                mapped_1 = self.mapFromGlobal(g1)
                mapped_2 = self.mapFromGlobal(g2)
                self.line_p1 = QPointF(mapped_1.x(), mapped_1.y())
                self.line_p2 = QPointF(mapped_2.x(), mapped_2.y())
                
                self.update()
                return

            mouse_logic = self.map_mouse_to_logic(event.globalPos())
            w, h = self._start_rect.width(), self._start_rect.height()
            l, t, r, b = -w/2, -h/2, w/2, h/2
            
            tx, ty = mouse_logic.x(), mouse_logic.y()
            
            if idx == 0: l, t = tx, ty      
            elif idx == 1: r, t = tx, ty    
            elif idx == 2: l, b = tx, ty    
            elif idx == 3: r, b = tx, ty    
            elif idx == 4: t = ty                 
            elif idx == 5: b = ty                 
            elif idx == 6: l = tx                 
            elif idx == 7: r = tx                 
            
            new_w = abs(r - l)
            new_h = abs(b - t)
            if new_w < 20: new_w = 20
            if new_h < 20: new_h = 20
            self._logical_rect = QRectF(0, 0, new_w, new_h)

            opp_idx = self._get_opposite_handle_index(idx)
            new_anchor_logic = self._get_logical_point_from_handle_index(opp_idx)
            self.update_widget_size(self._anchor_pos_parent, new_anchor_logic)
            self.update()
            return

        if self.shape_type == "line":
            local_mouse = event.pos()
            hs = self.HANDLE_SIZE
            r1 = QRectF(self.line_p1.x() - hs, self.line_p1.y() - hs, hs*2, hs*2)
            r2 = QRectF(self.line_p2.x() - hs, self.line_p2.y() - hs, hs*2, hs*2)
            if r1.contains(local_mouse) or r2.contains(local_mouse):
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.SizeAllCursor)
            return

        logic_mouse = self.map_mouse_to_logic(event.globalPos())
        w, h = self._logical_rect.width(), self._logical_rect.height()
        draw_rect = QRectF(-w/2, -h/2, w, h).adjusted(-4,-4,4,4)
        
        if self._get_rotation_handle_rect(draw_rect).contains(logic_mouse):
            self.setCursor(Qt.PointingHandCursor)
            return
            
        handles = self._get_handle_info(draw_rect)
        for i, (htype, r) in enumerate(handles):
            if r.contains(logic_mouse):
                if htype == "corner":
                    if i in [0, 3]: self.setCursor(Qt.SizeFDiagCursor) 
                    else: self.setCursor(Qt.SizeBDiagCursor)          
                else:
                    if i in [4, 5]: self.setCursor(Qt.SizeVerCursor)   
                    else: self.setCursor(Qt.SizeHorCursor)             
                return

        if draw_rect.contains(logic_mouse):
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._rotating = False
        self._resize_handle = None
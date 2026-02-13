import math
from PyQt5.QtWidgets import QWidget
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
        # İSTEK 2: Renkli ve 3D Silindir
        color = painter.brush().color() # Mevcut fırça rengini al
        _draw_cylinder_path(painter, rect, color)
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

def _draw_cylinder_path(painter, rect, base_color):
    w = rect.width()
    h = rect.height()
    el_h = min(h * 0.25, w * 0.5) 
    
    # Renk Tonları
    if base_color.alpha() == 0: # Eğer dolgu kapalıysa
        base_color = QColor(200, 200, 200, 50) # Hayalet renk
        
    light_color = base_color.lighter(130)
    dark_color = base_color.darker(110)
    
    painter.save()
    painter.setPen(Qt.NoPen) 
    
    # 1. Gövde ve Alt (Gradyan)
    body_path = QPainterPath()
    body_path.moveTo(rect.left(), rect.top() + el_h/2)
    body_path.lineTo(rect.left(), rect.bottom() - el_h/2)
    # Alt yay
    body_path.arcTo(QRectF(rect.left(), rect.bottom() - el_h, w, el_h), 180, 180)
    body_path.lineTo(rect.right(), rect.top() + el_h/2)
    # Üst yay (arka kısmı kapatmak için)
    body_path.arcTo(QRectF(rect.left(), rect.top(), w, el_h), 0, -180)
    body_path.closeSubpath()
    
    # Gövde Gradyanı (Soldan sağa: Koyu -> Normal -> Koyu)
    grad = QLinearGradient(rect.left(), 0, rect.right(), 0)
    grad.setColorAt(0.0, dark_color)
    grad.setColorAt(0.2, base_color)
    grad.setColorAt(0.5, light_color)
    grad.setColorAt(0.8, base_color)
    grad.setColorAt(1.0, dark_color)
    
    painter.setBrush(QBrush(grad))
    painter.drawPath(body_path)
    
    # 2. Üst Kapak (Daha açık, ışık vuruyor)
    painter.setBrush(QBrush(light_color))
    painter.drawEllipse(QRectF(rect.left(), rect.top(), w, el_h))
    
    painter.restore()
    
    # 3. Kenar Çizgileri (Tekrar çizelim ki net olsun)
    # Eski kalemi geri yükle ama sadece dış hatlar
    old_pen = painter.pen()
    if old_pen.style() != Qt.NoPen:
        painter.drawEllipse(QRectF(rect.left(), rect.top(), w, el_h)) # Üst
        # Alt yay
        painter.drawArc(QRectF(rect.left(), rect.bottom() - el_h, w, el_h), 180 * 16, 180 * 16)
        # Yanlar
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
    MARGIN = 60 # Handle'lar için pay

    def __init__(self, parent, shape_type, color, width=160, height=160):
        super().__init__(parent)
        self.shape_type = shape_type
        self.primary_color = QColor(color)
        self.border_color = QColor(255, 255, 255, 200)
        self.stroke_width = 3
        
        self.opacity_val = 255 
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.ClickFocus)
        
        # Durum Değişkenleri
        self.rotation_angle = 0.0
        self.filled = True
        self.is_selected = False
        self.text = ""
        self.is_flipped = False
        
        # Etkileşim
        self._resize_handle = None    
        self._rotating = False
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._rot_start_angle = 0.0   

        # Mantıksal dikdörtgen (Döndürülmemiş hali)
        self._logical_rect = QRectF(0, 0, width, height)
        
        # İlk boyutu ayarla
        self.update_widget_size()
        self.show()

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
            
    # ------ İSTEK 1: Dinamik Boyutlandırma (Boşluğa düşmeyi engelleme) ------
    def update_widget_size(self):
        """
        Şekil döndürüldüğünde veya boyutlandırıldığında widget'ın fiziksel boyutunu,
        şeklin ekran üzerindeki bounding box'ını (kapsayıcı kutusunu) içine alacak 
        şekilde günceller. Görsel merkezi sabit tutar.
        """
        # Mevcut merkez (Global)
        old_center = self.mapToGlobal(self.rect().center())
        if not self.isVisible(): # İlk açılışta düzeltme
             # İlk konumlandırma dışarıdan yapıldığı için burada geometry'ye güvenemeyiz
             # Sadece resize yapalım
             pass

        # Mantıksal Rect'i merkeze al ve döndür
        t = QTransform().rotate(self.rotation_angle)
        # Bounding Box hesapla
        # Logical rect (0,0,w,h) -> Merkez (w/2, h/2)
        w, h = self._logical_rect.width(), self._logical_rect.height()
        centered_rect = QRectF(-w/2, -h/2, w, h)
        rotated_rect = t.mapRect(centered_rect)
        
        # Yeni genişlik/yükseklik (Margin payı ekle)
        new_w = rotated_rect.width() + self.MARGIN * 2
        new_h = rotated_rect.height() + self.MARGIN * 2
        
        # Widget'ı boyutlandır
        self.resize(int(new_w), int(new_h))
        
        # Widget'ı eski merkeze geri taşı (Böylece döndürürken kaymaz)
        # Yeni widget merkezi = (new_w/2, new_h/2) local
        # Globalde bu noktanın old_center olmasını istiyoruz.
        # TopLeft = GlobalCenter - (new_w/2, new_h/2)
        if self.isVisible():
            new_top_left = old_center - QPoint(int(new_w/2), int(new_h/2))
            self.move(new_top_left)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Widget'ın tam ortasına git
        center = self.rect().center()
        painter.translate(center)
        
        # Döndür
        painter.rotate(self.rotation_angle)
        
        # Çizimi merkeze göre yap (-w/2, -h/2)
        # Logical rect'in boyutu kadar
        w, h = self._logical_rect.width(), self._logical_rect.height()
        draw_rect = QRectF(-w/2, -h/2, w, h)

        final_color = QColor(self.primary_color)
        final_color.setAlpha(self.opacity_val)
        
        # Silindir kendi fırça mantığını yönetiyor
        if self.shape_type == "cylinder":
             painter.setBrush(final_color) # Rengi aktar
        elif self.filled and self.shape_type != "line":
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
        # Global fare pozisyonunu, şeklin merkezine göre ve açısı düzeltilmiş
        # yerel koordinat sistemine çevirir.
        local_pos = self.mapFromGlobal(global_pos)
        widget_center = self.rect().center()
        
        dx = local_pos.x() - widget_center.x()
        dy = local_pos.y() - widget_center.y()
        
        angle_rad = math.radians(-self.rotation_angle)
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        
        # Logical Rect merkezli koordinat (0,0 noktası logical rect'in sol üstü değil, merkezi değil.
        # Logical rect (-w/2, -h/2, w, h) olarak çiziliyor paint'te.
        # Bu yüzden rx, ry doğrudan merkeze göre offset.
        # Logical rect koordinat sisteminde (sol üst köşe bazlı) işlem yapmak için:
        # Logical Rect Center = (0,0) (bizim çizim sistemimizde)
        # Mouse logic de (0,0) merkezli geliyor.
        
        # Ancak _get_handle_info 'rect' alıyor. Bizim rect'imiz (-w/2, -h/2, w, h).
        # Bu rect'in merkezi (0,0).
        # O yüzden rx, ry direk kullanılabilir.
        return QPointF(rx, ry)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            logic_mouse = self.map_mouse_to_logic(event.globalPos())
            
            # Logical draw rect (-w/2, -h/2, w, h)
            w, h = self._logical_rect.width(), self._logical_rect.height()
            draw_rect = QRectF(-w/2, -h/2, w, h)
            
            handles = self._get_handle_info(draw_rect)
            for i, (htype, h_rect) in enumerate(handles):
                if h_rect.contains(logic_mouse):
                    self._resize_handle = i
                    self.clicked.emit(self)
                    self._drag_start_pos = event.globalPos()
                    # Başlangıç boyutunu sakla
                    self._start_rect = QRectF(self._logical_rect)
                    return

            if self._get_rotation_handle_rect(draw_rect).contains(logic_mouse):
                self._rotating = True
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
            self.update_widget_size() # Dönünce boyutu güncelle!
            self.update()
            return

        if self._resize_handle is not None:
            idx = self._resize_handle
            
            if self.shape_type == "line":
                # Line serbest yönetimi
                mouse_logic = self.map_mouse_to_logic(event.globalPos())
                
                # Mevcut uç noktaları belirle (Merkez (0,0) bazlı draw_rect'ten)
                w, h = self._logical_rect.width(), self._logical_rect.height()
                draw_rect = QRectF(-w/2, -h/2, w, h)
                
                if self.is_flipped:
                    p1 = draw_rect.topRight()    
                    p2 = draw_rect.bottomLeft()  
                else:
                    p1 = draw_rect.topLeft()     
                    p2 = draw_rect.bottomRight() 

                if idx == 0: p1 = mouse_logic
                elif idx == 1: p2 = mouse_logic
                
                # Yeni Rect
                new_rect_local = QRectF(p1, p2).normalized()
                
                # Merkez kayması var mı?
                # Line'ın merkezi değiştiği için widget'ın da kayması gerekebilir ama
                # şimdilik sadece boyutu güncelliyoruz. Line widget içinde yüzecek.
                
                self.is_flipped = (p1.x() < p2.x()) != (p1.y() < p2.y())
                self._logical_rect = QRectF(0, 0, new_rect_local.width(), new_rect_local.height())
                
                self.update_widget_size()
                self.update()

            else:
                # Standart Resize (Delta bazlı, Global fareden)
                delta = event.globalPos() - self._drag_start_pos
                
                # Bu delta widget koordinatlarında değil, global.
                # Ancak şekil dönük.
                # Basit çözüm: Farenin logical koordinatındaki değişimine bakmak daha doğru olurdu
                # ama kullanıcı deneyimi için global delta'yı logical eksenlere izdüşürmek gerek.
                # Hızlı çözüm: Mouse logic position kullanmak.
                
                mouse_logic = self.map_mouse_to_logic(event.globalPos())
                
                # Başlangıç Rect (Draw coord system: center 0,0)
                w, h = self._start_rect.width(), self._start_rect.height()
                l, t, r, b = -w/2, -h/2, w/2, h/2
                
                # Hangi kenar tutulduysa o kenarı mouse_logic'e çek
                target_x, target_y = mouse_logic.x(), mouse_logic.y()
                
                if idx == 0: l, t = target_x, target_y      # TL
                elif idx == 1: r, t = target_x, target_y    # TR
                elif idx == 2: l, b = target_x, target_y    # BL
                elif idx == 3: r, b = target_x, target_y    # BR
                elif idx == 4: t = target_y                 # Top
                elif idx == 5: b = target_y                 # Bottom
                elif idx == 6: l = target_x                 # Left
                elif idx == 7: r = target_x                 # Right
                
                new_w = abs(r - l)
                new_h = abs(b - t)
                
                # Minimum boyut
                if new_w < 20: new_w = 20
                if new_h < 20: new_h = 20
                
                self._logical_rect = QRectF(0, 0, new_w, new_h)
                self.update_widget_size()
                self.update()
            return

        # Cursor Değiştirme
        logic_mouse = self.map_mouse_to_logic(event.globalPos())
        w, h = self._logical_rect.width(), self._logical_rect.height()
        draw_rect = QRectF(-w/2, -h/2, w, h)
        
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
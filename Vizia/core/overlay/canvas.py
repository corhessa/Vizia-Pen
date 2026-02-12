from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRect

class CanvasLayer:
    """
    Her bir katmanın (Masaüstü veya Beyaz Tahta) çizim verilerini tutar.
    """
    def __init__(self, size):
        self.pixmap = QPixmap(size)
        self.pixmap.fill(Qt.transparent)
        self.history = [] 
        self.widgets = [] 

    def clear(self):
        self.pixmap.fill(Qt.transparent)
        # Widgetları kapat ve bellekten sil
        for item in self.history:
            if item.get('obj'):
                try: 
                    item['obj'].close()
                    item['obj'].deleteLater()
                except: pass
        self.history.clear()
        self.widgets.clear()
        self.redraw()

    def undo(self):
        if not self.history: return
        last_item = self.history.pop()
        
        # 5. Madde Çözümü: Geri alırken widget (şekil) ise yok et
        if last_item.get('type') in ['text', 'image', 'shape']:
            if last_item.get('obj'): 
                try: 
                    last_item['obj'].close()
                    last_item['obj'].deleteLater() # Bellekten de sil
                except: pass
            if last_item.get('obj') in self.widgets: 
                self.widgets.remove(last_item['obj'])
                
        self.redraw()

    def draw_segment(self, p1, p2, color, width, mode, is_whiteboard):
        """Fare hareket ederken pixmap üzerine anlık çizim yapar"""
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        if mode == "eraser":
            if is_whiteboard:
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                pen = QPen(Qt.white, width * 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            else:
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                pen = QPen(Qt.transparent, width * 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        painter.setPen(pen)
        painter.drawLine(p1, p2)
        painter.end()

    def add_stroke_to_history(self, path, color, width, mode, is_whiteboard):
        saved_color = color
        if mode == "eraser":
            saved_color = Qt.white if is_whiteboard else Qt.transparent
            
        self.history.append({
            'type': 'path', 
            'path': QPainterPath(path), 
            'color': saved_color, 
            'width': width * (3 if mode == 'eraser' else 1), 
            'mode': mode
        })

    def add_shape(self, shape_type, start, end, color, width):
        # Bu metod eski çizim şekilleri için (line, rect, ellipse - vektörel olmayan)
        self.history.append({
            'type': 'shape', 
            'shape': shape_type, 
            'start': start, 
            'end': end, 
            'color': color, 
            'width': width
        })
        self.redraw()

    def add_widget_item(self, widget, widget_type):
        self.widgets.append(widget)
        self.history.append({'type': widget_type, 'obj': widget})

    def remove_widget_item(self, widget):
        if widget in self.widgets: self.widgets.remove(widget)
        for i in range(len(self.history) - 1, -1, -1):
            if self.history[i].get('obj') == widget:
                self.history.pop(i)
                break

    def redraw(self):
        """History'den her şeyi baştan çizer"""
        self.pixmap.fill(Qt.transparent)
        p = QPainter(self.pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        
        for item in self.history:
            if item.get('type') == 'path':
                mode = item.get('mode')
                if mode == 'eraser' and item['color'] == Qt.transparent:
                     p.setCompositionMode(QPainter.CompositionMode_Clear)
                else:
                     p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                     
                p.setPen(QPen(item['color'], item['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.drawPath(item['path'])
                
            elif item.get('type') == 'shape':
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                p.setPen(QPen(item['color'], item['width']))
                rect = QRect(item['start'], item['end']).normalized()
                if item['shape'] == 'line': p.drawLine(item['start'], item['end'])
                elif item['shape'] == 'rect': p.drawRect(rect)
                elif item['shape'] == 'ellipse': p.drawEllipse(rect)
        p.end()
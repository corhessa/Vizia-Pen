"""
Timeline görsel widget'ı (QGraphicsScene tabanlı)
"""
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QWidget, 
                             QVBoxLayout, QHBoxLayout, QScrollBar)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from ..core.timeline import Timeline, Track, Clip
from ..utils.constants import COLORS, TRACK_HEIGHT, PIXELS_PER_SECOND, RULER_HEIGHT
from ..utils.signals import timeline_signals


class TimelineWidget(QWidget):
    """Timeline ana widget'ı"""
    
    clip_selected = pyqtSignal(str)  # Clip ID
    playhead_moved = pyqtSignal(float)  # Saniye
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timeline = Timeline()
        self.zoom_level = 1.0
        self.playhead_position = 0.0
        self.selected_clip_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        layout.addWidget(self.view)
        
        # Timeline'ı çiz
        self.redraw_timeline()
    
    def set_timeline(self, timeline: Timeline):
        """Timeline'ı ayarlar"""
        self.timeline = timeline
        self.redraw_timeline()
    
    def redraw_timeline(self):
        """Timeline'ı yeniden çizer"""
        self.scene.clear()
        
        # Ruler (zaman cetveli)
        self.draw_ruler()
        
        # Track'leri çiz
        y_offset = RULER_HEIGHT
        for track in self.timeline.tracks:
            self.draw_track(track, y_offset)
            y_offset += TRACK_HEIGHT
        
        # Playhead çiz
        self.draw_playhead()
        
        # Scene boyutunu ayarla
        duration = self.timeline.calculate_duration()
        width = duration * PIXELS_PER_SECOND * self.zoom_level
        height = y_offset
        self.scene.setSceneRect(0, 0, max(width, 1000), height)
    
    def draw_ruler(self):
        """Zaman cetvelini çizer"""
        duration = self.timeline.calculate_duration()
        width = max(duration * PIXELS_PER_SECOND * self.zoom_level, 1000)
        
        # Arka plan
        ruler_rect = self.scene.addRect(
            0, 0, width, RULER_HEIGHT,
            QPen(QColor(COLORS['border'])),
            QBrush(QColor(COLORS['panel']))
        )
        
        # Zaman işaretleri (her 5 saniye)
        for second in range(0, int(duration) + 1, 5):
            x = second * PIXELS_PER_SECOND * self.zoom_level
            line = self.scene.addLine(
                x, RULER_HEIGHT - 10, x, RULER_HEIGHT,
                QPen(QColor(COLORS['text_secondary']))
            )
            
            # Zaman metni
            text = self.scene.addText(f"{second}s")
            text.setDefaultTextColor(QColor(COLORS['text_secondary']))
            text.setPos(x + 2, 2)
    
    def draw_track(self, track: Track, y_offset: float):
        """Track'i çizer"""
        duration = self.timeline.calculate_duration()
        width = max(duration * PIXELS_PER_SECOND * self.zoom_level, 1000)
        
        # Track arka planı
        track_rect = self.scene.addRect(
            0, y_offset, width, TRACK_HEIGHT,
            QPen(QColor(COLORS['border'])),
            QBrush(QColor(COLORS['surface']))
        )
        
        # Track adı
        text = self.scene.addText(track.name)
        text.setDefaultTextColor(QColor(COLORS['text_primary']))
        text.setPos(5, y_offset + 5)
        
        # Klipleri çiz
        for clip in track.clips:
            self.draw_clip(clip, y_offset)
    
    def draw_clip(self, clip: Clip, y_offset: float):
        """Klip'i çizer"""
        x = clip.start_time * PIXELS_PER_SECOND * self.zoom_level
        width = clip.duration * PIXELS_PER_SECOND * self.zoom_level
        height = TRACK_HEIGHT - 10
        
        # Klip kutusu
        color = QColor(COLORS['blue_accent']) if clip.id == self.selected_clip_id else QColor(COLORS['purple_accent'])
        clip_rect = self.scene.addRect(
            x, y_offset + 5, width, height,
            QPen(QColor(COLORS['border'])),
            QBrush(color)
        )
        clip_rect.setToolTip(clip.name)
        
        # Klip adı
        text = self.scene.addText(clip.name)
        text.setDefaultTextColor(QColor(COLORS['text_primary']))
        text.setPos(x + 5, y_offset + 10)
    
    def draw_playhead(self):
        """Playhead'i çizer (mor çizgi)"""
        x = self.playhead_position * PIXELS_PER_SECOND * self.zoom_level
        height = len(self.timeline.tracks) * TRACK_HEIGHT + RULER_HEIGHT
        
        # Playhead çizgisi
        pen = QPen(QColor(COLORS['purple_accent']))
        pen.setWidth(2)
        line = self.scene.addLine(x, 0, x, height, pen)
        
        # Üst üçgen
        # TODO: Üçgen şekli ekle
    
    def set_playhead_position(self, position: float):
        """Playhead pozisyonunu ayarlar"""
        self.playhead_position = position
        self.redraw_timeline()
        self.playhead_moved.emit(position)
    
    def zoom_in(self):
        """Yakınlaştır"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.redraw_timeline()
    
    def zoom_out(self):
        """Uzaklaştır"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.2)
        self.redraw_timeline()
    
    def add_clip_to_track(self, track_index: int, clip: Clip):
        """Track'e klip ekler"""
        if 0 <= track_index < len(self.timeline.tracks):
            track = self.timeline.tracks[track_index]
            track.add_clip(clip)
            self.redraw_timeline()
            timeline_signals.clip_added.emit(clip)
    
    def mousePressEvent(self, event):
        """Mouse tıklama eventi"""
        # TODO: Klip seçimi, playhead taşıma vb.
        super().mousePressEvent(event)

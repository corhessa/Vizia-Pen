"""
Timeline veri modeli - tracks ve clips
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import uuid


@dataclass
class Clip:
    """Timeline'daki tek bir medya klibi"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filepath: str = ""
    start_time: float = 0.0  # Timeline'daki başlangıç zamanı (saniye)
    duration: float = 0.0  # Klip süresi (saniye)
    trim_start: float = 0.0  # Orijinal medyadan kesilen başlangıç (saniye)
    trim_end: float = 0.0  # Orijinal medyadan kesilen bitiş (saniye)
    media_duration: float = 0.0  # Orijinal medya süresi
    media_type: str = "video"  # video, audio, image, text
    name: str = ""
    
    # Görsel özellikler
    x: float = 0.0
    y: float = 0.0
    width: float = 1.0  # Scale faktörü (1.0 = orijinal)
    height: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Ses özellikleri
    volume: float = 1.0  # 0.0 - 2.0
    muted: bool = False
    
    # Efektler
    effects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metin özellikleri (text tipi için)
    text_content: str = ""
    text_font: str = "Arial"
    text_size: int = 48
    text_color: str = "#ffffff"
    text_position: str = "center"  # center, top, bottom, custom
    
    def __post_init__(self):
        """Başlatma sonrası işlemler"""
        if not self.name:
            import os
            self.name = os.path.basename(self.filepath) if self.filepath else "Yeni Klip"
        
        # Duration hesaplama
        if self.duration == 0.0 and self.media_duration > 0.0:
            self.duration = self.media_duration - self.trim_start - self.trim_end
    
    @property
    def end_time(self) -> float:
        """Klip bitiş zamanı"""
        return self.start_time + self.duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Clip'i dictionary'ye çevirir"""
        return {
            'id': self.id,
            'filepath': self.filepath,
            'start_time': self.start_time,
            'duration': self.duration,
            'trim_start': self.trim_start,
            'trim_end': self.trim_end,
            'media_duration': self.media_duration,
            'media_type': self.media_type,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'rotation': self.rotation,
            'opacity': self.opacity,
            'volume': self.volume,
            'muted': self.muted,
            'effects': self.effects,
            'text_content': self.text_content,
            'text_font': self.text_font,
            'text_size': self.text_size,
            'text_color': self.text_color,
            'text_position': self.text_position,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Clip':
        """Dictionary'den Clip oluşturur"""
        return cls(**data)


@dataclass
class Track:
    """Timeline track'i (video, audio, text, overlay)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    track_type: str = "video"  # video, audio, text, overlay
    clips: List[Clip] = field(default_factory=list)
    height: int = 60  # Pixel cinsinden track yüksekliği
    locked: bool = False
    visible: bool = True
    muted: bool = False  # Audio track'ler için
    
    def __post_init__(self):
        """Başlatma sonrası işlemler"""
        if not self.name:
            self.name = f"{self.track_type.capitalize()} Track"
    
    def add_clip(self, clip: Clip) -> None:
        """Track'e klip ekler"""
        self.clips.append(clip)
        self._sort_clips()
    
    def remove_clip(self, clip_id: str) -> bool:
        """Track'ten klip siler"""
        for i, clip in enumerate(self.clips):
            if clip.id == clip_id:
                self.clips.pop(i)
                return True
        return False
    
    def get_clip(self, clip_id: str) -> Optional[Clip]:
        """ID'ye göre klip döndürür"""
        for clip in self.clips:
            if clip.id == clip_id:
                return clip
        return None
    
    def _sort_clips(self) -> None:
        """Klipleri başlangıç zamanına göre sıralar"""
        self.clips.sort(key=lambda c: c.start_time)
    
    def get_clips_at_time(self, time: float) -> List[Clip]:
        """Belirtilen zamandaki tüm klipleri döndürür"""
        return [c for c in self.clips if c.start_time <= time < c.end_time]
    
    def to_dict(self) -> Dict[str, Any]:
        """Track'i dictionary'ye çevirir"""
        return {
            'id': self.id,
            'name': self.name,
            'track_type': self.track_type,
            'clips': [c.to_dict() for c in self.clips],
            'height': self.height,
            'locked': self.locked,
            'visible': self.visible,
            'muted': self.muted,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Track':
        """Dictionary'den Track oluşturur"""
        clips_data = data.pop('clips', [])
        track = cls(**data)
        track.clips = [Clip.from_dict(c) for c in clips_data]
        return track


class Timeline:
    """Ana timeline yöneticisi"""
    
    def __init__(self):
        self.tracks: List[Track] = []
        self.playhead_position: float = 0.0  # Saniye cinsinden
        self.zoom_level: float = 1.0  # Zoom faktörü
        self.duration: float = 0.0  # Toplam timeline süresi
        
        # Varsayılan track'leri ekle
        self.add_track(Track(name="Video 1", track_type="video"))
        self.add_track(Track(name="Audio 1", track_type="audio"))
    
    def add_track(self, track: Track) -> None:
        """Timeline'a track ekler"""
        self.tracks.append(track)
    
    def remove_track(self, track_id: str) -> bool:
        """Timeline'dan track siler"""
        for i, track in enumerate(self.tracks):
            if track.id == track_id:
                self.tracks.pop(i)
                return True
        return False
    
    def get_track(self, track_id: str) -> Optional[Track]:
        """ID'ye göre track döndürür"""
        for track in self.tracks:
            if track.id == track_id:
                return track
        return None
    
    def get_clip(self, clip_id: str) -> Optional[Clip]:
        """Tüm track'lerde klip arar"""
        for track in self.tracks:
            clip = track.get_clip(clip_id)
            if clip:
                return clip
        return None
    
    def calculate_duration(self) -> float:
        """Timeline'ın toplam süresini hesaplar"""
        max_time = 0.0
        for track in self.tracks:
            for clip in track.clips:
                max_time = max(max_time, clip.end_time)
        self.duration = max_time
        return max_time
    
    def get_all_clips_at_time(self, time: float) -> List[tuple[Track, Clip]]:
        """Belirtilen zamandaki tüm track'lerdeki klipleri döndürür"""
        result = []
        for track in self.tracks:
            clips = track.get_clips_at_time(time)
            for clip in clips:
                result.append((track, clip))
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Timeline'ı dictionary'ye çevirir"""
        return {
            'tracks': [t.to_dict() for t in self.tracks],
            'playhead_position': self.playhead_position,
            'zoom_level': self.zoom_level,
            'duration': self.duration,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timeline':
        """Dictionary'den Timeline oluşturur"""
        timeline = cls()
        timeline.tracks = []  # Varsayılan track'leri temizle
        
        for track_data in data.get('tracks', []):
            timeline.add_track(Track.from_dict(track_data))
        
        timeline.playhead_position = data.get('playhead_position', 0.0)
        timeline.zoom_level = data.get('zoom_level', 1.0)
        timeline.duration = data.get('duration', 0.0)
        
        return timeline

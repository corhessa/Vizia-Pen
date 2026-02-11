"""
Custom PyQt signals for inter-component communication
"""
try:
    from PyQt5.QtCore import QObject, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    # Fallback for when PyQt5 is not available
    PYQT_AVAILABLE = False
    QObject = object
    
    # Mock pyqtSignal
    class pyqtSignal:
        def __init__(self, *args):
            pass
        def emit(self, *args, **kwargs):
            pass
        def connect(self, *args, **kwargs):
            pass


class ProjectSignals(QObject):
    """Proje ile ilgili sinyaller"""
    project_loaded = pyqtSignal(dict)  # Proje yüklendiğinde
    project_saved = pyqtSignal(str)  # Proje kaydedildiğinde
    project_modified = pyqtSignal()  # Proje değiştirildiğinde
    project_closed = pyqtSignal()  # Proje kapatıldığında


class TimelineSignals(QObject):
    """Timeline ile ilgili sinyaller"""
    clip_added = pyqtSignal(object)  # Klip eklendiğinde
    clip_removed = pyqtSignal(str)  # Klip silindiğinde
    clip_modified = pyqtSignal(str)  # Klip değiştirildiğinde
    clip_selected = pyqtSignal(object)  # Klip seçildiğinde
    playhead_moved = pyqtSignal(float)  # Playhead hareket ettiğinde
    zoom_changed = pyqtSignal(float)  # Zoom değiştiğinde
    track_added = pyqtSignal(object)  # Track eklendiğinde
    track_removed = pyqtSignal(str)  # Track silindiğinde


class PlayerSignals(QObject):
    """Oynatıcı ile ilgili sinyaller"""
    play_started = pyqtSignal()
    play_paused = pyqtSignal()
    play_stopped = pyqtSignal()
    position_changed = pyqtSignal(float)  # Saniye cinsinden
    duration_changed = pyqtSignal(float)  # Saniye cinsinden
    volume_changed = pyqtSignal(int)  # 0-100 arası


class ExportSignals(QObject):
    """Export ile ilgili sinyaller"""
    export_started = pyqtSignal()
    export_progress = pyqtSignal(int)  # 0-100 arası
    export_completed = pyqtSignal(str)  # Dosya yolu
    export_failed = pyqtSignal(str)  # Hata mesajı
    export_cancelled = pyqtSignal()


# Global sinyal instance'ları
project_signals = ProjectSignals()
timeline_signals = TimelineSignals()
player_signals = PlayerSignals()
export_signals = ExportSignals()

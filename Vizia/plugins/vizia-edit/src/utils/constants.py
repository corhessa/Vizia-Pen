"""
Sabitler ve yapılandırma değerleri
"""
from typing import List, Tuple

# Desteklenen video formatları
SUPPORTED_VIDEO_FORMATS: List[str] = [
    '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'
]

# Desteklenen ses formatları
SUPPORTED_AUDIO_FORMATS: List[str] = [
    '.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.wma'
]

# Desteklenen görsel formatları
SUPPORTED_IMAGE_FORMATS: List[str] = [
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'
]

# Tüm desteklenen medya formatları
SUPPORTED_MEDIA_FORMATS = SUPPORTED_VIDEO_FORMATS + SUPPORTED_AUDIO_FORMATS + SUPPORTED_IMAGE_FORMATS

# Vizia Dark + Purple renk paleti
COLORS = {
    'background': '#0d0d0f',
    'panel': '#1c1c1e',
    'surface': '#2c2c2e',
    'border': '#3a3a3c',
    'blue_accent': '#007aff',
    'purple_accent': '#8b5cf6',
    'purple_light': '#a855f7',
    'purple_dark': '#7c3aed',
    'red': '#ff3b30',
    'green': '#4cd964',
    'text_primary': '#ffffff',
    'text_secondary': '#a1a1a6',
}

# Font
DEFAULT_FONT = 'Segoe UI'
DEFAULT_FONT_SIZE = 10

# Timeline ayarları
TIMELINE_HEIGHT = 300
TRACK_HEIGHT = 60
TRACK_MIN_HEIGHT = 40
TRACK_MAX_HEIGHT = 120
RULER_HEIGHT = 30
PIXELS_PER_SECOND = 50  # Varsayılan zoom seviyesi

# Thumbnail ayarları
THUMBNAIL_WIDTH = 80
THUMBNAIL_HEIGHT = 45
THUMBNAIL_INTERVAL = 1.0  # saniye

# Video export ayarları
EXPORT_PRESETS = {
    '720p': {'width': 1280, 'height': 720},
    '1080p': {'width': 1920, 'height': 1080},
    '1440p': {'width': 2560, 'height': 1440},
    '4K': {'width': 3840, 'height': 2160},
}

EXPORT_FPS = [24, 30, 60]
EXPORT_FORMATS = ['mp4', 'mov', 'webm']

# Kısayol tuşları
SHORTCUTS = {
    'play_pause': 'Space',
    'split': 'S',
    'delete': 'Delete',
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Shift+Z',
    'save': 'Ctrl+S',
    'export': 'Ctrl+E',
    'import': 'Ctrl+I',
    'zoom_in': '+',
    'zoom_out': '-',
    'rewind': 'J',
    'stop': 'K',
    'forward': 'L',
}

# Track tipleri
TRACK_TYPE_VIDEO = 'video'
TRACK_TYPE_AUDIO = 'audio'
TRACK_TYPE_TEXT = 'text'
TRACK_TYPE_OVERLAY = 'overlay'

# FFmpeg ayarları
FFMPEG_THREAD_COUNT = 4
FFMPEG_PRESET = 'medium'  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow

# Proje ayarları
PROJECT_EXTENSION = '.vzproj'
AUTOSAVE_INTERVAL = 300  # saniye (5 dakika)
MAX_RECENT_PROJECTS = 10

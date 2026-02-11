"""
Dosya işlemleri ve yardımcı fonksiyonlar
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, List
from .constants import SUPPORTED_MEDIA_FORMATS, SUPPORTED_VIDEO_FORMATS, SUPPORTED_AUDIO_FORMATS, SUPPORTED_IMAGE_FORMATS


def is_video_file(filepath: str) -> bool:
    """Video dosyası mı kontrol eder"""
    ext = Path(filepath).suffix.lower()
    return ext in SUPPORTED_VIDEO_FORMATS


def is_audio_file(filepath: str) -> bool:
    """Ses dosyası mı kontrol eder"""
    ext = Path(filepath).suffix.lower()
    return ext in SUPPORTED_AUDIO_FORMATS


def is_image_file(filepath: str) -> bool:
    """Görsel dosyası mı kontrol eder"""
    ext = Path(filepath).suffix.lower()
    return ext in SUPPORTED_IMAGE_FORMATS


def is_supported_media(filepath: str) -> bool:
    """Desteklenen medya formatı mı kontrol eder"""
    ext = Path(filepath).suffix.lower()
    return ext in SUPPORTED_MEDIA_FORMATS


def get_temp_dir() -> str:
    """
    Geçici dosyalar için dizin oluşturur ve yolunu döndürür
    """
    temp_dir = os.path.join(tempfile.gettempdir(), 'vizia_edit')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def get_cache_dir() -> str:
    """
    Önbellek (thumbnail vs.) için dizin oluşturur ve yolunu döndürür
    """
    cache_dir = os.path.join(get_temp_dir(), 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_thumbnail_cache_dir() -> str:
    """
    Thumbnail önbelleği için dizin oluşturur ve yolunu döndürür
    """
    thumb_dir = os.path.join(get_cache_dir(), 'thumbnails')
    os.makedirs(thumb_dir, exist_ok=True)
    return thumb_dir


def format_time(seconds: float) -> str:
    """
    Saniyeyi timecode formatına çevirir (HH:MM:SS.mmm)
    
    Args:
        seconds: Saniye cinsinden zaman
        
    Returns:
        Formatlanmış zaman string'i
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def parse_timecode(timecode: str) -> float:
    """
    Timecode string'ini saniyeye çevirir
    
    Args:
        timecode: HH:MM:SS.mmm formatında string
        
    Returns:
        Saniye cinsinden zaman
    """
    try:
        parts = timecode.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            secs_parts = parts[2].split('.')
            seconds = int(secs_parts[0])
            millis = int(secs_parts[1]) if len(secs_parts) > 1 else 0
            
            total = hours * 3600 + minutes * 60 + seconds + millis / 1000
            return total
    except:
        pass
    return 0.0


def sanitize_filename(filename: str) -> str:
    """
    Dosya adını temizler (geçersiz karakterleri kaldırır)
    
    Args:
        filename: Temizlenecek dosya adı
        
    Returns:
        Temizlenmiş dosya adı
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_size_mb(filepath: str) -> float:
    """
    Dosya boyutunu MB cinsinden döndürür
    
    Args:
        filepath: Dosya yolu
        
    Returns:
        Boyut (MB)
    """
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0


def ensure_dir(directory: str) -> None:
    """
    Dizinin var olduğundan emin olur, yoksa oluşturur
    
    Args:
        directory: Dizin yolu
    """
    os.makedirs(directory, exist_ok=True)

"""
Video thumbnail üretimi ve önbellek yönetimi
"""
import os
import hashlib
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor
from ..utils.ffmpeg_utils import extract_thumbnail
from ..utils.file_utils import get_thumbnail_cache_dir
from ..utils.constants import THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, THUMBNAIL_INTERVAL


class ThumbnailGenerator:
    """Video thumbnail üretici"""
    
    def __init__(self, max_workers: int = 4):
        self.cache_dir = get_thumbnail_cache_dir()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def get_cache_key(self, video_path: str, timestamp: float) -> str:
        """
        Video ve zaman için önbellek anahtarı üretir
        
        Args:
            video_path: Video dosyası yolu
            timestamp: Saniye cinsinden zaman
            
        Returns:
            Önbellek dosya adı
        """
        key_str = f"{video_path}_{timestamp}"
        hash_obj = hashlib.md5(key_str.encode())
        return f"{hash_obj.hexdigest()}.jpg"
    
    def get_cached_thumbnail(self, video_path: str, timestamp: float) -> Optional[str]:
        """
        Önbellekteki thumbnail'i döndürür (varsa)
        
        Args:
            video_path: Video dosyası yolu
            timestamp: Saniye cinsinden zaman
            
        Returns:
            Thumbnail dosya yolu veya None
        """
        cache_file = os.path.join(self.cache_dir, self.get_cache_key(video_path, timestamp))
        if os.path.exists(cache_file):
            return cache_file
        return None
    
    def generate_thumbnail(self, video_path: str, timestamp: float, 
                          force: bool = False) -> Optional[str]:
        """
        Video'dan thumbnail üretir
        
        Args:
            video_path: Video dosyası yolu
            timestamp: Saniye cinsinden zaman
            force: Önbelleği yoksay ve yeniden üret
            
        Returns:
            Thumbnail dosya yolu veya None
        """
        # Önbellekte var mı kontrol et
        if not force:
            cached = self.get_cached_thumbnail(video_path, timestamp)
            if cached:
                return cached
        
        # Üret
        cache_file = os.path.join(self.cache_dir, self.get_cache_key(video_path, timestamp))
        
        success = extract_thumbnail(
            video_path, 
            cache_file, 
            timestamp, 
            THUMBNAIL_WIDTH
        )
        
        if success and os.path.exists(cache_file):
            return cache_file
        
        return None
    
    def generate_thumbnails_async(self, video_path: str, 
                                 start_time: float, end_time: float,
                                 callback=None) -> None:
        """
        Belirtilen zaman aralığı için asenkron thumbnail üretir
        
        Args:
            video_path: Video dosyası yolu
            start_time: Başlangıç zamanı (saniye)
            end_time: Bitiş zamanı (saniye)
            callback: Her thumbnail üretildiğinde çağrılacak fonksiyon
        """
        timestamps = []
        current = start_time
        
        while current <= end_time:
            timestamps.append(current)
            current += THUMBNAIL_INTERVAL
        
        def generate_and_callback(ts):
            thumb_path = self.generate_thumbnail(video_path, ts)
            if callback and thumb_path:
                callback(ts, thumb_path)
            return thumb_path
        
        # Asenkron üret
        self.executor.map(generate_and_callback, timestamps)
    
    def generate_thumbnail_strip(self, video_path: str, 
                                start_time: float, end_time: float) -> List[str]:
        """
        Thumbnail şeridi üretir
        
        Args:
            video_path: Video dosyası yolu
            start_time: Başlangıç zamanı (saniye)
            end_time: Bitiş zamanı (saniye)
            
        Returns:
            Thumbnail dosya yolları listesi
        """
        thumbnails = []
        current = start_time
        
        while current <= end_time:
            thumb = self.generate_thumbnail(video_path, current)
            if thumb:
                thumbnails.append(thumb)
            current += THUMBNAIL_INTERVAL
        
        return thumbnails
    
    def clear_cache(self) -> None:
        """Tüm önbelleği temizler"""
        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        except Exception as e:
            print(f"Önbellek temizleme hatası: {e}")
    
    def get_cache_size(self) -> float:
        """
        Önbellek boyutunu MB cinsinden döndürür
        
        Returns:
            Boyut (MB)
        """
        total_size = 0
        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        except:
            pass
        
        return total_size / (1024 * 1024)
    
    def shutdown(self) -> None:
        """Thread pool'u kapatır"""
        self.executor.shutdown(wait=False)

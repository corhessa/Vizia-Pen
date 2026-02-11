"""
FFmpeg tabanlı video işleme engine
"""
import subprocess
import os
from typing import Optional, List, Dict, Any
from ..utils.ffmpeg_utils import (
    check_ffmpeg, probe_file, get_video_info, 
    build_filter_string, extract_thumbnail
)
from ..utils.file_utils import get_temp_dir


class VideoEngine:
    """Video işleme motoru (FFmpeg sarmalayıcı)"""
    
    def __init__(self):
        self.ffmpeg_available = check_ffmpeg()
    
    def check_available(self) -> bool:
        """FFmpeg'in kullanılabilir olup olmadığını kontrol eder"""
        return self.ffmpeg_available
    
    def get_video_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Video dosyası bilgilerini döndürür
        
        Args:
            filepath: Video dosyası yolu
            
        Returns:
            Video bilgileri veya None
        """
        return get_video_info(filepath)
    
    def cut_video(self, input_path: str, output_path: str, 
                  start_time: float, duration: float) -> bool:
        """
        Video'yu belirtilen sürede keser
        
        Args:
            input_path: Kaynak video
            output_path: Çıktı video
            start_time: Başlangıç zamanı (saniye)
            duration: Süre (saniye)
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available:
            return False
        
        try:
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', input_path,
                '-t', str(duration),
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Video kesme hatası: {e}")
            return False
    
    def concat_videos(self, input_paths: List[str], output_path: str) -> bool:
        """
        Birden fazla videoyu birleştirir
        
        Args:
            input_paths: Kaynak video listesi
            output_path: Çıktı video
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available or not input_paths:
            return False
        
        try:
            # Geçici concat dosyası oluştur
            concat_file = os.path.join(get_temp_dir(), 'concat_list.txt')
            with open(concat_file, 'w') as f:
                for path in input_paths:
                    f.write(f"file '{path}'\n")
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            
            # Geçici dosyayı temizle
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            return result.returncode == 0
        except Exception as e:
            print(f"Video birleştirme hatası: {e}")
            return False
    
    def apply_filters(self, input_path: str, output_path: str, 
                     filters: List[Dict[str, Any]]) -> bool:
        """
        Video'ya filtreler uygular
        
        Args:
            input_path: Kaynak video
            output_path: Çıktı video
            filters: Uygulanacak filtreler
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available or not filters:
            return False
        
        try:
            filter_string = build_filter_string(filters)
            if not filter_string:
                return False
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', filter_string,
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            return result.returncode == 0
        except Exception as e:
            print(f"Filtre uygulama hatası: {e}")
            return False
    
    def extract_frame(self, video_path: str, output_path: str, 
                     timestamp: float) -> bool:
        """
        Video'dan belirli bir zamanda frame çıkarır
        
        Args:
            video_path: Video dosyası
            output_path: Çıktı görsel
            timestamp: Saniye cinsinden zaman
            
        Returns:
            Başarılıysa True
        """
        return extract_thumbnail(video_path, output_path, timestamp)
    
    def create_video_from_image(self, image_path: str, output_path: str, 
                               duration: float) -> bool:
        """
        Statik görselden video oluşturur
        
        Args:
            image_path: Görsel dosyası
            output_path: Çıktı video
            duration: Video süresi (saniye)
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available:
            return False
        
        try:
            cmd = [
                'ffmpeg',
                '-loop', '1',
                '-i', image_path,
                '-t', str(duration),
                '-pix_fmt', 'yuv420p',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Görsel video dönüştürme hatası: {e}")
            return False

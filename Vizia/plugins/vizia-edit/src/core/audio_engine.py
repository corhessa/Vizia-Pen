"""
FFmpeg tabanlı ses işleme engine
"""
import subprocess
import os
import numpy as np
from typing import Optional, List
from ..utils.ffmpeg_utils import check_ffmpeg, get_audio_info
from ..utils.file_utils import get_temp_dir


class AudioEngine:
    """Ses işleme motoru (FFmpeg sarmalayıcı)"""
    
    def __init__(self):
        self.ffmpeg_available = check_ffmpeg()
    
    def check_available(self) -> bool:
        """FFmpeg'in kullanılabilir olup olmadığını kontrol eder"""
        return self.ffmpeg_available
    
    def get_audio_info(self, filepath: str) -> Optional[dict]:
        """
        Ses dosyası bilgilerini döndürür
        
        Args:
            filepath: Ses dosyası yolu
            
        Returns:
            Ses bilgileri veya None
        """
        return get_audio_info(filepath)
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """
        Video'dan sesi çıkarır
        
        Args:
            video_path: Video dosyası
            audio_path: Çıktı ses dosyası
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available:
            return False
        
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # Video yok
                '-acodec', 'copy',
                '-y',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Ses çıkarma hatası: {e}")
            return False
    
    def adjust_volume(self, input_path: str, output_path: str, 
                     volume: float) -> bool:
        """
        Ses seviyesini ayarlar
        
        Args:
            input_path: Kaynak ses
            output_path: Çıktı ses
            volume: Ses seviyesi (0.0 - 2.0, 1.0 = normal)
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available:
            return False
        
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-af', f'volume={volume}',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Ses seviyesi ayarlama hatası: {e}")
            return False
    
    def apply_fade(self, input_path: str, output_path: str, 
                  fade_in: float = 0, fade_out: float = 0,
                  duration: Optional[float] = None) -> bool:
        """
        Fade in/out efekti uygular
        
        Args:
            input_path: Kaynak ses
            output_path: Çıktı ses
            fade_in: Fade in süresi (saniye)
            fade_out: Fade out süresi (saniye)
            duration: Toplam ses süresi (fade_out hesabı için)
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available:
            return False
        
        try:
            filters = []
            
            if fade_in > 0:
                filters.append(f'afade=t=in:st=0:d={fade_in}')
            
            if fade_out > 0 and duration:
                start = duration - fade_out
                filters.append(f'afade=t=out:st={start}:d={fade_out}')
            
            if not filters:
                return False
            
            filter_str = ','.join(filters)
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-af', filter_str,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Fade efekti hatası: {e}")
            return False
    
    def get_waveform_data(self, audio_path: str, samples: int = 1000) -> Optional[np.ndarray]:
        """
        Ses dosyasından waveform verisi çıkarır (NumPy ile)
        
        Args:
            audio_path: Ses dosyası
            samples: Kaç örnek alınacağı
            
        Returns:
            Normalize edilmiş amplitüd değerleri (NumPy array)
        """
        if not self.ffmpeg_available:
            return None
        
        try:
            # FFmpeg ile ses verisini raw PCM olarak çıkar
            temp_pcm = os.path.join(get_temp_dir(), 'temp_audio.pcm')
            
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-f', 's16le',  # 16-bit PCM
                '-acodec', 'pcm_s16le',
                '-ac', '1',  # Mono
                '-ar', '8000',  # Düşük sample rate (performans için)
                '-y',
                temp_pcm
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode != 0:
                return None
            
            # PCM verisini oku
            audio_data = np.fromfile(temp_pcm, dtype=np.int16)
            
            # Temizle
            if os.path.exists(temp_pcm):
                os.remove(temp_pcm)
            
            # Downsample
            if len(audio_data) > samples:
                indices = np.linspace(0, len(audio_data) - 1, samples, dtype=int)
                audio_data = audio_data[indices]
            
            # Normalize (-1.0 to 1.0)
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            # Mutlak değerleri al (waveform görselleştirmesi için)
            audio_data = np.abs(audio_data)
            
            return audio_data
            
        except Exception as e:
            print(f"Waveform verisi çıkarma hatası: {e}")
            return None
    
    def mix_audio(self, input_paths: List[str], output_path: str) -> bool:
        """
        Birden fazla ses dosyasını karıştırır (mix)
        
        Args:
            input_paths: Kaynak ses dosyaları
            output_path: Çıktı ses
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available or len(input_paths) < 2:
            return False
        
        try:
            # FFmpeg amix filtresini kullan
            cmd = ['ffmpeg']
            
            for path in input_paths:
                cmd.extend(['-i', path])
            
            cmd.extend([
                '-filter_complex', f'amix=inputs={len(input_paths)}:duration=longest',
                '-y',
                output_path
            ])
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Ses karıştırma hatası: {e}")
            return False

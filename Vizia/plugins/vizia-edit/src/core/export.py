"""
Video export ve render pipeline (FFmpeg tabanlı)
"""
import subprocess
import os
import re
from typing import Optional, Dict, Any, Callable
from threading import Thread
from ..utils.ffmpeg_utils import check_ffmpeg, has_hardware_encoder
from ..utils.file_utils import get_temp_dir
from ..utils.signals import export_signals
from ..utils.constants import FFMPEG_PRESET, EXPORT_PRESETS
from .timeline import Timeline


class ExportSettings:
    """Export ayarları"""
    
    def __init__(self):
        self.output_path: str = ""
        self.format: str = "mp4"  # mp4, mov, webm
        self.resolution: tuple = (1920, 1080)
        self.fps: int = 30
        self.bitrate: Optional[int] = None  # None = otomatik
        self.codec: str = "h264"  # h264, h265
        self.hardware_encoding: bool = True
        self.preset: str = FFMPEG_PRESET
        self.audio_bitrate: int = 192  # kbps
    
    def to_dict(self) -> Dict[str, Any]:
        """Ayarları dictionary'ye çevirir"""
        return {
            'output_path': self.output_path,
            'format': self.format,
            'resolution': self.resolution,
            'fps': self.fps,
            'bitrate': self.bitrate,
            'codec': self.codec,
            'hardware_encoding': self.hardware_encoding,
            'preset': self.preset,
            'audio_bitrate': self.audio_bitrate,
        }


class ExportEngine:
    """Video export ve render motoru"""
    
    def __init__(self):
        self.ffmpeg_available = check_ffmpeg()
        self.is_exporting = False
        self.cancel_requested = False
        self.current_process: Optional[subprocess.Popen] = None
    
    def check_available(self) -> bool:
        """FFmpeg'in kullanılabilir olup olmadığını kontrol eder"""
        return self.ffmpeg_available
    
    def get_hardware_encoder(self, codec: str) -> Optional[str]:
        """
        Mevcut hardware encoder'ı döndürür
        
        Args:
            codec: h264 veya h265
            
        Returns:
            Encoder adı veya None (software fallback)
        """
        if codec == "h264":
            if has_hardware_encoder("h264_nvenc"):
                return "h264_nvenc"
            elif has_hardware_encoder("h264_qsv"):
                return "h264_qsv"
        elif codec == "h265":
            if has_hardware_encoder("hevc_nvenc"):
                return "hevc_nvenc"
            elif has_hardware_encoder("hevc_qsv"):
                return "hevc_qsv"
        
        return None
    
    def export_timeline(self, timeline: Timeline, settings: ExportSettings,
                       progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Timeline'ı export eder
        
        Args:
            timeline: Export edilecek timeline
            settings: Export ayarları
            progress_callback: İlerleme callback fonksiyonu (0-100)
            
        Returns:
            Başarılıysa True
        """
        if not self.ffmpeg_available or self.is_exporting:
            return False
        
        self.is_exporting = True
        self.cancel_requested = False
        export_signals.export_started.emit()
        
        # Thread'de export et
        thread = Thread(
            target=self._export_thread,
            args=(timeline, settings, progress_callback)
        )
        thread.start()
        
        return True
    
    def _export_thread(self, timeline: Timeline, settings: ExportSettings,
                      progress_callback: Optional[Callable[[int], None]]) -> None:
        """Export thread fonksiyonu"""
        try:
            success = self._do_export(timeline, settings, progress_callback)
            
            if self.cancel_requested:
                export_signals.export_cancelled.emit()
            elif success:
                export_signals.export_completed.emit(settings.output_path)
            else:
                export_signals.export_failed.emit("Export başarısız")
                
        except Exception as e:
            export_signals.export_failed.emit(str(e))
        finally:
            self.is_exporting = False
            self.current_process = None
    
    def _do_export(self, timeline: Timeline, settings: ExportSettings,
                  progress_callback: Optional[Callable[[int], None]]) -> bool:
        """Gerçek export işlemi"""
        
        # Basitleştirilmiş export: Tüm track'lerdeki videoları birleştir
        # Gerçek implementasyon tüm efektleri, geçişleri vb. işler
        
        try:
            # Encoder seç
            if settings.hardware_encoding:
                encoder = self.get_hardware_encoder(settings.codec)
                if not encoder:
                    encoder = "libx264" if settings.codec == "h264" else "libx265"
            else:
                encoder = "libx264" if settings.codec == "h264" else "libx265"
            
            # FFmpeg komutu oluştur
            # Bu basit bir örnek - gerçek implementasyon complex filtergraph kullanır
            
            # İlk video track'inden ilk klibi al (demo için)
            video_tracks = [t for t in timeline.tracks if t.track_type == 'video']
            if not video_tracks or not video_tracks[0].clips:
                return False
            
            first_clip = video_tracks[0].clips[0]
            
            cmd = [
                'ffmpeg',
                '-i', first_clip.filepath,
                '-c:v', encoder,
                '-preset', settings.preset,
                '-s', f'{settings.resolution[0]}x{settings.resolution[1]}',
                '-r', str(settings.fps),
                '-c:a', 'aac',
                '-b:a', f'{settings.audio_bitrate}k',
            ]
            
            if settings.bitrate:
                cmd.extend(['-b:v', f'{settings.bitrate}k'])
            
            cmd.extend(['-y', settings.output_path])
            
            # Progress tracking için
            duration = timeline.duration
            
            # FFmpeg'i çalıştır
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # İlerlemeyi takip et
            for line in self.current_process.stderr:
                if self.cancel_requested:
                    self.current_process.terminate()
                    return False
                
                # FFmpeg progress parsing
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match and duration > 0:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    seconds = float(time_match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    
                    progress = int((current_time / duration) * 100)
                    progress = min(100, max(0, progress))
                    
                    if progress_callback:
                        progress_callback(progress)
                    
                    export_signals.export_progress.emit(progress)
            
            self.current_process.wait()
            return self.current_process.returncode == 0
            
        except Exception as e:
            print(f"Export hatası: {e}")
            return False
    
    def cancel_export(self) -> None:
        """Devam eden export'u iptal eder"""
        self.cancel_requested = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
    
    def estimate_file_size(self, timeline: Timeline, settings: ExportSettings) -> float:
        """
        Tahmini dosya boyutunu hesaplar (MB)
        
        Args:
            timeline: Timeline
            settings: Export ayarları
            
        Returns:
            Tahmini boyut (MB)
        """
        duration = timeline.duration
        
        if settings.bitrate:
            video_bitrate = settings.bitrate
        else:
            # Otomatik bitrate tahmini
            pixels = settings.resolution[0] * settings.resolution[1]
            if pixels >= 3840 * 2160:  # 4K
                video_bitrate = 20000
            elif pixels >= 2560 * 1440:  # 1440p
                video_bitrate = 12000
            elif pixels >= 1920 * 1080:  # 1080p
                video_bitrate = 8000
            else:  # 720p ve altı
                video_bitrate = 5000
        
        total_bitrate = video_bitrate + settings.audio_bitrate
        size_mb = (total_bitrate * duration) / (8 * 1024)  # kbps * saniye / 8 / 1024
        
        return size_mb

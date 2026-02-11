"""
FFmpeg komut oluşturma ve yardımcı fonksiyonlar
"""
import subprocess
import json
import shutil
import os
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path


def check_ffmpeg() -> bool:
    """
    FFmpeg'in sistemde kurulu olup olmadığını kontrol eder
    
    Returns:
        FFmpeg kuruluysa True
    """
    return shutil.which('ffmpeg') is not None


def check_ffprobe() -> bool:
    """
    FFprobe'un sistemde kurulu olup olmadığını kontrol eder
    
    Returns:
        FFprobe kuruluysa True
    """
    return shutil.which('ffprobe') is not None


def probe_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    FFprobe ile medya dosyasının bilgilerini alır
    
    Args:
        filepath: Medya dosyası yolu
        
    Returns:
        Dosya bilgileri dict'i veya None
    """
    if not check_ffprobe():
        return None
    
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            filepath
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"FFprobe error: {e}")
    
    return None


def get_video_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Video dosyasından temel bilgileri çıkarır
    
    Args:
        filepath: Video dosyası yolu
        
    Returns:
        Video bilgileri (duration, width, height, fps, codec, bitrate)
    """
    probe_data = probe_file(filepath)
    if not probe_data:
        return None
    
    info = {}
    
    # Format bilgileri
    if 'format' in probe_data:
        fmt = probe_data['format']
        info['duration'] = float(fmt.get('duration', 0))
        info['bitrate'] = int(fmt.get('bit_rate', 0))
        info['size'] = int(fmt.get('size', 0))
    
    # Video stream bilgileri
    for stream in probe_data.get('streams', []):
        if stream.get('codec_type') == 'video':
            info['width'] = stream.get('width', 0)
            info['height'] = stream.get('height', 0)
            info['codec'] = stream.get('codec_name', 'unknown')
            
            # FPS hesaplama
            fps_str = stream.get('r_frame_rate', '0/1')
            try:
                num, den = map(int, fps_str.split('/'))
                info['fps'] = num / den if den > 0 else 0
            except:
                info['fps'] = 0
            
            break
    
    return info


def get_audio_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Ses dosyasından temel bilgileri çıkarır
    
    Args:
        filepath: Ses dosyası yolu
        
    Returns:
        Ses bilgileri (duration, sample_rate, channels, codec)
    """
    probe_data = probe_file(filepath)
    if not probe_data:
        return None
    
    info = {}
    
    # Format bilgileri
    if 'format' in probe_data:
        fmt = probe_data['format']
        info['duration'] = float(fmt.get('duration', 0))
    
    # Audio stream bilgileri
    for stream in probe_data.get('streams', []):
        if stream.get('codec_type') == 'audio':
            info['sample_rate'] = stream.get('sample_rate', 0)
            info['channels'] = stream.get('channels', 0)
            info['codec'] = stream.get('codec_name', 'unknown')
            info['bitrate'] = int(stream.get('bit_rate', 0))
            break
    
    return info


def extract_thumbnail(video_path: str, output_path: str, timestamp: float = 0.0, width: int = 160) -> bool:
    """
    Video'dan belirli bir zamanda thumbnail çıkarır
    
    Args:
        video_path: Video dosyası yolu
        output_path: Çıktı görsel yolu
        timestamp: Saniye cinsinden zaman
        width: Thumbnail genişliği (yükseklik otomatik hesaplanır)
        
    Returns:
        Başarılıysa True
    """
    if not check_ffmpeg():
        return False
    
    try:
        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-vf', f'scale={width}:-1',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"Thumbnail extraction error: {e}")
        return False


def extract_audio_waveform_data(audio_path: str, samples: int = 1000) -> Optional[List[float]]:
    """
    Ses dosyasından waveform verisi çıkarır
    
    Args:
        audio_path: Ses dosyası yolu
        samples: Kaç örnek alınacağı
        
    Returns:
        Normalize edilmiş amplitüd değerleri listesi
    """
    # Bu fonksiyon NumPy ile ses verisi işleyerek implement edilecek
    # Şimdilik basit bir placeholder
    return None


def build_filter_string(filters: List[Dict[str, Any]]) -> str:
    """
    FFmpeg filtergraph string'i oluşturur
    
    Args:
        filters: Filtre tanımları listesi
        
    Returns:
        FFmpeg filtergraph string'i
    """
    filter_parts = []
    
    for f in filters:
        filter_type = f.get('type')
        
        if filter_type == 'brightness':
            value = f.get('value', 0)  # -1.0 to 1.0
            filter_parts.append(f'eq=brightness={value}')
        
        elif filter_type == 'contrast':
            value = f.get('value', 1)  # 0 to 2
            filter_parts.append(f'eq=contrast={value}')
        
        elif filter_type == 'saturation':
            value = f.get('value', 1)  # 0 to 3
            filter_parts.append(f'eq=saturation={value}')
        
        elif filter_type == 'hue':
            value = f.get('value', 0)  # -180 to 180
            filter_parts.append(f'hue=h={value}')
        
        elif filter_type == 'blur':
            value = f.get('value', 5)  # 0 to 20
            filter_parts.append(f'boxblur={value}')
        
        elif filter_type == 'sharpen':
            filter_parts.append('unsharp=5:5:1.0:5:5:0.0')
        
        elif filter_type == 'grayscale':
            filter_parts.append('hue=s=0')
        
        elif filter_type == 'sepia':
            filter_parts.append('colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131')
        
        elif filter_type == 'vignette':
            angle = f.get('angle', 'PI/5')
            filter_parts.append(f'vignette=angle={angle}')
        
        elif filter_type == 'speed':
            value = f.get('value', 1.0)
            if value != 1.0:
                filter_parts.append(f'setpts={1/value}*PTS')
    
    return ','.join(filter_parts) if filter_parts else None


def has_hardware_encoder(encoder: str) -> bool:
    """
    Belirtilen hardware encoder'ın sistemde mevcut olup olmadığını kontrol eder
    
    Args:
        encoder: Encoder adı (h264_nvenc, hevc_nvenc, h264_qsv, vb.)
        
    Returns:
        Encoder mevcutsa True
    """
    if not check_ffmpeg():
        return False
    
    try:
        cmd = ['ffmpeg', '-hide_banner', '-encoders']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return encoder in result.stdout
    except:
        return False

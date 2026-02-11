"""
Video efektleri ve filtre tanımları
"""
from typing import List, Dict, Any, Optional
from ..utils.ffmpeg_utils import build_filter_string


# Önceden tanımlı filtre presetleri
FILTER_PRESETS = {
    'siyah_beyaz': [
        {'type': 'grayscale'}
    ],
    'sepia': [
        {'type': 'sepia'}
    ],
    'vintage': [
        {'type': 'saturation', 'value': 0.7},
        {'type': 'contrast', 'value': 1.2},
        {'type': 'vignette'}
    ],
    'sinematik': [
        {'type': 'saturation', 'value': 0.8},
        {'type': 'contrast', 'value': 1.1},
    ],
    'soguk': [
        {'type': 'hue', 'value': 20},
        {'type': 'saturation', 'value': 1.2}
    ],
    'sicak': [
        {'type': 'hue', 'value': -20},
        {'type': 'saturation', 'value': 1.2}
    ],
}


# Geçiş efektleri
TRANSITION_TYPES = [
    'fade',
    'dissolve',
    'wipe_left',
    'wipe_right',
    'wipe_up',
    'wipe_down',
    'slide_left',
    'slide_right',
    'zoom_in',
    'zoom_out',
]


class Effect:
    """Video/Audio efekti base class"""
    
    def __init__(self, effect_type: str, params: Dict[str, Any] = None):
        self.effect_type = effect_type
        self.params = params or {}
        self.enabled = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Efekti dictionary'ye çevirir"""
        return {
            'effect_type': self.effect_type,
            'params': self.params,
            'enabled': self.enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Effect':
        """Dictionary'den Effect oluşturur"""
        effect = cls(
            effect_type=data.get('effect_type', ''),
            params=data.get('params', {})
        )
        effect.enabled = data.get('enabled', True)
        return effect


class ColorEffect(Effect):
    """Renk düzeltme efekti"""
    
    def __init__(self, brightness: float = 0, contrast: float = 1.0, 
                 saturation: float = 1.0, hue: float = 0):
        params = {
            'brightness': brightness,  # -1.0 to 1.0
            'contrast': contrast,      # 0 to 2.0
            'saturation': saturation,  # 0 to 3.0
            'hue': hue,                # -180 to 180
        }
        super().__init__('color', params)
    
    def get_ffmpeg_filters(self) -> List[Dict[str, Any]]:
        """FFmpeg filtrelerini döndürür"""
        filters = []
        
        if self.params['brightness'] != 0:
            filters.append({'type': 'brightness', 'value': self.params['brightness']})
        
        if self.params['contrast'] != 1.0:
            filters.append({'type': 'contrast', 'value': self.params['contrast']})
        
        if self.params['saturation'] != 1.0:
            filters.append({'type': 'saturation', 'value': self.params['saturation']})
        
        if self.params['hue'] != 0:
            filters.append({'type': 'hue', 'value': self.params['hue']})
        
        return filters


class BlurEffect(Effect):
    """Blur efekti"""
    
    def __init__(self, intensity: float = 5.0):
        params = {'intensity': intensity}  # 0 to 20
        super().__init__('blur', params)
    
    def get_ffmpeg_filters(self) -> List[Dict[str, Any]]:
        return [{'type': 'blur', 'value': self.params['intensity']}]


class SpeedEffect(Effect):
    """Hız değiştirme efekti"""
    
    def __init__(self, speed: float = 1.0):
        params = {'speed': speed}  # 0.25 to 4.0
        super().__init__('speed', params)
    
    def get_ffmpeg_filters(self) -> List[Dict[str, Any]]:
        return [{'type': 'speed', 'value': self.params['speed']}]


class TransitionEffect(Effect):
    """İki klip arası geçiş efekti"""
    
    def __init__(self, transition_type: str = 'fade', duration: float = 1.0):
        params = {
            'transition_type': transition_type,
            'duration': duration,
        }
        super().__init__('transition', params)


def apply_preset_filter(preset_name: str) -> List[Dict[str, Any]]:
    """
    Önceden tanımlı filtre presetini uygular
    
    Args:
        preset_name: Preset adı
        
    Returns:
        Filtre listesi
    """
    return FILTER_PRESETS.get(preset_name, [])


def get_available_effects() -> Dict[str, List[str]]:
    """
    Mevcut tüm efektleri kategorize edilmiş şekilde döndürür
    
    Returns:
        Kategori -> Efekt listesi mapping
    """
    return {
        'Renk': ['Parlaklık', 'Kontrast', 'Doygunluk', 'Ton'],
        'Filtre': ['Siyah-Beyaz', 'Sepia', 'Vintage', 'Sinematik', 'Soğuk', 'Sıcak'],
        'Efekt': ['Blur', 'Sharpen', 'Vignette'],
        'Hız': ['Yavaş (0.5x)', 'Normal', 'Hızlı (2x)', 'Çok Hızlı (4x)', 'Ters Oynat'],
        'Geçiş': ['Fade', 'Dissolve', 'Wipe', 'Slide', 'Zoom'],
    }

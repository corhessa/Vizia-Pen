"""
Proje yönetimi - kaydetme, açma, otomatik kaydetme
"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .timeline import Timeline
from ..utils.constants import PROJECT_EXTENSION, MAX_RECENT_PROJECTS
from ..utils.signals import project_signals


class Project:
    """Video düzenleme projesi"""
    
    def __init__(self, name: str = "Yeni Proje"):
        self.name = name
        self.filepath: Optional[str] = None
        self.timeline = Timeline()
        self.created_at = datetime.now().isoformat()
        self.modified_at = datetime.now().isoformat()
        self.modified = False
        
        # Proje ayarları
        self.settings = {
            'resolution': {'width': 1920, 'height': 1080},
            'fps': 30,
            'sample_rate': 48000,
        }
    
    def save(self, filepath: Optional[str] = None) -> bool:
        """
        Projeyi dosyaya kaydeder
        
        Args:
            filepath: Kaydedilecek dosya yolu (None ise mevcut filepath kullanılır)
            
        Returns:
            Başarılıysa True
        """
        if filepath:
            self.filepath = filepath
        
        if not self.filepath:
            return False
        
        # Dosya uzantısını kontrol et
        if not self.filepath.endswith(PROJECT_EXTENSION):
            self.filepath += PROJECT_EXTENSION
        
        try:
            data = self.to_dict()
            
            # Dizini oluştur
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            
            # JSON olarak kaydet
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.modified = False
            self.modified_at = datetime.now().isoformat()
            
            # Son projeler listesine ekle
            self._add_to_recent_projects()
            
            project_signals.project_saved.emit(self.filepath)
            return True
            
        except Exception as e:
            print(f"Proje kaydetme hatası: {e}")
            return False
    
    @classmethod
    def load(cls, filepath: str) -> Optional['Project']:
        """
        Dosyadan proje yükler
        
        Args:
            filepath: Yüklenecek dosya yolu
            
        Returns:
            Project instance veya None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = cls.from_dict(data)
            project.filepath = filepath
            project.modified = False
            
            # Son projeler listesine ekle
            project._add_to_recent_projects()
            
            project_signals.project_loaded.emit(data)
            return project
            
        except Exception as e:
            print(f"Proje yükleme hatası: {e}")
            return None
    
    def mark_modified(self) -> None:
        """Projeyi değiştirilmiş olarak işaretler"""
        self.modified = True
        self.modified_at = datetime.now().isoformat()
        project_signals.project_modified.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Projeyi dictionary'ye çevirir"""
        return {
            'name': self.name,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'settings': self.settings,
            'timeline': self.timeline.to_dict(),
            'version': '1.0.0',
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Dictionary'den Project oluşturur"""
        project = cls(name=data.get('name', 'Yeni Proje'))
        project.created_at = data.get('created_at', datetime.now().isoformat())
        project.modified_at = data.get('modified_at', datetime.now().isoformat())
        project.settings = data.get('settings', project.settings)
        
        if 'timeline' in data:
            project.timeline = Timeline.from_dict(data['timeline'])
        
        return project
    
    def _add_to_recent_projects(self) -> None:
        """Son projeler listesine ekler"""
        if not self.filepath:
            return
        
        recent_file = self._get_recent_projects_file()
        
        try:
            # Mevcut listeyi yükle
            if os.path.exists(recent_file):
                with open(recent_file, 'r', encoding='utf-8') as f:
                    recent = json.load(f)
            else:
                recent = []
            
            # Yeni projeyi ekle (varsa önce çıkar)
            abs_path = os.path.abspath(self.filepath)
            if abs_path in recent:
                recent.remove(abs_path)
            recent.insert(0, abs_path)
            
            # Maksimum sayıda tut
            recent = recent[:MAX_RECENT_PROJECTS]
            
            # Kaydet
            os.makedirs(os.path.dirname(recent_file), exist_ok=True)
            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump(recent, f, indent=2)
                
        except Exception as e:
            print(f"Son projeler kaydedilemedi: {e}")
    
    @staticmethod
    def _get_recent_projects_file() -> str:
        """Son projeler dosyasının yolunu döndürür"""
        from ..utils.file_utils import get_temp_dir
        return os.path.join(get_temp_dir(), 'recent_projects.json')
    
    @staticmethod
    def get_recent_projects() -> list:
        """Son projelerin listesini döndürür"""
        recent_file = Project._get_recent_projects_file()
        
        try:
            if os.path.exists(recent_file):
                with open(recent_file, 'r', encoding='utf-8') as f:
                    recent = json.load(f)
                
                # Var olan dosyaları filtrele
                return [p for p in recent if os.path.exists(p)]
        except:
            pass
        
        return []

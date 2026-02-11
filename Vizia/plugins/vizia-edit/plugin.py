"""
Vizia-Pen Plugin Entegrasyonu
"""

import os
import sys


class ViziaPlugin:
    """Vizia-Pen eklenti tanımı"""
    
    name = "Vizia Edit"
    icon = "video-editing.png"
    
    def __init__(self):
        self.editor = None
    
    def run(self, overlay):
        """
        Plugin çalıştırıldığında
        Args:
            overlay: Vizia-Pen overlay instance
        """

        # plugin klasörünü path'e ekle
        plugin_root = os.path.dirname(os.path.abspath(__file__))
        if plugin_root not in sys.path:
            sys.path.insert(0, plugin_root)

        # artık src bulunabilir
        from src.app import ViziaEditApp
        
        self.editor = ViziaEditApp(overlay)
        self.editor.show()

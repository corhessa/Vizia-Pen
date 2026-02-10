# core/web_galacean/web_engine.py

import sys
import os
from PyQt5.QtCore import QUrl

class ViziaEngineAssets:
    """
    Vizia Studio için gerekli yerel HTML dosyasını bulur.
    """
    
    @staticmethod
    def get_engine_url():
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # [FIX 1] Klasör adı "web" (küçük harf) olmalı.
            # Proje yapısı: Vizia/core/web_galacean -> (2 up) -> Vizia -> Assets -> web
            project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
            html_path = os.path.join(project_root, "Assets", "web", "vizia_editor.html")
            
            if not os.path.exists(html_path):
                # Fallback: Belki büyük harflidir
                html_path = os.path.join(project_root, "Assets", "Web", "vizia_editor.html")

            print(f"Vizia Engine Yolu: {html_path}")

            if not os.path.exists(html_path):
                print(f"KRİTİK HATA: Dosya bulunamadı!")
                return QUrl("about:blank")

            return QUrl.fromLocalFile(html_path)

        except Exception as e:
            print(f"URL Oluşturma Hatası: {e}")
            return QUrl("about:blank")
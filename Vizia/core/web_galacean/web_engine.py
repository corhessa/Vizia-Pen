# core/web_galacean/web_engine.py

import sys
import os
from PyQt5.QtCore import QUrl

class ViziaEngineAssets:
    """
    Vizia Studio için gerekli yerel HTML dosyasını bulur ve 
    WebEngine'in anlayacağı bir URL formatına çevirir.
    """
    
    @staticmethod
    def get_engine_url():
        try:
            # 1. Şu anki dosyanın (web_engine.py) konumunu al
            # Örn: C:\Github\Vizia-Pen\Vizia\core\web_galacean
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 2. Proje ana dizinine çık (2 seviye yukarı: core -> Vizia)
            # Örn: C:\Github\Vizia-Pen\Vizia
            project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

            # 3. HTML dosyasının yolunu oluştur
            # HATA DÜZELTİLDİ: "Vizia" klasörü zaten project_root içinde olduğu için
            # tekrar "Vizia" eklememize gerek yok. Doğrudan "Assets"e gidiyoruz.
            html_path = os.path.join(project_root, "Assets", "Web", "vizia_editor.html")
            
            # Kontrol (Terminalde görmek için)
            print(f"Vizia Engine Yolu: {html_path}")

            if not os.path.exists(html_path):
                print(f"KRİTİK HATA: Dosya bulunamadı!")
                return QUrl("about:blank")

            return QUrl.fromLocalFile(html_path)

        except Exception as e:
            print(f"URL Oluşturma Hatası: {e}")
            return QUrl("about:blank")
import os
from .extractors import FileExtractor
from .exporters import FileExporter

# İki noktayı kaldırdık
from lens_core.translator import ViziaTranslator

# ... kodun geri kalanı aynı

class WorkflowOrchestrator:
    def __init__(self):
        self.extractor = FileExtractor()
        self.exporter = FileExporter()
        self.translator = ViziaTranslator()

    def process_file(self, file_path, target_lang="tr"):
        """Gelecekte burayı QThread içine alarak arka planda çalıştırabiliriz"""
        try:
            # 1. Oku
            text = self.extractor.extract(file_path)
            if not text.strip():
                print("Dosya boş veya okunamadı.")
                return

            # 2. Çevir
            translated_text = self.translator.translate(text, target=target_lang)

            # 3. Dışa Aktar (Orijinal dosyanın yanına _Ceviri olarak yazar)
            base, ext = os.path.splitext(file_path)
            export_path = f"{base}_Ceviri.txt" # Şimdilik düz metin kaydediyoruz
            
            self.exporter.export(translated_text, export_path)
            print(f"Workflow Tamamlandı: {export_path}")
            
        except Exception as e:
            print(f"Workflow Hatası: {e}")
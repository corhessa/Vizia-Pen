import time
import random
import os
from PyQt5.QtCore import QThread, pyqtSignal
from workflow.extractors import DocumentExtractor
from workflow.exporters import DocumentExporter

class ViziaWorkflowOrchestrator(QThread):
    progress = pyqtSignal(int, str)  # Yüzde, Durum Metni
    finished = pyqtSignal(bool, str) # Başarı durumu, Sonuç/Dosya Yolu

    def __init__(self, file_path, target_format, target_lang, include_images, translator):
        super().__init__()
        self.file_path = file_path
        self.target_format = target_format
        self.target_lang = target_lang
        self.include_images = include_images
        self.translator = translator

    def run(self):
        try:
            self.progress.emit(10, "Dosya ayrıştırılıyor...")
            elements = DocumentExtractor.extract(self.file_path, self.include_images)
            
            if not elements:
                self.finished.emit(False, "Dosya okunamadı veya içi boş.")
                return

            total_text_blocks = sum(1 for el in elements if el['type'] == 'text')
            processed_blocks = 0
            
            self.progress.emit(30, "Çeviri motoru başlatılıyor...")
            
            # Ban yememek ve sınırı aşmamak için çeviri döngüsü
            for el in elements:
                if el['type'] == 'text' and self.target_lang != "":
                    original_text = el['content']
                    
                    # 2000 karakterlik akıllı (Chunking) parçalama
                    chunks = [original_text[i:i+2000] for i in range(0, len(original_text), 2000)]
                    translated_chunks = []
                    
                    for chunk in chunks:
                        res = self.translator.translate(chunk, target=self.target_lang)
                        translated_chunks.append(res)
                        time.sleep(random.uniform(0.3, 0.8)) # İnsansı gecikme (Anti-ban)
                        
                    el['content'] = " ".join(translated_chunks)
                    processed_blocks += 1
                    
                    # İlerleme barını dinamik hesapla (30 ile 90 arası)
                    pct = 30 + int((processed_blocks / total_text_blocks) * 60)
                    self.progress.emit(pct, f"Çevriliyor... ({processed_blocks}/{total_text_blocks})")

            self.progress.emit(90, f"Yeni {self.target_format.upper()} dosyası oluşturuluyor...")
            
            # Çıktı dosya yolunu ayarla
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            out_dir = os.path.dirname(self.file_path)
            lang_suffix = f"_{self.target_lang}" if self.target_lang else "_islenmis"
            out_path = os.path.join(out_dir, f"{base_name}{lang_suffix}.{self.target_format.lower()}")

            success = DocumentExporter.export(elements, out_path)
            
            if success:
                self.progress.emit(100, "İşlem Tamamlandı!")
                self.finished.emit(True, out_path)
            else:
                self.finished.emit(False, "Dosya kaydedilirken hata oluştu.")

        except Exception as e:
            self.finished.emit(False, f"Kritik Hata: {str(e)}")
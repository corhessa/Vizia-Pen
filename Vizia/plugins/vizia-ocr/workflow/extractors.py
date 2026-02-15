import fitz  # PyMuPDF
import docx

class DocumentExtractor:
    @staticmethod
    def extract(file_path, include_images=False):
        """Dosyayı okur ve metin/görsel parçalarını (element listesi) döndürür."""
        ext = file_path.lower().split('.')[-1]
        elements = []

        try:
            if ext == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    elements.append({"type": "text", "content": f.read()})
            
            elif ext == 'docx':
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    if para.text.strip():
                        elements.append({"type": "text", "content": para.text})
            
            elif ext == 'pdf':
                doc = fitz.open(file_path)
                for page in doc:
                    text = page.get_text()
                    if text.strip():
                        # Kırık satırları birleştirip anlam bütünlüğünü (çeviri kalitesini) koruyoruz
                        clean_text = text.replace('-\n', '').replace('\n', ' ')
                        elements.append({"type": "text", "content": clean_text})
                    
                    if include_images:
                        for img in page.get_images():
                            base_image = doc.extract_image(img[0])
                            elements.append({"type": "image", "data": base_image["image"], "ext": base_image["ext"]})
        except Exception as e:
            print(f"Okuma/Çıkarma Hatası: {e}")
            
        return elements
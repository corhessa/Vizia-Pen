import fitz  # PyMuPDF

class FileExtractor:
    def extract(self, file_path):
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            return self._extract_pdf(file_path)
        elif ext == 'txt':
            return self._extract_txt(file_path)
        return ""

    def _extract_pdf(self, path):
        text = ""
        try:
            doc = fitz.open(path)
            for page in doc:
                text += page.get_text() + "\n"
        except Exception as e:
            print(f"PDF Okuma Hatası: {e}")
        return text

    def _extract_txt(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
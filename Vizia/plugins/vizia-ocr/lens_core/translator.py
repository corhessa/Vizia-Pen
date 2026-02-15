from deep_translator import GoogleTranslator

class ViziaTranslator:
    def __init__(self):
        self.client = GoogleTranslator()

    def translate(self, text, source='auto', target='tr'):
        if not text or len(text.strip()) == 0:
            return ""
        try:
            self.client.source = source
            self.client.target = target
            # Uzun metinlerde 5000 karakter sınırını korumak için
            if len(text) > 4900:
                text = text[:4900]
            return self.client.translate(text)
        except Exception as e:
            print(f"Çeviri Hatası: {e}")
            return "Çeviri yapılamadı (İnternet bağlantınızı kontrol edin)."
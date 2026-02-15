class FileExporter:
    def export(self, text, output_path):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"Dışa Aktarma Hatası: {e}")
            return False
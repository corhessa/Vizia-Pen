# 🚀 Vizia Edit - Hızlı Başlangıç Kılavuzu

## 📋 3 Adımda Kurulum

### 1️⃣ Otomatik Kurulum (En Kolay)

**Linux/macOS:**
```bash
./install.sh
```

**Windows:**
```
install.bat
```

### 2️⃣ Kontrol

```bash
python3 check_dependencies.py
```

### 3️⃣ Çalıştır

```bash
python3 run.py
```

---

## ❌ Sorun mu Yaşıyorsunuz?

### "Kütüphaneleri kuramıyorum" Sorunu

**Çözüm 1 - Minimal Kurulum:**
```bash
pip3 install -r requirements-minimal.txt
```

**Çözüm 2 - Platform-Özel:**
```bash
# Windows
pip3 install -r requirements-windows.txt

# macOS
pip3 install -r requirements-macos.txt

# Linux
pip3 install -r requirements.txt
```

**Çözüm 3 - Tek Tek Kurulum:**
```bash
pip3 install PyQt5>=5.15.0
pip3 install numpy>=1.21.0
pip3 install Pillow>=9.0.0
```

**Çözüm 4 - Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python run.py
```

**Çözüm 5 - Kullanıcı Dizinine Kur:**
```bash
pip3 install --user -r requirements.txt
```

---

## 🔍 Sık Sorulan Sorular

### Q: "pip: command not found" hatası
**A:** `python3 -m pip install -r requirements.txt` kullanın

### Q: "Permission denied" hatası
**A:** `pip3 install --user -r requirements.txt` kullanın

### Q: PyQt5 kurulamıyor
**A:** Sistem paketlerini kurun:
```bash
# Ubuntu/Debian
sudo apt install python3-pyqt5

# macOS
brew install qt5
```

### Q: "externally-managed-environment" hatası
**A:** Virtual environment kullanın (Çözüm 4'e bakın)

### Q: FFmpeg kurulu değil
**A:** 
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html adresinden indirin
```

### Q: python-mpv kurulamıyor
**A:** Bu opsiyoneldir! mpv olmadan da çalışır.
```bash
# Kurmak isterseniz:
# Ubuntu/Debian
sudo apt install mpv libmpv-dev
pip3 install python-mpv
```

---

## 📁 Dosya Yapısı

```
📂 vizia-edit/
├── 📄 README.md              # Genel bilgi
├── 📄 INSTALL.md             # Detaylı kurulum (SORUNLAR İÇİN BURAYA!)
├── 📄 TESTING.md             # Test kılavuzu
├── 📄 QUICKSTART.md          # Bu dosya
├── 📄 requirements.txt       # Ana bağımlılıklar
├── 📄 requirements-minimal.txt   # Minimal bağımlılıklar
├── 📄 requirements-windows.txt   # Windows için
├── 📄 requirements-macos.txt     # macOS için
├── 🔧 check_dependencies.py  # Bağımlılık kontrolü
├── 🔧 install.sh             # Linux/macOS kurulum
├── 🔧 install.bat            # Windows kurulum
└── 🚀 run.py                 # Uygulamayı başlat
```

---

## 💡 İpuçları

### Minimal Çalışma

Sadece core engine'i test etmek için (GUI olmadan):
```bash
pip3 install numpy
python3 -c "from src.core.timeline import Timeline; print('✓ Core çalışıyor')"
```

### Hata Ayıklama

Kurulum logunu kaydetmek için:
```bash
pip3 install -r requirements.txt 2>&1 | tee install_log.txt
```

### Sistem Bilgilerini Toplama

```bash
python3 --version
pip3 --version
uname -a  # Linux/macOS
```

---

## 🆘 Hâlâ Sorun mu Yaşıyorsunuz?

1. **Detaylı Kurulum Kılavuzunu Okuyun:**
   ```bash
   cat INSTALL.md
   # veya
   open INSTALL.md  # macOS
   start INSTALL.md # Windows
   ```

2. **Bağımlılık Kontrolü:**
   ```bash
   python3 check_dependencies.py
   ```

3. **GitHub Issues:**
   - https://github.com/corhessa/vizia-edit/issues
   - Hata mesajının tamamını paylaşın
   - İşletim sisteminizi belirtin
   - Python sürümünüzü belirtin

---

## ✅ Başarılı Kurulum Sonrası

```bash
# Standalone modda çalıştır
python3 run.py

# Veya plugin olarak kullan
# 1. vizia-edit klasörünü Vizia/plugins/ dizinine kopyalayın
# 2. Vizia-Pen'i başlatın
# 3. "Vizia Edit" butonuna tıklayın
```

---

## 📞 Destek

- 📖 Dokümantasyon: README.md, INSTALL.md, TESTING.md
- 🐛 Hata Bildirimi: GitHub Issues
- 💬 Soru Sor: GitHub Discussions

---

**🎬 Vizia Edit - Profesyonel video düzenleme artık daha kolay!**
